import os
import cv2
import numpy as np
import copy
from dataclasses import dataclass
from typing import Optional
from contextlib import contextmanager

from packages.carla1s.actors import Sensor
from packages.carla1s.tf import Point, CoordConverter, Transform, Coordinate

from ..dataset_dumper import DatasetDumper

class SemanticKittiDumper(DatasetDumper):
    
    MAPPING_SEG_KITTI_DEFAULT = 0 # unlabeled
    MAPPING_SEG_CARLA_TO_KITTI = {
        1: 40,   # road - road
        2: 48,   # sidewalk - sidewalk
        3: 50,   # building - building
        4: 52,   # wall - other-structure
        5: 51,   # fence - fence
        6: 80,   # pole - pole
        7: 99,   # traffic light - other-object
        8: 81,   # traffic sign - traffic-sign
        9: 70,   # vegetation - vegetation
        10: 72,  # terrain - terrain
        11: 0,   # sky - unlabeled
        12: 30,  # pedestrian - person
        13: 31,  # rider - bicyclist
        14: 10,  # car - car
        15: 18,  # truck - truck
        16: 13,  # bus - bus
        17: 16,  # train - on-rails
        18: 15,  # motorcycle - motorcycle
        19: 11,  # bicycle - bicycle
        20: 20,  # static - outlier
        21: 259, # dynamic - moving-other-vehicle
        22: 99,  # other - other-object
        23: 49,  # water - other-ground
        24: 60,  # road line - lane-marking
        25: 49,  # ground - other-ground
        26: 52,  # bridge - other-structure
        27: 49,  # rail - other-ground
        28: 51,  # guard rail - fence
        29: 60,  # lane-marking
        30: 44   # parking
    }
    
    @dataclass
    class SemanticLidarBind(DatasetDumper.SensorBind):
        """绑定语义激光雷达至输出点云和标签文件夹路径"""
        data_path: str
        labels_path: str
        
    @dataclass
    class TimestampBind(DatasetDumper.Bind):
        """绑定时间戳至文件路径"""
        data_path: str
    
    @dataclass
    class PoseBind(DatasetDumper.Bind):
        """绑定位姿至文件路径"""
        data_path: str
    
    @dataclass
    class CameraBind(DatasetDumper.SensorBind):
        """绑定图像至输出文件夹路径"""
        data_path: str
    
    @dataclass
    class CalibTrBind(DatasetDumper.Bind):
        """绑定标定数据至文件路径"""
        data_path: str
    
    def __init__(self, 
                 root_path: str, 
                 *,
                 max_workers: int = 3):
        super().__init__(root_path, max_workers)
        self._timestamp_offset: Optional[float] = None
        self._pose_offset: Optional[Transform] = None
        self._pose_offset_coordinate: Optional[Coordinate] = None
    
    @property
    def current_frame_name(self) -> str:
        """当前帧的名称, 格式为 6 位数字, 不足 6 位则补 0"""
        return f'{self._current_frame_count:06d}'

    @contextmanager
    def create_sequence(self, name: str = None):
        super().create_sequence(name)
        self._setup_content_folder()
        self.logger.info("=> SEQUENCE BEGINS ".ljust(80, '='))
        yield
        self.logger.info("=> SEQUENCE ENDS ".ljust(80, '='))

    def create_frame(self) -> 'SemanticKittiDumper':
        # 遍历所有的 bind, 创建 dump 任务
        self._current_frame_count += 1
        self._promises = []
        
        # 处理第一帧的特殊情况, 标记 offset 为 None，并创建 calib 文件  
        if self._current_frame_count == 1:
            self._timestamp_offset = None
            self._pose_offset = None
            self._setup_calib_file()

        for bind in self.binds:
            if isinstance(bind, self.SemanticLidarBind):
                self._promises.append(self.thread_pool.submit(self._dump_semantic_lidar, bind))
            elif isinstance(bind, self.CameraBind):
                self._promises.append(self.thread_pool.submit(self._dump_image, bind))
            elif isinstance(bind, self.TimestampBind):
                self._promises.append(self.thread_pool.submit(self._dump_timestamp, bind))
            elif isinstance(bind, self.PoseBind):
                self._promises.append(self.thread_pool.submit(self._dump_pose, bind))

        return self
    
    def bind_camera(self, 
                    sensor: Sensor, 
                    *,
                    data_folder: str) -> 'DatasetDumper':
        self._binds.append(self.CameraBind(sensor, data_folder))
        return self

    def bind_semantic_lidar(self, 
                            sensor: Sensor, 
                            *,
                            data_folder: str, 
                            labels_folder: str) -> 'DatasetDumper':
        self._binds.append(self.SemanticLidarBind(sensor, data_folder, labels_folder))
        return self

    def bind_timestamp(self, 
                       sensor: Sensor, 
                       *,
                       file_path: str) -> 'DatasetDumper':
        if os.path.splitext(file_path)[1] == '':
            raise ValueError(f"Path {file_path} is a folder, not a file.")
        self.binds.append(self.TimestampBind(sensor, file_path))
        
    def bind_pose(self, 
                  sensor: Sensor, 
                  *,
                  file_path: str) -> 'DatasetDumper':
        if os.path.splitext(file_path)[1] == '':
            raise ValueError(f"Path {file_path} is a folder, not a file.")
        self.binds.append(self.PoseBind(sensor, file_path))
        
    def bind_calib(self, 
                   *, 
                   tr_sensor: Sensor, 
                   file_path: str) -> 'DatasetDumper':
        if os.path.splitext(file_path)[1] == '':
            raise ValueError(f"Path {file_path} is a folder, not a file.")
        self.binds.append(self.CalibTrBind(tr_sensor, file_path))

    def _setup_content_folder(self):
        """创建内容文件夹."""
        for bind in self.binds:
            # 如果以扩展名结尾则创建文件，否则创建目录
            if os.path.splitext(bind.data_path)[1] == '':
                os.makedirs(os.path.join(self.current_sequence_path, bind.data_path))
                self.logger.info(f"Created folder at: {os.path.join(self.current_sequence_path, bind.data_path)}")
            else:
                with open(os.path.join(self.current_sequence_path, bind.data_path), 'w') as f:
                    f.write('')
                    self.logger.info(f"Created file at: {os.path.join(self.current_sequence_path, bind.data_path)}")
            # 处理特殊项
            if isinstance(bind, self.SemanticLidarBind):
                os.makedirs(os.path.join(self.current_sequence_path, bind.labels_path))
                self.logger.info(f"Created labels path: {os.path.join(self.current_sequence_path, bind.labels_path)}")

    def _setup_calib_file(self):
        """创建标定文件."""
        # 寻找 calib bind 和 pose bind
        calib_bind = next((bind for bind in self.binds if isinstance(bind, self.CalibTrBind)), None)
        pose_bind = next((bind for bind in self.binds if isinstance(bind, self.PoseBind)), None)
        
        if calib_bind is None or pose_bind is None:
            raise ValueError("Calib bind or pose bind not found")
        
        self._promises.append(self.thread_pool.submit(self._dump_calib, calib_bind, pose_bind))

    def _dump_image(self, bind: CameraBind):
        # 阻塞等待传感器更新
        bind.actor.on_data_ready.wait()
        # 储存数据
        file_name = f"{self.current_frame_name}.png"
        path = os.path.join(self.current_sequence_path, bind.data_path, file_name)
        cv2.imwrite(path, bind.actor.data.content)
        # 打印日志
        self.logger.debug(f"[frame={bind.actor.data.frame}] Dumped image to {path}")

    def _dump_semantic_lidar(self, bind: SemanticLidarBind):
        # 阻塞等待传感器更新
        bind.actor.on_data_ready.wait()
        
        # 准备储存路径
        file_name = f"{self.current_frame_name}"
        path_data = os.path.join(self.current_sequence_path, bind.data_path, file_name + '.bin')
        path_labels = os.path.join(self.current_sequence_path, bind.labels_path, file_name + '.label')
        
        # 处理点云
        points = [Point(x=x, y=-y, z=z) for x, y, z in bind.actor.data.content[:, :3]]
        points = CoordConverter.from_system(*points).get_list()
        points = np.array([[p.x, p.y, p.z, 1.0] for p in points], dtype=np.float32)
                
        # 处理标注
        seg = bind.actor.data.content[:, 3]
        seg = np.array([self.MAPPING_SEG_CARLA_TO_KITTI.get(i, self.MAPPING_SEG_KITTI_DEFAULT) for i in seg], dtype=np.uint16)

        oid = bind.actor.data.content[:, 4]
        labels = np.column_stack((seg.astype(np.uint16), oid.astype(np.uint16)))
        
        # 储存数据
        points.tofile(path_data)
        labels.tofile(path_labels)
        
        # 打印日志
        self.logger.debug(f"[frame={bind.actor.data.frame}] Dumped pointcloud(shape={points.shape}) to {path_data}")
        self.logger.debug(f"[frame={bind.actor.data.frame}] Dumped labels(shape={labels.shape}) to {path_labels}")

    def _dump_timestamp(self, bind: DatasetDumper.SensorBind):
        """导出时间戳, 以秒为单位, 使用科学计数法, 保留小数点后 6 位.

        Args:
            bind (DatasetDumper.SensorBind): 参考的传感器绑定
        """
        bind.actor.on_data_ready.wait()
        if self._timestamp_offset is None:
            self._timestamp_offset = bind.actor.data.timestamp
        timestamp = bind.actor.data.timestamp - self._timestamp_offset
        with open(os.path.join(self.current_sequence_path, bind.data_path), 'a') as f:
            f.write(f"{timestamp:.6e}\n")
            
        self.logger.debug(f"[frame={bind.actor.data.frame}] Dumped timestamp to {os.path.join(self.current_sequence_path, bind.data_path)}, value: {timestamp:.6e}")

    def _dump_pose(self, bind: PoseBind):
        """导出位姿数据, 是 3x4 的变换矩阵, 表示当前帧参考传感器到初始帧参考传感器的位姿变换.

        Args:
            bind (PoseBind): 参考的传感器绑定
        """
        bind.actor.on_data_ready.wait()
        
        # 准备储存路径
        path = os.path.join(self.current_sequence_path, bind.data_path)
        
        # 获取位姿数据并转换为
        pose = bind.actor.data.transform
        
        # 如果 offset 未设置, 则设置为当前帧的位姿
        if self._pose_offset is None:
            self._pose_offset = copy.deepcopy(pose)
            self._pose_offset_coordinate = Coordinate(self._pose_offset).change_orientation(CoordConverter.CARLA_CAM_TO_KITTI_CAM_ORIENTATION)

        # # 计算当前帧的位姿相对初始帧的位姿

        cami_on_cam0_kittiori_kitticoord = (Coordinate(pose)
                                            .change_orientation(CoordConverter.CARLA_CAM_TO_KITTI_CAM_ORIENTATION)
                                            .apply_transform(Transform(matrix=self._pose_offset_coordinate.data.matrix)))
        
        # 将位姿矩阵转换为 3x4 的变换矩阵
        pose_matrix = cami_on_cam0_kittiori_kitticoord.data.matrix[:3, :]

        # 横向展开, 表示为 1x12 的行向量, 并处理为小数点后 6 位的科学计数法表示, 以空格分隔
        pose_matrix = pose_matrix.flatten()
        pose_matrix = [f"{value:.6e}" for value in pose_matrix]
        pose_matrix = ' '.join(pose_matrix)

        # 保存到文件
        with open(path, 'a') as f:
            f.write(f"{pose_matrix}\n")
        self.logger.debug(f"[frame={bind.actor.data.frame}] Dumped pose to {path}")

    def _dump_calib(self, bind_calib: CalibTrBind, bind_pose: PoseBind):
        # 阻塞等待传感器更新
        bind_calib.actor.on_data_ready.wait()
        bind_pose.actor.on_data_ready.wait()
        
        # 准备对象
        target = bind_calib.actor
        cam_0 = bind_pose.actor
        other_cams = set(bind.actor for bind in self.binds if isinstance(bind, self.CameraBind) and bind.actor != cam_0)
        # 确保cam_0在第一位
        cams = [cam_0] + list(other_cams)
        
        # 准备储存路径
        path = os.path.join(self.current_sequence_path, bind_calib.data_path)
        
        def compute_intrinsic_matrix(w, h, fov):
            focal = w / (2.0 * np.tan(fov * np.pi / 360.0))
            K = np.identity(3)
            K[0, 0] = K[1, 1] = focal
            K[0, 2] = w / 2.0
            K[1, 2] = h / 2.0
            K[2, 2] = 1
            return K
        
        def compute_projection_matrix(K, R, t):
            # extern matrix
            RT = np.hstack((R, t))
            P = np.dot(K, RT)
            return P

        # 处理相机
        cam0_on_cam0_kittiori_carlacoord = (Coordinate(cam_0.data.transform)
                                            .change_orientation(CoordConverter.CARLA_CAM_TO_KITTI_CAM_ORIENTATION))
        for idx, cam in enumerate(cams):
            # 获取内参
            image_width = int(cam.attributes['image_size_x'])
            image_height = int(cam.attributes['image_size_y'])
            fov = float(cam.attributes['fov'])
            
            
            K = compute_intrinsic_matrix(image_width, image_height, fov)
            
            # 获取外参
            cam_on_cam0_kittiori_kitticoord = (Coordinate(cam.data.transform)
                                               .change_orientation(CoordConverter.CARLA_CAM_TO_KITTI_CAM_ORIENTATION)
                                               .apply_transform(Transform(matrix=cam0_on_cam0_kittiori_carlacoord.data.matrix)))

            R = cam_on_cam0_kittiori_kitticoord.data.matrix[:3, :3]
            t = cam_on_cam0_kittiori_kitticoord.data.matrix[:3, -1].reshape(3, 1)
            P = compute_projection_matrix(K, R, t)
            
            # 保存到文件
            with open(path, 'a') as calibfile:
                calibfile.write(f"P{idx}:")
                string = ' '.join(['{:.12e}'.format(value) for row in P for value in row])
                calibfile.write(string + "\n")
                self.logger.debug(f"[frame={cam.data.frame}] Dumped calib P{idx} to {path}")
        
        # 处理雷达到相机的变换
        lidar_on_cam0_kittiori_kitticoord = (Coordinate(target.data.transform)
                                             .change_orientation(CoordConverter.LEFT_HANDED_TO_RIGHT_HANDED_ORIENTATION)
                                             .apply_transform(Transform(matrix=cam0_on_cam0_kittiori_carlacoord.data.matrix)))
        Tr = lidar_on_cam0_kittiori_kitticoord.data.matrix

        with open(path, 'a') as calibfile:
            calibfile.write("Tr:")
            string = ' '.join(['{:.12e}'.format(value) for row in Tr[:3, :] for value in row])
            calibfile.write(string + "\n")
            self.logger.debug(f"[frame={bind_calib.actor.data.frame}] Dumped calib Tr to {path}")
