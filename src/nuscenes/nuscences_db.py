import os
import sqlite3
import uuid
import datetime
import json
import time
from typing import Tuple, List


class NuScenesDB:

    def __init__(self, db_path):
        self._db_path = db_path
        self._conn, self._cursor = self._create_database()
        # 初始化表
        self._create_tables()
        
    def get_nuscenes_token(self) -> str:
        return str(uuid.uuid4().hex)
    
    def get_nuscenes_timestamp(self, timestamp: float) -> int:
        return int(timestamp * 1_000_000)   

    def _decode_json_list(self, json_str: str) -> List[float]:
        return json.loads(json_str)
    
    def _create_database(self) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
        # 如果文件已经存在则抛出异常
        if os.path.exists(self._db_path):
            # TODO: 删除文件是临时解决方案
            os.remove(self._db_path)
            # raise FileExistsError(f"File {self._db_path} already exists")
        
        # 创建数据库
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        cursor = conn.cursor()

        return conn, cursor
        
    def _create_tables(self):
        self._create_table_log()
        self._create_table_map()
        self._create_table_pair_log_map()
        self._create_table_scene()
        self._create_table_sample()
        self._create_table_sample_data()
        self._create_table_ego_pose()
        self._create_table_calibrated_sensor()
        self._create_table_sensor()
        self._create_table_visibility()
        self._create_table_attribute()
        self._create_table_category()
        self._create_table_instance()
        self._create_table_sample_annotation()
        self._create_table_lidarseg()
    
    def _create_table_log(self):
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS log (
                token TEXT PRIMARY KEY,
                logfile TEXT NOT NULL,
                vehicle TEXT NOT NULL,
                date_captured TEXT NOT NULL,
                location TEXT NOT NULL
            )
        ''')
        
    def _create_table_map(self):
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS map (
                token TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                filename TEXT NOT NULL
            )
        ''')
        
    def _create_table_pair_log_map(self):
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS pair_log_map (
                log_token TEXT NOT NULL,
                map_token TEXT NOT NULL,
                FOREIGN KEY (log_token) REFERENCES log (token),
                FOREIGN KEY (map_token) REFERENCES map (token)
            )
        ''')
        
    def _create_table_scene(self):
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS scene (
                token TEXT PRIMARY KEY,
                log_token TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY (log_token) REFERENCES log (token)
            )
        ''')

    def _create_table_sample(self):
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS sample (
                token TEXT PRIMARY KEY,
                scene_token TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                prev TEXT,
                next TEXT,
                FOREIGN KEY (scene_token) REFERENCES scene (token),
                FOREIGN KEY (prev) REFERENCES sample (token),
                FOREIGN KEY (next) REFERENCES sample (token)
            )
        ''')
        
    def _create_table_sample_data(self):
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS sample_data (
                token TEXT PRIMARY KEY,
                sample_token TEXT NOT NULL,
                ego_pose_token TEXT NOT NULL,
                calibrated_sensor_token TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                fileformat TEXT NOT NULL,
                is_key_frame BOOLEAN NOT NULL,
                height INTEGER DEFAULT 0,
                width INTEGER DEFAULT 0,
                filename TEXT NOT NULL,
                prev TEXT,
                next TEXT,
                FOREIGN KEY (sample_token) REFERENCES sample (token),
                FOREIGN KEY (prev) REFERENCES sample_data (token),
                FOREIGN KEY (next) REFERENCES sample_data (token),
                FOREIGN KEY (ego_pose_token) REFERENCES ego_pose (token),
                FOREIGN KEY (calibrated_sensor_token) REFERENCES calibrated_sensor (token)
            )
        ''')
        
    def _create_table_ego_pose(self):
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS ego_pose (
                token TEXT PRIMARY KEY,
                timestamp INTEGER NOT NULL,
                translation TEXT NOT NULL,  -- Store as JSON string
                rotation TEXT NOT NULL      -- Store as JSON string
            )
        ''')
        
    def _create_table_calibrated_sensor(self):
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS calibrated_sensor (
                token TEXT PRIMARY KEY,
                sensor_token TEXT NOT NULL,
                translation TEXT NOT NULL,      -- Store as JSON string
                rotation TEXT NOT NULL,         -- Store as JSON string
                camera_intrinsic TEXT NOT NULL, -- Store as JSON string
                FOREIGN KEY (sensor_token) REFERENCES sensor (token)
            )
        ''')
        
    def _create_table_sensor(self):
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor (
                token TEXT PRIMARY KEY,
                channel TEXT NOT NULL,
                modality TEXT NOT NULL
            )
        ''')

    def _create_table_visibility(self):
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS visibility (
                token TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                level TEXT NOT NULL
            )
        ''')
        
    def _create_table_attribute(self):
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS attribute (
                token TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                name TEXT NOT NULL
            )
        ''')

    def _create_table_category(self):
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS category (
                token TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                seg_index INTEGER NOT NULL
            )
        ''')

    def _create_table_instance(self):
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS instance (
                token TEXT PRIMARY KEY,
                category_token TEXT NOT NULL,
                first_annotation_token TEXT,
                last_annotation_token TEXT,
                FOREIGN KEY (category_token) REFERENCES category (token)
            )
        ''')
        
    def _create_table_sample_annotation(self):
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS sample_annotation (
                token TEXT PRIMARY KEY,
                sample_token TEXT NOT NULL,
                visibility_token TEXT NOT NULL,
                attribute_tokens TEXT NOT NULL,  -- Store as JSON string
                instance_token TEXT NOT NULL,
                translation TEXT NOT NULL,      -- Store as JSON string
                size TEXT NOT NULL,             -- Store as JSON string
                rotation TEXT NOT NULL,         -- Store as JSON string
                num_lidar_pts INTEGER NOT NULL,
                num_radar_pts INTEGER NOT NULL,
                next TEXT,
                prev TEXT,
                FOREIGN KEY (sample_token) REFERENCES sample (token),
                FOREIGN KEY (visibility_token) REFERENCES visibility (token),
                FOREIGN KEY (instance_token) REFERENCES instance (token),
                FOREIGN KEY (prev) REFERENCES sample_annotation (token),
                FOREIGN KEY (next) REFERENCES sample_annotation (token)
            )
        ''')
        
    def _create_table_lidarseg(self):
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS lidarseg (
                token TEXT PRIMARY KEY,
                sample_data_token TEXT NOT NULL,
                filename TEXT NOT NULL
            )
        ''')

    def add_log(self, *,
                dtime: datetime.datetime = datetime.datetime.now(),
                vehicle: str = 'UNKNOW', 
                location: str = 'UNKNOW',
                map_token: str) -> str:
        """增加一条 log 记录

        Args:
            map_token (str): 指向的 map 记录的 token
            dtime (datetime.datetime, optional): 数据采集的时间. 默认使用当前时间.
            vehicle (str, optional): 采集数据时所用到的车辆描述, 如: 'n18'. 默认为 'UNKNOW'.
            location (str, optional): 数据采集的地点描述. 如: 'singapore-onenorth'. 默认为 'UNKNOW'.

        Returns:
            str: _description_
        """
        token = self.get_nuscenes_token()
        log_file = f"{vehicle}-{dtime.strftime('%Y-%m-%d-%H-%M-%S%z')}"
        date_captured = dtime.strftime("%Y-%m-%d")
        
        # 记录 log 数据
        self._cursor.execute('''
            INSERT INTO log (token, logfile, vehicle, date_captured, location) VALUES (?, ?, ?, ?, ?)
        ''', (token, log_file, vehicle, date_captured, location))
        
        # 记录 log 和 map 的关系
        self._cursor.execute('''
            INSERT INTO pair_log_map (log_token, map_token) VALUES (?, ?)
        ''', (token, map_token))

        self._conn.commit()
        return token

    def add_map(self, *,
                category: str = 'UNKNOWN', 
                filename: str = 'UNKNOWN') -> str:
        """增加一条 map 记录

        Args:
            category (str, optional): 地图的分类描述, 如: 'semantic_prior'. 默认为 'UNKNOWN'.
            filename (str, optional): 地图文件名, 指向地图的占用图像, 如: 'maps/sample.png'. 默认为 'UNKNOWN'.

        Returns:
            str: 插入数据库的 token
        """
        token = self.get_nuscenes_token()
        
        self._cursor.execute('''
            INSERT INTO map (token, category, filename) VALUES (?, ?, ?)
        ''', (token, category, filename))
        
        self._conn.commit()
        return token
    
    def add_scene(self, *,
                  log_token: str,
                  name: str = 'UNKNOWN',
                  description: str = 'UNKNOWN') -> str:
        """增加一条 scene 记录

        Args:
            log_token (str): 指向的 log 记录的 token
            name (str, optional): 场景的名称, 如: 'scene-0061'. 默认为 'UNKNOWN'.
            description (str, optional): 场景的描述, 如: 'Parked truck, construction, ...'. 默认为 'UNKNOWN'.

        Returns: 
            str: 插入数据库的 token
        """
        token = self.get_nuscenes_token()
        
        self._cursor.execute('''
            INSERT INTO scene (token, log_token, name, description) VALUES (?, ?, ?, ?)
        ''', (token, log_token, name, description))
        
        self._conn.commit()
        return token

    def add_sample(self, *,
                   scene_token: str,
                   timestamp: float = time.time(),
                   prev: str = None) -> str:
        """增加一条 sample 记录, 每一个 sample 是一帧采集

        Args:
            scene_token (str): 指向的 scene 记录的 token
            timestamp (float): 时间戳, 采用标准 Unix 时间戳, 单位为秒, 默认使用当前时间戳
            prev (str, optional): 前一个 sample 记录的 token, 默认为 None

        Returns:
            str: 插入数据库的 token
        """
        token = self.get_nuscenes_token()
        # 将时间戳转换为微秒, 与 nuScence 定义一致
        timestamp = self.get_nuscenes_timestamp(timestamp)
        
        # 记录新值
        self._cursor.execute('''
            INSERT INTO sample (token, scene_token, timestamp, prev) VALUES (?, ?, ?, ?)
        ''', (token, scene_token, timestamp, prev))
        
        # 更新前一个 sample 记录的 next 值
        if prev:
            self._cursor.execute('''
                UPDATE sample SET next = ? WHERE token = ?
            ''', (token, prev))
        self._conn.commit()
        return token
    
    def add_sensor(self, *,
                   channel: str,
                   modality: str) -> str:
        """增加一条 sensor 记录

        Args:
            channel (str, optional): 传感器的通道描述, 如: 'CAM_FRONT'.
            modality (str, optional): 传感器的模态描述, 如: 'camera'.

        Returns:
            str: 插入数据库的 token
        """
        token = self.get_nuscenes_token()
        
        self._cursor.execute('''
            INSERT INTO sensor (token, channel, modality) VALUES (?, ?, ?)
        ''', (token, channel, modality))
        
        self._conn.commit()
        return token
    
    def add_calibrated_sensor(self, *,
                               sensor_token: str,
                               translation: List[float],
                               rotation: List[float],
                               camera_intrinsic: List[float] = list()) -> str:
        """增加一条 calibrated_sensor 记录

        Args:
            sensor_token (str): 指向的 sensor 记录的 token
            translation (list[float]): 平移向量
            rotation (list[float]): 旋转矩阵
            camera_intrinsic (list[float], optional): 如果传感器是相机, 则需要提供相机内参, 默认为空列表

        Returns:
            str: 插入数据库的 token
        """
        token = self.get_nuscenes_token()
        
        # 转换部分数据为 json 格式
        translation = json.dumps(translation)
        rotation = json.dumps(rotation)
        camera_intrinsic = json.dumps(camera_intrinsic)
        
        self._cursor.execute('''
            INSERT INTO calibrated_sensor (token, sensor_token, translation, rotation, camera_intrinsic) VALUES (?, ?, ?, ?, ?)
        ''', (token, sensor_token, translation, rotation, camera_intrinsic))
        
        self._conn.commit()
        return token
    
    def add_ego_pose(self, *,
                     token: str,
                     timestamp: float = time.time(),
                     translation: List[float],
                     rotation: List[float]) -> str:
        """增加一条 ego_pose 记录

        Args:
            token (str, optional): 需要与 sample_data 表中的 token 一致
            timestamp (float, optional): 时间戳, 采用标准 Unix 时间戳, 单位为秒, 默认使用当前时间戳
            translation (list[float]): 平移向量
            rotation (list[float]): 旋转矩阵

        Returns:
            str: 插入数据库的 token
        """
        timestamp = self.get_nuscenes_timestamp(timestamp)
        
        # 转换部分数据为 json 格式
        translation = json.dumps(translation)
        rotation = json.dumps(rotation)
        
        self._cursor.execute('''
            INSERT INTO ego_pose (token, timestamp, translation, rotation) VALUES (?, ?, ?, ?)
        ''', (token, timestamp, translation, rotation))
        
        self._conn.commit()
        return token
    
    def add_sample_data(self, *,
                        token: str,
                        sample_token: str,
                        ego_pose_token: str,
                        calibrated_sensor_token: str,
                        timestamp: float = time.time(),
                        fileformat: str = 'UNKNOWN',
                        is_key_frame: bool = False,
                        height: int = 0,
                        width: int = 0,
                        filename: str = 'UNKNOWN',
                        prev: str = None) -> str:
        """增加一条 sample_data 记录

        Args:
            token (str, optional): 需要与 ego_pose 表中的 token 一致, 由外部程序确保一致性
            sample_token (str): 指向的 sample 记录的 token
            ego_pose_token (str): 指向的 ego_pose 记录的 token
            calibrated_sensor_token (str): 指向的 calibrated_sensor 记录的 token
            timestamp (float, optional): 时间戳, 采用标准 Unix 时间戳, 单位为秒, 默认使用当前时间戳
            fileformat (str, optional): 文件格式, 如: 'jpg'. 默认为 'UNKNOWN'.
            is_key_frame (bool, optional): 是否为关键帧, 默认为 False.
            height (int, optional): 图像高度, 默认为 0, 传入不为图像时请保持默认.
            width (int, optional): 图像宽度, 默认为 0, 传入不为图像时请保持默认.
            filename (str, optional): 文件名, 默认为 'UNKNOWN'.
            prev (str, optional): 前一个 sample_data 记录的 token, 默认为 None. 

        Returns:
            str: 插入数据库的 token
        """
        timestamp = self.get_nuscenes_timestamp(timestamp)
        
        # 记录新值
        self._cursor.execute('''
            INSERT INTO sample_data (token, sample_token, ego_pose_token, calibrated_sensor_token, timestamp, fileformat, is_key_frame, height, width, filename, prev) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (token, sample_token, ego_pose_token, calibrated_sensor_token, timestamp, fileformat, is_key_frame, height, width, filename, prev))
        
        # 更新前一个 sample_data 记录的 next 值
        if prev:
            self._cursor.execute('''
                UPDATE sample_data SET next = ? WHERE token = ?
            ''', (token, prev))
        
        self._conn.commit()
        return token

    def add_visibility(self, *,
                       token: str = None,
                       description: str,
                       level: str) -> str:
        """增加一条 visibility 记录

        Args:
            description (str): 可见性描述, 如: 'visible'.
            level (str): 可见性等级, 如: 'low'.

        Returns:
            str: 插入数据库的 token
        """
        token = token or self.get_nuscenes_token()
        
        self._cursor.execute('''
            INSERT INTO visibility (token, description, level) VALUES (?, ?, ?)
        ''', (token, description, level))
        
        self._conn.commit()
        return token
    
    def add_attribute(self, *,
                      name: str,
                      description: str = 'NOT_SET') -> str:
        """增加一条 attribute 记录

        Args:
            name (str): 属性名称, 如: 'car'.
            description (str, optional): 属性描述, 默认为 'NOT_SET'.

        Returns:
            str: 插入数据库的 token
        """
        token = self.get_nuscenes_token()
        
        self._cursor.execute('''
            INSERT INTO attribute (token, name, description) VALUES (?, ?, ?)
        ''', (token, name, description))
        
        self._conn.commit()
        return token

    def add_category(self, *,
                     index: int,
                     name: str,
                     description: str = 'UNKNOWN') -> str:
        """增加一条 category 记录

        Args:
            name (str): 类别名称, 如: 'car'.
            description (str, optional): 类别描述, 默认为 'UNKNOWN'.

        Returns:
            str: 插入数据库的 token
        """
        token = self.get_nuscenes_token()
        
        self._cursor.execute('''
            INSERT INTO category (token, name, description, seg_index) VALUES (?, ?, ?, ?)
        ''', (token, name, description, index))
        
        self._conn.commit()
        return token

    def add_instance(self, *,
                     category_token: str,
                     first_annotation_token: str = None) -> str:
        """增加一条 instance 记录

        Args:
            category_token (str): 指向的 category 记录的 token
            first_annotation_token (str, optional): 指向的第一个 sample_annotation 记录的 token, 默认为 None

        Returns:
            str: 插入数据库的 token
        """
        token = self.get_nuscenes_token()
        
        self._cursor.execute('''
            INSERT INTO instance (token, category_token, first_annotation_token, last_annotation_token) VALUES (?, ?, ?, ?)
        ''', (token, category_token, first_annotation_token, first_annotation_token))
        
        self._conn.commit()
        return token
    
    def add_sample_annotation(self, *,
                               token: str,
                               sample_token: str,
                               visibility_token: str,
                               attribute_tokens: List[str] = [],
                               instance_token: str,
                               translation: List[float],
                               size: List[float],
                               rotation: List[float],
                               num_lidar_pts: int,
                               num_radar_pts: int,
                               prev: str = None) -> str:
        """增加一条 sample_annotation 记录

        Args:
            token (str): 指向的 sample_data 记录的 token
            sample_token (str): 指向的 sample 记录的 token
            visibility_token (str): 指向的 visibility 记录的 token
            attribute_tokens (list[str], optional): 属性记录的 token 列表, 默认为空列表
            instance_token (str): 指向的 instance 记录的 token  
            translation (list[float]): 平移向量
            size (list[float]): 尺寸向量
            rotation (list[float]): 旋转矩阵
            num_lidar_pts (int): 激光雷达点数
            num_radar_pts (int): 雷达点数
            prev (str, optional): 前一个 sample_annotation 记录的 token, 默认为 None

        Returns:
            str: 插入数据库的 token
        """        
        # 转换部分数据为 json 格式
        attribute_tokens = json.dumps(attribute_tokens)
        translation = json.dumps(translation)
        size = json.dumps(size)
        rotation = json.dumps(rotation)
        
        # 记录新值
        self._cursor.execute('''
            INSERT INTO sample_annotation (token, sample_token, visibility_token, attribute_tokens, instance_token, translation, size, rotation, num_lidar_pts, num_radar_pts, prev) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (token, sample_token, visibility_token, attribute_tokens, instance_token, translation, size, rotation, num_lidar_pts, num_radar_pts, prev))
        
        # 更新 instance 表的 last_annotation_token
        self._cursor.execute('''
            UPDATE instance SET last_annotation_token = ? WHERE token = ?
        ''', (token, instance_token))
        
        # 更新前一个 sample_annotation 记录的 next 值
        if prev:
            self._cursor.execute('''
                UPDATE sample_annotation SET next = ? WHERE token = ?
            ''', (token, prev))
        
        self._conn.commit()
        return token    
    
    def add_lidarseg(self, *,
                     token: str,
                     sample_data_token: str,
                     filename: str) -> str:
        """增加一条 lidarseg 记录

        Args:
            token (str): 指向的 sample_data 记录的 token
            sample_data_token (str): 指向的 sample_data 记录的 token
            filename (str): 文件名
        """
        self._cursor.execute('''
            INSERT INTO lidarseg (token, sample_data_token, filename) VALUES (?, ?, ?)
        ''', (token, sample_data_token, filename))
        
        self._conn.commit()
        return token
    
    def dump_log(self) -> str:
        """导出 log 表为 json 格式

        Returns:
            str: json 格式的 log 表, 与 nuScence 定义一致
        """
        self._cursor.execute('''
            SELECT * FROM log
        ''')
        rows = self._cursor.fetchall()
        columns = [column[0] for column in self._cursor.description]
        return json.dumps([dict(zip(columns, row)) for row in rows])
        
    def dump_map(self) -> str:
        """导出 map 表为 json 格式
        
        以下字段由数据库查询获得:
        - log_tokens

        Returns:
            str: json 格式的 map 表, 与 nuScence 定义一致
        """
        self._cursor.execute('''
            SELECT m.*, GROUP_CONCAT(plm.log_token) as log_tokens
            FROM map m
            LEFT JOIN pair_log_map plm ON m.token = plm.map_token
            GROUP BY m.token
        ''')
        rows = self._cursor.fetchall()
        columns = [column[0] for column in self._cursor.description]
        result = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            # 将log_tokens字符串转换为列表
            if row_dict['log_tokens']:
                row_dict['log_tokens'] = row_dict['log_tokens'].split(',')
            else:
                row_dict['log_tokens'] = []
            result.append(row_dict)
        return json.dumps(result)
    
    def dump_scene(self) -> str:
        """导出 scene 表为 json 格式
        
        以下字段由数据库查询获得:
        - nbr_samples
        - first_sample_token
        - last_sample_token

        Returns:
            str: json 格式的 scene 表, 与 nuScence 定义一致
        """
        self._cursor.execute('''
            SELECT s.*, 
                   COUNT(sa.token) AS nbr_samples,
                   (SELECT sa1.token FROM sample sa1 WHERE sa1.scene_token = s.token AND sa1.prev IS NULL) AS first_sample_token,
                   (SELECT sa2.token FROM sample sa2 WHERE sa2.scene_token = s.token AND sa2.next IS NULL) AS last_sample_token
            FROM scene s
            LEFT JOIN sample sa ON s.token = sa.scene_token
            GROUP BY s.token
        ''')
        rows = self._cursor.fetchall()
        columns = [column[0] for column in self._cursor.description]
        
        # 将 None 转换为空字符串
        result = []
        for row in rows:
            row_dict = {col: (val if val is not None else '') for col, val in zip(columns, row)}
            result.append(row_dict)
        
        return json.dumps(result)

    def dump_sample(self) -> str:
        """导出 sample 表为 json 格式

        Returns:
            str: json 格式的 sample 表, 与 nuScence 定义一致
        """
        self._cursor.execute('''
            SELECT * FROM sample
        ''')
        rows = self._cursor.fetchall()
        columns = [column[0] for column in self._cursor.description]
        
        # 将 None 转换为空字符串
        result = []
        for row in rows:
            row_dict = {col: (val if val is not None else '') for col, val in zip(columns, row)}
            result.append(row_dict)
        
        return json.dumps(result)

    def dump_sensor(self) -> str:
        """导出 sensor 表为 json 格式

        Returns:
            str: json 格式的 sensor 表, 与 nuScence 定义一致
        """
        self._cursor.execute('''
            SELECT * FROM sensor
        ''')
        rows = self._cursor.fetchall()
        columns = [column[0] for column in self._cursor.description]
        return json.dumps([dict(zip(columns, row)) for row in rows])

    def dump_calibrated_sensor(self) -> str:
        """导出 calibrated_sensor 表为 json 格式

        Returns:
            str: json 格式的 calibrated_sensor 表, 与 nuScence 定义一致
        """
        self._cursor.execute('''
            SELECT * FROM calibrated_sensor
        ''')
        rows = self._cursor.fetchall()
        columns = [column[0] for column in self._cursor.description]
        
        result = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            # Decode the JSON strings for translation, rotation, and camera_intrinsic
            row_dict['translation'] = self._decode_json_list(row_dict['translation'])
            row_dict['rotation'] = self._decode_json_list(row_dict['rotation'])
            row_dict['camera_intrinsic'] = self._decode_json_list(row_dict['camera_intrinsic'])
            result.append(row_dict)
        
        return json.dumps(result)
    
    def dump_ego_pose(self) -> str:
        """导出 ego_pose 表为 json 格式

        Returns:
            str: json 格式的 ego_pose 表, 与 nuScence 定义一致
        """
        self._cursor.execute('''
            SELECT * FROM ego_pose
        ''')
        rows = self._cursor.fetchall()
        columns = [column[0] for column in self._cursor.description]
        
        result = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            # Decode the JSON strings for translation and rotation
            row_dict['translation'] = self._decode_json_list(row_dict['translation'])
            row_dict['rotation'] = self._decode_json_list(row_dict['rotation'])
            result.append(row_dict)
            
        return json.dumps(result)
    
    def dump_sample_data(self) -> str:
        """导出 sample_data 表为 json 格式

        Returns:
            str: json 格式的 sample_data 表, 与 nuScence 定义一致
        """
        self._cursor.execute('''
            SELECT * FROM sample_data
        ''')
        rows = self._cursor.fetchall()
        columns = [column[0] for column in self._cursor.description]
        
        result = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            # Convert None to empty string for 'next' and 'prev'
            row_dict['next'] = row_dict['next'] if row_dict['next'] is not None else ''
            row_dict['prev'] = row_dict['prev'] if row_dict['prev'] is not None else ''
            result.append(row_dict)
        
        return json.dumps(result)

    def dump_visibility(self) -> str:
        """导出 visibility 表为 json 格式

        Returns:
            str: json 格式的 visibility 表, 与 nuScence 定义一致
        """
        self._cursor.execute('''
            SELECT * FROM visibility
        ''')
        rows = self._cursor.fetchall()
        columns = [column[0] for column in self._cursor.description]
        return json.dumps([dict(zip(columns, row)) for row in rows])

    def dump_attribute(self) -> str:
        """导出 attribute 表为 json 格式

        Returns:
            str: json 格式的 attribute 表, 与 nuScence 定义一致 
        """
        self._cursor.execute('''
            SELECT * FROM attribute
        ''')
        rows = self._cursor.fetchall()
        columns = [column[0] for column in self._cursor.description]
        return json.dumps([dict(zip(columns, row)) for row in rows])

    def dump_instance(self) -> str:
        """导出 instance 表为 json 格式

        Returns:
            str: json 格式的 instance 表, 与 nuScence 定义一致
        """
        self._cursor.execute('''
            SELECT i.*, 
                COUNT(sa.instance_token) AS nbr_annotations
            FROM instance i
            LEFT JOIN sample_annotation sa ON i.token = sa.instance_token
            GROUP BY i.token
        ''')
        rows = self._cursor.fetchall()
        columns = [column[0] for column in self._cursor.description]
        
        result = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            result.append(row_dict)
        
        return json.dumps(result)

    def dump_category(self) -> str:
        """导出 category 表为 json 格式

        Returns:
            str: json 格式的 category 表, 与 nuScence 定义一致
        """
        self._cursor.execute('''
            SELECT * FROM category
        ''')
        rows = self._cursor.fetchall()
        columns = [column[0] for column in self._cursor.description]
        
        # 在字典中替换 'seg_index' 为 'index' 
        return json.dumps([
            {('index' if col == 'seg_index' else col): value for col, value in zip(columns, row)}
            for row in rows
        ])

    def dump_lidarseg(self) -> str:
        """导出 lidarseg 表为 json 格式

        Returns:
            str: json 格式的 lidarseg 表, 与 nuScence 定义一致
        """
        self._cursor.execute('''
            SELECT * FROM lidarseg
        ''')
        rows = self._cursor.fetchall()
        columns = [column[0] for column in self._cursor.description]
        return json.dumps([dict(zip(columns, row)) for row in rows])
    
    def dump_sample_annotation(self) -> str:
        """导出 sample_annotation 表为 json 格式

        Returns:
            str: json 格式的 sample_annotation 表, 与 nuScence 定义一致
        """
        self._cursor.execute('''
            SELECT * FROM sample_annotation
        ''')
        rows = self._cursor.fetchall()
        columns = [column[0] for column in self._cursor.description]
        return json.dumps([dict(zip(columns, row)) for row in rows])

    def get_category_token_by_index(self, index: int) -> str:
        """根据 index 获取 category 表中的 token"""
        self._cursor.execute('''
            SELECT token FROM category WHERE seg_index = ?
        ''', (index,))
        return self._cursor.fetchone()[0]
    
    def update_instance(self, *,
                        token: str,
                        last_annotation_token: str) -> None:
        """更新 instance 表中的记录"""
        self._cursor.execute('''
            UPDATE instance SET last_annotation_token = ? WHERE token = ?
        ''', (last_annotation_token, token))
        self._conn.commit()
