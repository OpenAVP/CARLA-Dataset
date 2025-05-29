import logging
import argparse

from packages.carla1s import CarlaContext, ManualExecutor
from packages.carla1s.actors import Vehicle, RgbCamera, SemanticLidar
from packages.carla1s.tf import Transform
from packages.carla1s.utils.waypoint import Waypoints

from src.nuscenes import NuScenesLidarsegDumper

import sustech_coe_parkinglot_enhancement

def main(*,
         fps: int = 20,
         map: str = 'SUSTech_COE_ParkingLot',
         output: str = './temp/',
         host: str = 'localhost',
         port: int = 2000,
         point_num: int = 0,
         control: str = 'auto',
         create_vehicle: bool = False,
         log_level: int = logging.DEBUG):

    with CarlaContext(host=host, port=port, log_level=log_level) as cc, ManualExecutor(cc, fixed_delta_seconds=1/fps) as exe:
        cc.reload_world(map_name=map,reset_actor_list=False)
        
        # 地图一共92个生成点
        ego_vehicle: Vehicle = (cc.actor_factory
            .create(Vehicle, from_blueprint='vehicle.tesla.model3')
            .with_name("ego_vehicle")
            .with_transform(cc.get_spawn_point(point_num))
            .build())
        if control == 'manual':
            exe.wait_sim_seconds(15)
        
        cam_front: RgbCamera = (cc.actor_factory
            .create(RgbCamera)
            .with_name("cam_f")
            .with_transform(Transform(x=1.50, y=0.00, z=2.00))
            .with_attributes(image_size_x=1600, image_size_y=900, fov=70)
            .with_parent(ego_vehicle)
            .build())
        
        cam_front_left: RgbCamera = (cc.actor_factory
            .create(RgbCamera)
            .with_name("cam_fl")
            .with_transform(Transform(x=1.50, y=-0.70, z=2.00, yaw=-55))
            .with_attributes(image_size_x=1600, image_size_y=900, fov=70)
            .with_parent(ego_vehicle)
            .build())
        
        cam_front_right: RgbCamera = (cc.actor_factory
            .create(RgbCamera)
            .with_name("cam_fr")
            .with_transform(Transform(x=1.50, y=0.70, z=2.00, yaw=55))
            .with_attributes(image_size_x=1600, image_size_y=900, fov=70)
            .with_parent(ego_vehicle)
            .build())
        
        cam_back: RgbCamera = (cc.actor_factory
            .create(RgbCamera)
            .with_name("cam_b")
            .with_transform(Transform(x=-1.50, y=0.00, z=2.00, yaw=180))
            .with_attributes(image_size_x=1600, image_size_y=900, fov=70)
            .with_parent(ego_vehicle)
            .build())
        
        cam_back_left: RgbCamera = (cc.actor_factory
            .create(RgbCamera)
            .with_name("cam_bl")
            .with_transform(Transform(x=-0.70, y=0.70, z=2.00, yaw=-110))
            .with_attributes(image_size_x=1600, image_size_y=900, fov=70)
            .with_parent(ego_vehicle)
            .build())
        
        cam_back_right: RgbCamera = (cc.actor_factory
            .create(RgbCamera)
            .with_name("cam_br")
            .with_transform(Transform(x=-0.70, y=-0.70, z=2.00, yaw=110))
            .with_attributes(image_size_x=1600, image_size_y=900, fov=70)
            .with_parent(ego_vehicle)
            .build())

        semantic_lidar: SemanticLidar = (cc.actor_factory
            .create(SemanticLidar)
            .with_name("sem_lidar")
            .with_transform(Transform(x=0.00, y=0.00, z=2.0))
            .with_parent(ego_vehicle)
            .with_attributes(rotation_frequency=fps,
                             points_per_second=140000,
                             channels=64,
                             range=80,
                             upper_fov=10,
                             lower_fov=-30,
                             )
            .build())

        cc.all_actors_spawn().all_sensors_listen()
        exe.wait_ticks(1)

        # SETUP DUMPER
        dumper = NuScenesLidarsegDumper(output, fps)
        dumper.bind_camera(cam_front, channel="CAM_FRONT")
        dumper.bind_camera(cam_front_left, channel="CAM_FRONT_LEFT")
        dumper.bind_camera(cam_front_right, channel="CAM_FRONT_RIGHT")
        dumper.bind_camera(cam_back, channel="CAM_BACK")
        dumper.bind_camera(cam_back_left, channel="CAM_BACK_LEFT")
        dumper.bind_camera(cam_back_right, channel="CAM_BACK_RIGHT")
        dumper.bind_semantic_lidar(semantic_lidar, channel="LIDAR_TOP")
        dumper.bind_vehicle(ego_vehicle)

        actors = []
        vehicles = []
        if create_vehicle:
            print("Start add vehicles...")
            actors, vehicles = sustech_coe_parkinglot_enhancement.create_vehicles(cc.client)
            print("Finish add vehicles...")

	# scene 帧数
        frame_num = 100
        if control == 'auto':
            ego_vehicle.set_autopilot(True)
        elif control == 'manual':
            dumper.logger.debug("Start manual control...")
        elif control == 'replay':
            waypoints_path = 'tf.npy'
            waypoints = Waypoints.from_file(file_path=waypoints_path, delta_seconds=1.0 / fps, forward=True, keep_last=False)
            waypoints_iter = iter(waypoints)
            ego_vehicle.set_physics(False)
            frame_num = len(waypoints)
        exe.wait_ticks(1)
        exe.wait_sim_seconds(1)

        # EXEC DUMP
        with dumper.create_sequence('v1.0-demo'):
            for i in range(frame_num):
                dumper.logger.debug(f'-> FRAME: {dumper.current_frame_name} '.ljust(80, '-'))
                if control == 'replay':
                    ego_vehicle.set_transform(next(waypoints_iter).as_carla_transform_obj())
                exe.wait_ticks(1)    
                dumper.create_frame().join()
                    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--fps', type=int, default=2, help='Recommended FPS of the simulation')
    parser.add_argument('--map', type=str, default='SUSTech_COE_ParkingLot', help='Name of the map to load')
    parser.add_argument('--output', type=str, default='./temp/', help='Path to save the dataset')
    parser.add_argument('--host', type=str, default='localhost', help='Host of the Carla server')
    parser.add_argument('--point_num', type=int, default=57, help='Spawn point of ego vehicle')
    parser.add_argument('--port', type=int, default=2000, help='Port of the Carla server')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode, setting log level to DEBUG')
    parser.add_argument('--control', type=str, default='auto', help='Way to control ego vehicle')
    parser.add_argument('--create_vehicle', type=bool, default=True, help='Way to control ego vehicle')
    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    
    try:
        main(fps=args.fps, map=args.map, output=args.output, host=args.host, port=args.port, point_num=args.point_num, control=args.control, create_vehicle=args.create_vehicle, log_level=log_level)
    except Exception:
        print(f'Exception occurred, check the log for more details.')
