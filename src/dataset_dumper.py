import os
from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List, Set
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from contextlib import contextmanager

from packages.carla1s.utils.logging import get_logger
from packages.carla1s.actors import Sensor



class DatasetDumper(ABC):
    
    @dataclass
    class SensorBind:
        """绑定一个传感器至具体的任务"""
        sensor: Sensor
    
    def __init__(self, root_path: str, max_workers: int = 3):
        # PRIVATE
        self._root_path = root_path
        self._current_sequence_name: Optional[str] = None
        self._current_frame_count = 0
        self._binds: List[DatasetDumper.SensorTargetPair] = list()
        self._thread_pool = ThreadPoolExecutor(max_workers)
        self._promises: List[Future] = list()
        # PUBLIC
        self.logger = get_logger('dumper')
        # CHECK
        if not os.path.exists(self._root_path):
            raise FileNotFoundError(f"Root path not found: {self._root_path}")

    @property
    def root_path(self) -> str:
        return self._root_path
    
    @property
    def binds(self) -> List['DatasetDumper.SensorTargetPair']:
        return self._binds

    @property
    def current_frame_name(self) -> str:
        return str(self._current_frame_count)

    @property
    def current_sequence_path(self) -> str:
        return os.path.join(self._root_path, self._current_sequence_name)
    
    @property
    def thread_pool(self) -> ThreadPoolExecutor:
        return self._thread_pool
    
    @property
    def bind_sensors(self) -> Set[Sensor]:
        return set(bind.sensor for bind in self.binds)

    @abstractmethod
    @contextmanager
    def create_sequence(self, name: str = None):
        """创建一个新的序列.

        Args:
            name (str, optional): 自定义的序列名. 默认使用当前时间的格式化.
        """
        # 初始化序列在对象中的设置
        self._current_sequence_name = name if name is not None else datetime.now().strftime(f"%Y_%m_%d_%H_%M_%S")
        self._current_frame_count = 0
        self.logger.info(f"Creating sequence: {self._current_sequence_name}")

        # 创建序列目录
        self._setup_sequence_folder()

    @abstractmethod
    def create_frame(self):
        """创建一帧数据. """
        pass

    def _setup_sequence_folder(self):
        """创建序列目录.

        Args:
            path (str): 序列目录路径.
        """
        # 如果序列目录已经存在，并且包含内容，则抛出异常
        if os.path.exists(self.current_sequence_path):
            if os.listdir(self.current_sequence_path):
                raise FileExistsError(f"Sequence directory already exists and contains files: {self._current_sequence_name}")
            else:
                self.logger.warning(f"Sequence directory already exists but is empty: {self._current_sequence_name}")
        
        # 创建序列目录
        os.makedirs(self.current_sequence_path)
        self.logger.info(f"Created sequence folder: {self.current_sequence_path}")

    def join(self):
        """阻塞等待线程池中所有任务完成."""
        count_success = 0
        count_error = 0
        for promise in as_completed(self._promises):
            try:
                promise.result()
            except Exception as e:
                self.logger.error(f"Error in promise: {e}", exc_info=True)
                count_error += 1
            else:
                count_success += 1

        self.logger.info(f"Frame {self.current_frame_name} dump completed with {count_success} success, {count_error} error.")
        
        # 完成数据写入后，清除事件
        for bind in self.binds:
            bind.sensor.on_data_ready.clear()
