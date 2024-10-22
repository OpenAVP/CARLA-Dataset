import logging
import time
import argparse

from packages.carla1s import CarlaContext, ManualExecutor, PassiveExecutor
from packages.carla1s.actors import Vehicle, RgbCamera, DepthCamera, SemanticLidar
from packages.carla1s.tf import Transform

from src.semantic_kitti import SemanticKittiDumper


def main(*, 
         fps: int = 20, 
         map: str = 'Town01', 
         output: str = './temp/', 
         host: str = 'localhost', 
         port: int = 2000,
         log_level: int = logging.DEBUG):

    with CarlaContext(host=host, port=port, log_level=log_level) as cc, ManualExecutor(cc, fixed_delta_seconds=1/fps) as exe:
        cc.reload_world(map_name=map)
        
        ego_vehicle: Vehicle = (cc.actor_factory
            .create(Vehicle, from_blueprint='vehicle.tesla.model3')
            .with_name("ego_vehicle")
            .with_transform(cc.get_spawn_point(0))
            .build())
        
        cam_0_tf = Transform(x=0.30, y=0.00, z=1.70)
        cam_1_tf = Transform(x=0.30, y=0.50, z=1.70)
        semantic_lidar_tf = Transform(x=0.00, y=0.00, z=2.80)

        cam_0_rgb: RgbCamera = (cc.actor_factory
            .create(RgbCamera)
            .with_name("cam_0_rgb")
            .with_transform(cam_0_tf)
            .with_parent(ego_vehicle)
            .build())
        cam_0_depth: DepthCamera = (cc.actor_factory
            .create(DepthCamera)
            .with_name("cam_0_depth")
            .with_transform(cam_0_tf)
            .with_parent(ego_vehicle)
            .build())
            
        cam_1_rgb: RgbCamera = (cc.actor_factory
            .create(RgbCamera)
            .with_name("cam_1_rgb")
            .with_transform(cam_1_tf)
            .with_parent(ego_vehicle)
            .build())
        cam_1_depth: DepthCamera = (cc.actor_factory
            .create(DepthCamera)
            .with_name("cam_1_depth")
            .with_transform(cam_1_tf)
            .with_parent(ego_vehicle)
            .build())
            
        semantic_lidar: SemanticLidar = (cc.actor_factory
            .create(SemanticLidar)
            .with_name("semantic_lidar")
            .with_transform(semantic_lidar_tf)
            .with_parent(ego_vehicle)
            .with_attributes(rotation_frequency=fps,
                             points_per_second=1000000,
                             channels=64,
                             range=100,
                             upper_fov=2,
                             lower_fov=-24.8,
                             )
            .build())
            
        cc.all_actors_spawn().all_sensors_listen()
        exe.wait_ticks(1)
        
        ego_vehicle.set_autopilot(True)
        exe.wait_ticks(1)
        exe.wait_sim_seconds(1)
        
        # SETUP DUMPER
        dumper = SemanticKittiDumper(output)
        dumper.bind_camera(cam_0_depth, data_folder="image_0")
        dumper.bind_camera(cam_1_depth, data_folder="image_1")
        dumper.bind_camera(cam_0_rgb, data_folder="image_2")
        dumper.bind_camera(cam_1_rgb, data_folder="image_3")
        dumper.bind_semantic_lidar(semantic_lidar, data_folder="velodyne", labels_folder="labels")
        dumper.bind_timestamp(cam_0_rgb, file_path="times.txt")
        dumper.bind_pose(cam_0_rgb, file_path="poses.txt")
        dumper.bind_calib(tr_sensor=semantic_lidar, file_path="calib.txt")

        # EXEC DUMP
        with dumper.create_sequence():
            for i in range(3):
                dumper.logger.info(f'-> FRAME: {dumper.current_frame_name} '.ljust(80, '-'))
                exe.wait_ticks(1)
                dumper.create_frame().join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--fps', type=int, default=20, help='Recommended FPS of the simulation')
    parser.add_argument('--map', type=str, default='Town01', help='Name of the map to load')
    parser.add_argument('--output', type=str, default='./temp/', help='Path to save the dataset')
    parser.add_argument('--host', type=str, default='localhost', help='Host of the Carla server')
    parser.add_argument('--port', type=int, default=2000, help='Port of the Carla server')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode, setting log level to DEBUG')
    args = parser.parse_args()
    
    log_level = logging.DEBUG if args.debug else logging.INFO
    
    try:
        main(fps=args.fps, map=args.map, output=args.output, host=args.host, port=args.port, log_level=log_level)
    except Exception:
        print(f'Exception occurred, check the log for more details.')
