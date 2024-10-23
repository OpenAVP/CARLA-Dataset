import carla
import json
import os
import numpy as np
import random
import cv2
from threading import Lock
from datetime import datetime
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Union, List, Dict

from packages.carla1s.actors import RgbCamera, DepthCamera, SemanticCamera, SemanticLidar, Vehicle
from packages.carla1s.tf import Transform

from ..dataset_dumper import DatasetDumper
from .nuscences_db import NuScenesDB


class NuScenesLidarsegDumper(DatasetDumper):
    
    MAPPING_SEG_NUSCENES_DEFAULT = 0
    MAPPING_SEG_NUSCENES_EGO = 31
    MAPPING_SEG_CARLA_TO_NUSCENES = {		
        0: 0, # unlabeled => noise
        1: 24, #road => flat.driveable_surface
        2: 26, #sidewalk => flat.sidewalk
        3: 28, #building =>static.manmade
        4: 28, #wall => static.manmade
        5: 28, #fence => static.manmade
        6: 28, #pole =>static.manmade
        7: 28, #traffic light =>static.manmade
        8: 28, #traffic sign =>static.manmade
        9: 30, #vegetation=> static.vegetation
        10: 27,#terrain => flat.terrain
        11: 0, #sky =>noise
        12: 2, #pedestrain =>human.pedestrian.adult
        13: 14, #rider => vehicle.bicycle
        14: 17, #car => vehicle.car
        15: 23, #truck =>vehicle.truck
        16: 16, #bus =>vehicle.bus.rigid
        17: 23, #train =>vehicle.bus.bendy
        18: 21, #motocycle=>vehicle.motorcycle
        19: 14, #bicycle =>vehicle.bicycle
        20: 29, #static =>static.other
        21: 9,  #dynamic => movable_object.barrier
        22: 29, #other =>static.other
        23: 29, #water=>static.other
        24: 24, #road line =>flat.driveable_surface
        25: 24, #ground =>flat.driveable_surface
        26: 29, #brige=>static.other
        27: 29, #rail track=>static.other
        28: 29, #guard rail=>static.other
        # 29: 25, #parking lane=>flat.other
        29: 24, #parking lane=>flat.driveable_surface
        30: 24,  #parking area=>flat.driveable_surface
    }  
    
    @dataclass
    class SensorBind(DatasetDumper.SensorBind):
        channel: str = None
        token_sensor: str = None
        token_calibrated_sensor: str = None

    @dataclass
    class CameraBind(SensorBind): pass

    @dataclass
    class LidarBind(SensorBind): pass
    
    @dataclass
    class SemanticLidarBind(LidarBind): pass

    @dataclass
    class VehicleBind(DatasetDumper.Bind): pass
    
    def __init__(self, 
                 root_path: str, 
                 *, 
                 max_workers: int = 3,
                 map_name: str = 'UNKNOWN_CARLA_MAP',
                 sequence_description: str = 'UNKNOWN'):
        super().__init__(root_path, max_workers)
        self._db: NuScenesDB = None  # WARNING: NEVER EXPOSE THIS PROPERTY TO THE PUBLIC
        self._map_name: str = map_name
        # DB TOKENS
        self._token_current_map: str = None
        self._token_current_scene: str = None
        self._token_current_log: str = None
        self._token_current_sample: str = None
        self._token_current_ego_pose: str = None
        self._token_current_sample_data: str = None
        self._token_default_attribute: str = None
        self._token_default_visibility: str = None
        # SEQUENCE INFO
        self._current_sequence_description: str = sequence_description
        self._current_sequence_data_header: str = ''
        self._current_sequence_known_objects: Dict[int, str] = dict()  # object_id, instance_token
        self._current_frame_timestamp: float = 0.0
        self._current_frame_ego_pose_translation: List[float] = [0.0, 0.0, 0.0]
        self._current_frame_ego_pose_rotation: List[float] = [0.0, 0.0, 0.0, 1.0]
        # LOCK
        self._lock_db: Lock = Lock()

    @property
    def current_frame_name(self) -> str:
        return str(self._current_frame_count)

    @contextmanager
    def create_sequence(self, 
                        name: str = None, 
                        *, 
                        description: str = 'UNKNOWN'):
        self.current_sequence_description = description
        super().create_sequence(name)
        self._setup_content_folder()
        self._setup_database()
        self.logger.info("=> SEQUENCE BEGINS ".ljust(80, '='))
        yield
        self.logger.info("=> SEQUENCE ENDS ".ljust(80, '='))
        self.dump_database()
    
    def create_frame(self) -> 'NuScenesLidarsegDumper':
        # 处理每帧开头的准备工作
        self._current_frame_count += 1
        self._token_current_sample_data = None
        self._promises = []
        
        # 如果是第一帧,必须执行一次空的 join
        if self._current_frame_count == 1:
            self.join()
        
        # 随机选取一个 Sensor, 等待它的数据更新, 优先选择 Camera
        # 在这个情况下, 车辆的移动已经完成, 采集时间戳可以被确定
        selected_binds_camera = [bind for bind in self.binds if isinstance(bind, self.CameraBind)]
        selected_binds_sensor = [bind for bind in self.binds if isinstance(bind, self.SensorBind)]
        if any(selected_binds_camera):
            selected_bind = random.choice(selected_binds_camera)
        elif any(selected_binds_sensor):
            selected_bind = random.choice(selected_binds_sensor)
        else:
            raise ValueError("No sensor bind found, please call `bind_somesensor()` first.")
        
        # 等待传感器数据更新
        self.logger.debug(f'Choose sensor: {selected_bind.actor.name} to wait for data update.')
        selected_bind.actor.on_data_ready.wait()
        self.logger.debug(f'Sensor {selected_bind.actor.name} data updated.')
        
        # 获取时间戳
        self._current_frame_timestamp = selected_bind.actor.data.timestamp
        
        # 在数据库中创建 sample 记录, 并更新当前 sample 的 token
        self._token_current_sample = self._db.add_sample(
            scene_token=self._token_current_scene, 
            timestamp=self._current_frame_timestamp, 
            prev=self._token_current_sample
        )
        
        # 暂存 ego pose 记录
        vehicle_bind = next((bind for bind in self.binds if isinstance(bind, self.VehicleBind)), None)
        if not vehicle_bind:
            raise ValueError("Vehicle bind is not found, please call `bind_vehicle()` first.")
        tf = vehicle_bind.actor.get_transform()
        self._current_frame_ego_pose_translation = [tf.x, tf.y, tf.z]
        self._current_frame_ego_pose_rotation = tf.quaternion.tolist()
        
        # 并行处理传感器数据
        for bind in self.binds:
            if isinstance(bind, self.CameraBind):
                self._promises.append(self.thread_pool.submit(self._dump_image_with_sample_data, bind))
            if isinstance(bind, self.LidarBind):
                self._promises.append(self.thread_pool.submit(self._dump_lidar_with_sample_data_and_lidarseg, bind, vehicle_bind))
            if isinstance(bind, self.SemanticLidarBind):
                self._promises.append(self.thread_pool.submit(self._dump_instance_with_annotation, bind, vehicle_bind))
        
        return self
    
    def bind_camera(self, 
                    sensor: Union[RgbCamera, DepthCamera, SemanticCamera], 
                    *, 
                    channel: str) -> 'DatasetDumper':
        # 阻止完全重复的绑定
        if any(bind.channel == channel and bind.actor == sensor for bind in self.binds if isinstance(bind, self.CameraBind)):
            self.logger.warning(f"Sensor {sensor} with channel '{channel}' is already bound. Skipping binding.")
            return self
        
        # 如果传感器的 rolename 与 channel 不同, 则提醒
        role_name = sensor.attributes.get('role_name', None)
        if role_name != channel:
            self.logger.warning(f"Note that sensor role name '{role_name}' is different from channel '{channel}'.")
        
        # 执行绑定
        self._binds.append(self.CameraBind(actor=sensor, channel=channel))
        return self
    
    def bind_semantic_lidar(self, 
                            sensor: Union[SemanticLidar], 
                            *, 
                            channel: str) -> 'DatasetDumper':
        # 阻止完全重复的绑定
        if any(bind.channel == channel and bind.actor == sensor for bind in self.binds if isinstance(bind, self.LidarBind)):
            self.logger.warning(f"Sensor {sensor} with channel '{channel}' is already bound. Skipping binding.")
            return self
        
        # 如果传感器的 rolename 与 channel 不同, 则提醒
        role_name = sensor.attributes.get('role_name', None)
        if role_name != channel:
            self.logger.warning(f"Note that sensor role name '{role_name}' is different from channel '{channel}'.")
        
        # 执行绑定
        self._binds.append(self.SemanticLidarBind(actor=sensor, channel=channel))
        return self
    
    def bind_vehicle(self, vehicle: Union[Vehicle]) -> 'DatasetDumper':
        self._binds.append(self.VehicleBind(actor=vehicle))
        return self

    def dump_database(self):
        """将数据库写入文件."""
        self.logger.info(f"Dumping nuscences database to file.")
        
        db_folder = os.path.join(self.current_sequence_path, self.current_sequence_name)    

        self._dump_json_to_file(self._db.dump_visibility(), os.path.join(db_folder, 'visibility.json'))
        self._dump_json_to_file(self._db.dump_category(), os.path.join(db_folder, 'category.json'))
        self._dump_json_to_file(self._db.dump_attribute(), os.path.join(db_folder, 'attribute.json'))
        self._dump_json_to_file(self._db.dump_log(), os.path.join(db_folder, 'log.json'))
        self._dump_json_to_file(self._db.dump_map(), os.path.join(db_folder, 'map.json'))
        self._dump_json_to_file(self._db.dump_sensor(), os.path.join(db_folder, 'sensor.json'))
        self._dump_json_to_file(self._db.dump_calibrated_sensor(), os.path.join(db_folder, 'calibrated_sensor.json'))
        self._dump_json_to_file(self._db.dump_scene(), os.path.join(db_folder, 'scene.json'))
        self._dump_json_to_file(self._db.dump_sample(), os.path.join(db_folder, 'sample.json'))
        self._dump_json_to_file(self._db.dump_ego_pose(), os.path.join(db_folder, 'ego_pose.json'))
        self._dump_json_to_file(self._db.dump_sample_data(), os.path.join(db_folder, 'sample_data.json'))
        self._dump_json_to_file(self._db.dump_lidarseg(), os.path.join(db_folder, 'lidarseg.json'))
        self._dump_json_to_file(self._db.dump_instance(), os.path.join(db_folder, 'instance.json'))
        self._dump_json_to_file(self._db.dump_sample_annotation(), os.path.join(db_folder, 'sample_annotation.json'))

        self.logger.info(f"Database dumped successfully.")

    def _dump_image_with_sample_data(self, bind: CameraBind):
        # 阻塞等待传感器更新
        bind.actor.on_data_ready.wait()
        
        # 储存数据
        file_name = f"{self._current_sequence_data_header}__{bind.channel}__{self._db.get_nuscenes_timestamp(self._current_frame_timestamp)}.jpg"
        short_path = os.path.join('samples', bind.channel, file_name)
        path = os.path.join(self.current_sequence_path, short_path)
        cv2.imwrite(path, bind.actor.data.content)

        # 写入 sample_data 表和 ego_pose 表, 加锁以保证操作原子化
        with self._lock_db:
            token = self._db.get_nuscenes_token()
            self._db.add_sample_data(
                token=token,
                sample_token=self._token_current_sample,
                calibrated_sensor_token=bind.token_calibrated_sensor,
                ego_pose_token=token,
                filename=short_path,
                timestamp=self._current_frame_timestamp,
                fileformat='jpg',
                is_key_frame=True,  # CARLA 中所有帧都是关键帧
                width=bind.actor.attributes['image_size_x'],
                height=bind.actor.attributes['image_size_y'],
                prev=self._token_current_sample_data
            )
            
            self._db.add_ego_pose(
                token=token,
                timestamp=self._current_frame_timestamp,
                translation=self._current_frame_ego_pose_translation,
                rotation=self._current_frame_ego_pose_rotation
            )
            
            self._token_current_sample_data = token
        
        # 打印日志
        self.logger.debug(f"Dumped '{bind.channel}' image to {path}")
        self.logger.debug(f"Created '{bind.channel}' sample_data record with token: '{token}'")
        self.logger.debug(f"Created '{bind.channel}' ego_pose record with token: '{token}'")
    
    def _dump_lidar_with_sample_data_and_lidarseg(self, bind: LidarBind, vehicle_bind: VehicleBind):
        # 阻塞等待传感器更新
        bind.actor.on_data_ready.wait()
        
        # 储存数据
        file_name = f"{self._current_sequence_data_header}__{bind.channel}__{self._db.get_nuscenes_timestamp(self._current_frame_timestamp)}.bin"
        short_path = os.path.join('samples', bind.channel, file_name)
        path = os.path.join(self.current_sequence_path, short_path)
        
        # 储存点云数据
        data = np.insert(bind.actor.data.content, 4, np.arange(1, bind.actor.data.content.shape[0] + 1), axis=1)
        data.tofile(path)
        self.logger.debug(f"Dumped '{bind.channel}' lidar to {path}, points: {data.shape[0]}")
        
        # 写入 sample_data 表和 ego_pose 表, 加锁以保证操作原子化
        with self._lock_db:
            token = self._db.get_nuscenes_token()
            self._db.add_sample_data(
                token=token,
                sample_token=self._token_current_sample,
                calibrated_sensor_token=bind.token_calibrated_sensor,
                ego_pose_token=token,
                filename=short_path,
                timestamp=self._current_frame_timestamp,
                fileformat='pcd',
                is_key_frame=True,  # CARLA 中所有帧都是关键帧
                prev=self._token_current_sample_data
            )
            
            self._db.add_ego_pose(
                token=token,
                timestamp=self._current_frame_timestamp,
                translation=self._current_frame_ego_pose_translation,
                rotation=self._current_frame_ego_pose_rotation
            )
            
            self._token_current_sample_data = token
            
        self.logger.debug(f"Created '{bind.channel}' sample_data record with token: '{token}'")
        self.logger.debug(f"Created '{bind.channel}' ego_pose record with token: '{token}'")
        
        # 准备并写入 lidarseg 数据
        # WARNING: 禁止更改该操作所在位置
        file_name_lidarseg = f"{token}_lidarseg.bin"
        short_path_lidarseg = os.path.join('lidarseg', file_name_lidarseg)
        path_lidarseg = os.path.join(self.current_sequence_path, short_path_lidarseg)
        seg_id = bind.actor.data.content[:, 3]
        obj_id = bind.actor.data.content[:, 4]
        
        # 重新映射 index
        # STEP1: 处理标签映射
        seg_id = np.array([self.MAPPING_SEG_CARLA_TO_NUSCENES.get(i, self.MAPPING_SEG_NUSCENES_DEFAULT) for i in seg_id])
        
        # STEP2: 处理 vehicle.ego 的特殊标签
        if vehicle_bind and vehicle_bind.actor:
            index_ego = np.where(obj_id == int(vehicle_bind.actor.entity.id))[0]
        else:
            index_ego = np.array([])
            
        # STEP3: 将 ego vehicle 的标签设置为 MAPPING_SEG_NUSCENES_EGO
        seg_id[index_ego] = self.MAPPING_SEG_NUSCENES_EGO
        
        # 写入数据
        seg_id.tofile(path_lidarseg)
        self.logger.debug(f"Dumped '{bind.channel}' lidarseg to {path_lidarseg}, points: {seg_id.shape[0]}")

        # 写入 lidarseg 表
        with self._lock_db:
            token = self._db.add_lidarseg(
                token=token,
                sample_data_token=token,
                filename=short_path_lidarseg
            )
        self.logger.debug(f"Created '{bind.channel}' lidarseg record with token: '{token}'")

    def _dump_instance_with_annotation(self, bind: SemanticLidarBind, vehicle_bind: VehicleBind):
        # 阻塞等待传感器更新
        bind.actor.on_data_ready.wait()
        
        @dataclass
        class ObjectInfo:
            object_id: int
            semantic_id: int
            lidar_count: int = 0
            radar_count: int = 0
            translation = [0, 0, 0]
            size = [0, 0, 0]
            rotation = [0, 0, 0, 0]
        
        infos: Dict[int, ObjectInfo] = dict()
        
        # 解析点云数据, 聚类每个 objectId , semanticId 及其出现的次数
        vehicle_id = vehicle_bind.actor.entity.id if vehicle_bind and vehicle_bind.actor else None
        cloud = bind.actor.data.content
        for row in cloud:
            object_id = int(row[3])
            semantic_id = int(row[4])
            
            # 重新映射 semantic_id, 并考虑 ego vehicle 的特殊标签
            semantic_id = self.MAPPING_SEG_CARLA_TO_NUSCENES.get(semantic_id, self.MAPPING_SEG_NUSCENES_DEFAULT)
            if vehicle_id == object_id:
                semantic_id = self.MAPPING_SEG_NUSCENES_EGO

            # 如果 object_id 在当前帧中未知, 则创建一个新的 ObjectInfo 对象
            if object_id not in infos:
                infos[object_id] = ObjectInfo(object_id=object_id, semantic_id=semantic_id)
            
            # 增加点云计数
            infos[object_id].lidar_count += 1
            
        # 打印聚类结果日志
        self.logger.debug(f"Annotated {len(infos)} instances from '{bind.channel}' lidar.")
        
        # 获取所有 actor 的 bounding box
        # WARNING: 此处使用了原生 CARLA API, 注意甄别
        world = bind.actor.entity.get_world()
        actors = world.get_actors()
        for actor in actors:
            # 如果聚类结果中不存在该 object_id, 则跳过
            if actor.id not in infos:
                continue
            # 否则更新聚类结果
            bb = actor.bounding_box
            bb_tf = Transform(x=bb.location.x, y=bb.location.y, z=bb.location.z, yaw=bb.rotation.yaw, pitch=bb.rotation.pitch, roll=bb.rotation.roll)
            info = infos[actor.id]
            info.translation = [bb.location.x, bb.location.y, bb.location.z]
            info.size = [bb.extent.x, bb.extent.y, bb.extent.z]
            info.rotation = bb_tf.quaternion.tolist()
            
        # 打印聚类结果日志
        self.logger.debug(f"Annotated {len(infos)} instances with MAPPING_SEG_CARLA_TO_NUSCENES filter.")

        # 确定 instance 
        prev_annotation_token = None
        for info in infos.values():
            # TODO: 需确定是否需要该忽略
            # 忽略标签为 MAPPING_SEG_NUSCENES_DEFAULT 0 - noise 的实例
            # if info.semantic_id == self.MAPPING_SEG_NUSCENES_DEFAULT:
            #     continue
            
            token_annotation = self._db.get_nuscenes_token()
            with self._lock_db:
                token_category = self._db.get_category_token_by_index(info.semantic_id)
            token_instance = None
            
            # 如果 object_id 在当前序列中未知, 则创建一个新的 instance 记录, 并更新当前序列已知对象字典
            if info.object_id not in self._current_sequence_known_objects:
                with self._lock_db:
                    token_instance = self._db.add_instance(
                        category_token=token_category,
                        first_annotation_token=token_annotation
                    )
                self._current_sequence_known_objects[info.object_id] = token_instance
                self.logger.debug(f"Created '{bind.channel}' instance record with token: '{token_instance}' for object_id: {info.object_id}")
            else:
                token_instance = self._current_sequence_known_objects[info.object_id]
                
            # 更新 instance 与 annotation 表
            with self._lock_db:
                self._db.update_instance(
                    token=token_instance,
                    last_annotation_token=token_annotation
                )
                prev_annotation_token = self._db.add_sample_annotation(
                    token=token_annotation,
                    sample_token=self._token_current_sample,
                    instance_token=token_instance,
                    attribute_tokens=[self._token_default_attribute],
                    visibility_token=self._token_default_visibility,
                    translation=info.translation,
                    size=info.size,
                    rotation=info.rotation,
                    num_lidar_pts=info.lidar_count,
                    num_radar_pts=info.radar_count,
                    prev=prev_annotation_token
                )
                self.logger.debug(f"Created annotation record for object_id: {info.object_id}, token: '{token_annotation}'")


    def _setup_database(self):
        """创建数据库文件."""
        self._db = NuScenesDB(os.path.join(self.current_sequence_path, 'nuscences.db'))
        self._setup_db_visibility()
        self._setup_db_category()
        self._setup_db_attribute()
        self._setup_db_map()
        self._setup_db_log()
        self._setup_db_sensor()
        self._setup_db_calibrated_sensor()
        self._setup_db_scene()

    def _setup_db_visibility(self):
        """填充 visibility 表."""
        self._db.add_visibility(token='1', description="visibility of whole object is between 0 and 40%", level="v0-40")
        self._db.add_visibility(token='2', description="visibility of whole object is between 40 and 60%", level="v40-60")
        self._db.add_visibility(token='3', description="visibility of whole object is between 60 and 80%", level="v60-80")
        self._token_default_visibility = self._db.add_visibility(token='4', description="visibility of whole object is between 80 and 100%", level="v80-100")

    def _setup_db_category(self):
        """填充 category 表."""
        self._db.add_category(index=0, name="noise", description="Any lidar return that does not correspond to a physical object, such as dust, vapor, noise, fog, raindrops, smoke and reflections.")
        self._db.add_category(index=1, name="animal", description="All animals, e.g. cats, rats, dogs, deer, birds.")
        self._db.add_category(index=2, name="human.pedestrian.adult", description="Adult subcategory.")
        self._db.add_category(index=3, name="human.pedestrian.child", description="Child subcategory.")
        self._db.add_category(index=4, name="human.pedestrian.construction_worker", description="Construction worker")
        self._db.add_category(index=5, name="human.pedestrian.personal_mobility", description="A small electric or self-propelled vehicle, e.g. skateboard, segway, or scooters, on which the person typically travels in a upright position. Driver and (if applicable) rider should be included in the bounding box along with the vehicle.")
        self._db.add_category(index=6, name="human.pedestrian.police_officer", description="Police officer.")
        self._db.add_category(index=7, name="human.pedestrian.stroller", description="Strollers. If a person is in the stroller, include in the annotation.")
        self._db.add_category(index=8, name="human.pedestrian.wheelchair", description="Wheelchairs. If a person is in the wheelchair, include in the annotation.")
        self._db.add_category(index=9, name="movable_object.barrier", description="Temporary road barrier placed in the scene in order to redirect traffic. Commonly used at construction sites. This includes concrete barrier, metal barrier and water barrier. No fences.")
        self._db.add_category(index=10, name="movable_object.debris", description="Movable object that is left on the driveable surface that is too large to be driven over safely, e.g tree branch, full trash bag etc.")
        self._db.add_category(index=11, name="movable_object.pushable_pullable", description="Objects that a pedestrian may push or pull. For example dolleys, wheel barrows, garbage-bins, or shopping carts.")
        self._db.add_category(index=12, name="movable_object.trafficcone", description="All types of traffic cone.")
        self._db.add_category(index=13, name="static_object.bicycle_rack", description="Area or device intended to park or secure the bicycles in a row. It includes all the bikes parked in it and any empty slots that are intended for parking bikes.")
        self._db.add_category(index=14, name="vehicle.bicycle", description="Human or electric powered 2-wheeled vehicle designed to travel at lower speeds either on road surface, sidewalks or bike paths.")
        self._db.add_category(index=15, name="vehicle.bus.bendy", description="Bendy bus subcategory. Annotate each section of the bendy bus individually.")
        self._db.add_category(index=16, name="vehicle.bus.rigid", description="Rigid bus subcategory.")
        self._db.add_category(index=17, name="vehicle.car", description="Vehicle designed primarily for personal use, e.g. sedans, hatch-backs, wagons, vans, mini-vans, SUVs and jeeps. If the vehicle is designed to carry more than 10 people use vehicle.bus. If it is primarily designed to haul cargo use vehicle.truck.")
        self._db.add_category(index=18, name="vehicle.construction", description="Vehicles primarily designed for construction. Typically very slow moving or stationary. Cranes and extremities of construction vehicles are only included in annotations if they interfere with traffic. Trucks used to haul rocks or building materials are considered vehicle.truck rather than construction vehicles.")
        self._db.add_category(index=19, name="vehicle.emergency.ambulance", description="All types of ambulances.")
        self._db.add_category(index=20, name="vehicle.emergency.police", description="All types of police vehicles including police bicycles and motorcycles.")
        self._db.add_category(index=21, name="vehicle.motorcycle", description="Gasoline or electric powered 2-wheeled vehicle designed to move rapidly (at the speed of standard cars) on the road surface. This category includes all motorcycles, vespas and scooters.")
        self._db.add_category(index=22, name="vehicle.trailer", description="Any vehicle trailer, both for trucks, cars and bikes.")
        self._db.add_category(index=23, name="vehicle.truck", description="Vehicles primarily designed to haul cargo including pick-ups, lorrys, trucks and semi-tractors. Trailers hauled after a semi-tractor should be labeled as vehicle.trailer")
        self._db.add_category(index=24, name="flat.driveable_surface", description="All paved or unpaved surfaces that a car can drive on with no concern of traffic rules.")
        self._db.add_category(index=25, name="flat.other", description="All other forms of horizontal ground-level structures that do not belong to any of driveable_surface, curb, sidewalk and terrain. Includes elevated parts of traffic islands, delimiters, rail tracks, stairs with at most 3 steps and larger bodies of water (lakes, rivers).")
        self._db.add_category(index=26, name="flat.sidewalk", description="Sidewalk, pedestrian walkways, bike paths, etc. Part of the ground designated for pedestrians or cyclists. Sidewalks do **not** have to be next to a road.")
        self._db.add_category(index=27, name="flat.terrain", description="Natural horizontal surfaces such as ground level horizontal vegetation (< 20 cm tall), grass, rolling hills, soil, sand and gravel.")
        self._db.add_category(index=28, name="static.manmade", description="Includes man-made structures but not limited to: buildings, walls, guard rails, fences, poles, drainages, hydrants, flags, banners, street signs, electric circuit boxes, traffic lights, parking meters and stairs with more than 3 steps.")
        self._db.add_category(index=29, name="static.other", description="Points in the background that are not distinguishable, or objects that do not match any of the above labels.")
        self._db.add_category(index=30, name="static.vegetation", description="Any vegetation in the frame that is higher than the ground, including bushes, plants, potted plants, trees, etc. Only tall grass (> 20cm) is part of this, ground level grass is part of `terrain`.")
        self._db.add_category(index=31, name="vehicle.ego", description="The vehicle on which the cameras, radar and lidar are mounted, that is sometimes visible at the bottom of the image.")

    def _setup_db_attribute(self):
        """填充 attribute 表."""
        self._db.add_attribute(name="vehicle.moving", description="Vehicle is moving.")
        self._db.add_attribute(name="vehicle.stopped", description="Vehicle, with a driver/rider in/on it, is currently stationary but has an intent to move.")
        self._db.add_attribute(name="vehicle.parked", description="Vehicle is stationary (usually for longer duration) with no immediate intent to move.")
        self._db.add_attribute(name="cycle.with_rider", description="There is a rider on the bicycle or motorcycle.")
        self._db.add_attribute(name="cycle.without_rider", description="There is NO rider on the bicycle or motorcycle.")
        self._db.add_attribute(name="pedestrian.sitting_lying_down", description="The human is sitting or lying down.")
        self._db.add_attribute(name="pedestrian.standing", description="The human is standing.")
        self._db.add_attribute(name="pedestrian.moving", description="The human is moving.")
        self._token_default_attribute = self._db.add_attribute(name="default", description="Default attribute.")

    def _setup_db_map(self):
        """填充 map 表."""
        token = self._db.add_map(category='semantic_prior')
        self._token_current_map = token

    def _setup_db_log(self):
        """填充 log 表."""
        if not self._token_current_map:
            raise ValueError("Map token is None or Empty, please call `_setup_db_map` first.")
        
        # 尝试在 binds 中找到 VehicleBind
        vehicle_bind = next((bind for bind in self.binds if isinstance(bind, self.VehicleBind)), None)
        vehicle_name = 'UNKNOWN_CARLA_VEHICLE'
        if vehicle_bind and vehicle_bind.actor:
            vehicle_name = vehicle_bind.actor.attributes.get('role_name', vehicle_name)
            
        dtime = datetime.now()
        
        self._token_current_log = self._db.add_log(vehicle=vehicle_name, 
                                                    location=self._map_name, 
                                                    map_token=self._token_current_map,
                                                    dtime=dtime)
        self._current_sequence_data_header = f"{vehicle_name}-{dtime.strftime('%Y-%m-%d-%H-%M-%S%z')}"
    
    def _setup_db_sensor(self):
        """填充 sensor 表."""
        for bind in [bind for bind in self.binds if isinstance(bind, self.SensorBind)]:
            # 根据绑定确定模态
            if isinstance(bind, self.CameraBind):
                modality = 'camera'
            elif isinstance(bind, self.LidarBind):
                modality = 'lidar'
            else:
                raise ValueError(f"Unknown sensor modality: {type(bind)}")

            # 添加传感器记录
            token = self._db.add_sensor(channel=bind.channel, modality=modality)
            bind.token_sensor = token
            
    def _setup_db_calibrated_sensor(self):
        """填充 calibrated_sensor 表."""
        for bind in [bind for bind in self.binds if isinstance(bind, self.SensorBind)]:
            # 阻止 token_sensor 为空的绑定
            if not bind.token_sensor:
                raise ValueError(f"Sensor token is None or Empty, please call `_setup_db_sensor` first.")
            
            # 对于相机计算 3x3 内参矩阵
            if isinstance(bind, self.CameraBind):
                width = int(bind.actor.attributes['image_size_x'])
                height = int(bind.actor.attributes['image_size_y'])
                fov = float(bind.actor.attributes['fov'])
                focal = width / (2.0 * np.tan(fov * np.pi / 360.0))
                intrinsic = np.identity(3)
                intrinsic[0, 0] = intrinsic[1, 1] = focal
                intrinsic[0, 2] = width / 2.0
                intrinsic[1, 2] = height / 2.0
                intrinsic[2, 2] = 1
                intrinsic = intrinsic.tolist()

            tf = bind.actor.get_transform(relative=True)
            translation = [tf.x, tf.y, tf.z]
            rotation = tf.quaternion.tolist()
            token = self._db.add_calibrated_sensor(sensor_token=bind.token_sensor, 
                                                   translation=translation, 
                                                   rotation=rotation, 
                                                   camera_intrinsic=intrinsic)
            bind.token_calibrated_sensor = token

    def _setup_db_scene(self):
        """填充 scene 表."""
        token = self._db.add_scene(
            name=self._current_sequence_name, 
            log_token=self._token_current_log, 
            description=self._current_sequence_description
        )
        self._token_current_scene = token

    def _dump_json_to_file(self, json_str: str, filename: str):
        """将 JSON 数据写入文件."""
        with open(filename, 'w') as f:
            # 进行格式化
            json.dump(json.loads(json_str), f, indent=2)
        self.logger.info(f"Dumped JSON data to file: {filename}")

    def _setup_content_folder(self):
        """创建内容文件夹."""
        # L1: 创建 nuscence 文件夹一层结构
        os.makedirs(os.path.join(self.current_sequence_path, 'maps'))
        os.makedirs(os.path.join(self.current_sequence_path, 'samples'))
        os.makedirs(os.path.join(self.current_sequence_path, 'sweeps'))
        os.makedirs(os.path.join(self.current_sequence_path, self.current_sequence_name))
        os.makedirs(os.path.join(self.current_sequence_path, 'lidarseg'))

        # L2: 根据传感器绑定的 channel 创建 samples 文件夹, 并在 sweeps 文件夹下创建软连接
        for bind in [bind for bind in self.binds if isinstance(bind, self.SensorBind)]:
            folder_path = os.path.join(self.current_sequence_path, 'samples', bind.channel)
            os.makedirs(folder_path)
            self.logger.info(f"Created folder at: {folder_path}")
            # 创建软连接
            os.symlink(os.path.join(folder_path), os.path.join(self.current_sequence_path, 'sweeps', bind.channel))

