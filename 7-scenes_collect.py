#!/usr/bin/python
# Write Python 3 code in this online editor and run it.
import carla
import numpy as np
import os
import math
import time
import random
import cv2
import sustech_coe_parkinglot_enhancement
from queue import Queue

# ======================
# 1. Carla连接与基础配置
# ======================

def setup_carla(map_name):
    client = carla.Client('172.17.0.1', 2000)  # 连接Carla服务器
    client.set_timeout(5.0)                 # 设置超时时间
    world = client.get_world()
    
    # 2. 加载指定地图（替换为实际地图名称）
    world = client.load_world(map_name)        # 示例地图
    settings = world.get_settings()
    settings.synchronous_mode = True           # 启用同步模式
    settings.fixed_delta_seconds = 0.033         # 固定时间步长
    world.apply_settings(settings)
    
    return client, world

# ======================
# 3. 载具生成模块
# ======================

def spawn_ego_vehicle(world):
    blueprint_library = world.get_blueprint_library()
    vehicle_bp = blueprint_library.filter('vehicle.tesla.model3')[0]  # 选择特斯拉Model3
    spawn_points = world.get_map().get_spawn_points()
    spawn_point = random.choice(spawn_points)
    # 生成自车
    ego_vehicle = world.spawn_actor(vehicle_bp, spawn_point)
    ego_vehicle.set_autopilot(True)
    return ego_vehicle

# ======================
# 4. 传感器配置
# ======================

class CameraManager:
    def __init__(self, ego_vehicle, world):
        self.ego_vehicle = ego_vehicle
        self.world = world
        self.rgb_queue = Queue(maxsize=100)      # RGB图像队列
        self.depth_queue = Queue(maxsize=100)    # 深度图像队列
        self.pose_queue = Queue(maxsize=100)     # 位姿矩阵队列
        
        # 创建摄像头蓝图
        self.create_cameras()

    def create_cameras(self):
        camera_transform = carla.Transform(carla.Location(x=1.5, y=0, z=2.4))
        # 前视RGB相机
        rgb_bp = self.create_camera_blueprint('sensor.camera.rgb', 640, 480, 90)
        self.rgb_sensor = self.world.spawn_actor(
            rgb_bp, camera_transform, attach_to=self.ego_vehicle)
        self.rgb_sensor.listen(self._rgb_callback)

        # 前视深度相机
        depth_bp = self.create_camera_blueprint('sensor.camera.depth', 640, 480, 90)
        self.depth_sensor = self.world.spawn_actor(
            depth_bp, camera_transform, attach_to=self.ego_vehicle)
        self.depth_sensor.listen(self._depth_callback)

    def create_camera_blueprint(self, cam_type, width, height, fov):
        blueprint = self.world.get_blueprint_library().find(cam_type)
        blueprint.set_attribute('image_size_x', f'{width}')
        blueprint.set_attribute('image_size_y', f'{height}')
        blueprint.set_attribute('fov', f'{fov}')
        return blueprint

    def _rgb_callback(self, image):
        array = np.reshape(np.copy(image.raw_data), (image.height, image.width, 4))
        array = array[:, :, :3]  # 去除Alpha通道
        self.rgb_queue.put(array.copy())

    def _depth_callback(self, image):
        self.depth_queue.put(image)

# ======================
# 5. 主循环与数据采集
# ======================

def main_loop(client, world, ego_vehicle, camera_manager, frame_limit = 0):
    time.sleep(2)
    try:
        frame_count = 0
        while True:
            print("frame count:",frame_count)
            world.tick()  # 同步模式必须调用tick
            
            # 获取自车位姿矩阵
            pose_matrix = ego_vehicle.get_transform().get_matrix()
            camera_manager.pose_queue.put(np.array(pose_matrix.copy()))
            
            # 保存数据（示例保存逻辑）
            save_data_frame(
                frame_count,
                camera_manager.rgb_queue,
                camera_manager.depth_queue,
                camera_manager.pose_queue
            )
            
            frame_count += 1
            if frame_limit > 0 and frame_count > frame_limit:
                break
            
    except KeyboardInterrupt:
        print("数据采集终止")

def save_data_frame(frame_id, rgb_q, depth_q, pose_q):
    """保存单帧数据"""
    os.makedirs(f'sustech/seq-01', exist_ok=True)
    os.makedirs(f'sustech/test', exist_ok=True)

    # 保存RGB图像
    if not rgb_q.empty():
        rgb = rgb_q.get()
        cv2.imwrite(f'sustech/seq-01/frame-{frame_id}.color.png', rgb)
        cv2.imwrite(f'sustech/test/frame-{frame_id}.color.png', rgb)
    
    # 保存深度图像
    if not depth_q.empty():
        depth = depth_q.get()
        depth_color_converter = carla.ColorConverter.LogarithmicDepth
        depth.save_to_disk(f'sustech/seq-01/frame-{frame_id}.depth.png', depth_color_converter)
    
    # 保存位姿矩阵
    if not pose_q.empty():
        pose = pose_q.get()
        np.savetxt(f'sustech/seq-01/frame-{frame_id}.pose.txt', np.c_[pose],fmt='%.7e',delimiter='\t')


# ======================
# 6. 采集场景初始化
# ======================

if __name__ == '__main__':
    # map_name = 'SUSTech_COE_ParkingLot'
    # map_name = 'Town01'
    map_name = 'Town05'
    client, world = setup_carla(map_name)
    
    # 设置自车
    ego_vehicle = spawn_ego_vehicle(world)
    
    # 加载其他车辆
    actors, vehicles = sustech_coe_parkinglot_enhancement.create_vehicles(client)
    
    # 初始化传感器系统
    camera_manager = CameraManager(ego_vehicle, world)
    
    # 启动主循环
    main_loop(client, world, ego_vehicle, camera_manager, 272)
