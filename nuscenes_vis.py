from nuscenes.nuscenes import NuScenes
import numpy as np
from pyquaternion import Quaternion

demo_id = 6

# 4 5

nusc = NuScenes(version=f'v1.0-demo_{demo_id}', dataroot=f'/home/CARLA-Dataset/temp/v1.0-demo_{demo_id}', verbose=True)
# nusc = NuScenes(version='v1.0-trainval', dataroot='/media/suayu/9e2b2e70-4f6e-44da-8e70-f1dd7a0057f31/nuscenes_carla/nuscenes', verbose=True)
# nusc = NuScenes(version='v1.0-trainval', dataroot='/media/suayu/9e2b2e70-4f6e-44da-8e70-f1dd7a0057f31/nuscenes', verbose=True)


# 检查数据库中的场景
# nusc.list_scenes()

# nuscenes_carla:
# (7500000, {'token': '16184d27684845738389b5d72e48a3b4', 'log_token': '557cc1ce387e436cb17d4db5a09a27a0', 'name': 'v1.0-demo_58', 
#            'description': 'UNKNOWN', 'nbr_samples': 100, 'first_sample_token': '8eaac7940e1058ee96383f09686b113a', 
#            'last_sample_token': '491a0bd2d0c24e80a53de645a2b4b6db'})
# nuscenes:
# (1531883530449377, {'token': '73030fb67d3c46cfb5e590168088ae39', 'log_token': '6b6513e6c8384cec88775cae30b78c0e', 'nbr_samples': 40, 'first_sample_token': 
#                     'e93e98b63d3b40209056d129dc53ceee', 'last_sample_token': '40e413c922184255a94f08d3c10037e0', 'name': 'scene-0001', 
#                     'description': 'Construction, maneuver between several trucks'})

# 检查第一个场景的元数据

# print("scene:",nusc.scene)
my_scene = nusc.scene[0]
# my_scene

#
first_sample_token = my_scene['first_sample_token']

# The rendering command below is commented out because it tends to crash in notebooks
# nusc.render_sample(first_sample_token)

my_sample = nusc.get('sample', first_sample_token)

# print("my_sample:first_sample:")
# my_sample

# nusc.list_sample(my_sample['token'])

#
# print("my_sample['data']:",)
data = nusc.get('sample_data', my_sample['data']['CAM_FRONT'])
# print("first_sample_token:",first_sample_token," ",data)
data = nusc.get('ego_pose', data['ego_pose_token'])
# print("ego_pose:",data)
rot = data['rotation']
q1 = Quaternion([rot[0], rot[1], rot[2], rot[3]])
print("q1:",q1)
print("yaw_pitch_roll:",q1.yaw_pitch_roll," yaw:",np.rad2deg(q1.yaw_pitch_roll[0]))

# 
sensor = 'CAM_FRONT'
cam_front_data = nusc.get('sample_data', my_sample['data'][sensor])
# print(f"my_sample['data']['{sensor}']:",cam_front_data)

nusc.render_sample_data(cam_front_data['token'], out_path="_front.jpg", use_flat_vehicle_coordinates=False)

sensor = 'CAM_BACK'
cam_back_data = nusc.get('sample_data', my_sample['data'][sensor])
# print(f"my_sample['data']['{sensor}']:",cam_back_data)

nusc.render_sample_data(cam_back_data['token'], out_path="_back.jpg", use_flat_vehicle_coordinates=False)

sensor = 'CAM_FRONT_LEFT'
cam_front_left_data = nusc.get('sample_data', my_sample['data'][sensor])
# print(f"my_sample['data']['{sensor}']:",cam_front_left_data)

nusc.render_sample_data(cam_front_left_data['token'], out_path="_front_left.jpg", use_flat_vehicle_coordinates=False)

sensor = 'CAM_FRONT_RIGHT'
cam_front_right_data = nusc.get('sample_data', my_sample['data'][sensor])
# print(f"my_sample['data']['{sensor}']:",cam_front_right_data)

nusc.render_sample_data(cam_front_right_data['token'], out_path="_front_right.jpg", use_flat_vehicle_coordinates=False)

sensor = 'CAM_BACK_LEFT'
cam_back_left_data = nusc.get('sample_data', my_sample['data'][sensor])
# print(f"my_sample['data']['{sensor}']:",cam_back_left_data)

nusc.render_sample_data(cam_back_left_data['token'], out_path="_back_left.jpg", use_flat_vehicle_coordinates=False)

sensor = 'CAM_BACK_RIGHT'
cam_back_right_data = nusc.get('sample_data', my_sample['data'][sensor])
# print(f"my_sample['data']['{sensor}']:",cam_back_right_data)

nusc.render_sample_data(cam_back_right_data['token'], out_path="_back_right.jpg", use_flat_vehicle_coordinates=False)

#
my_annotation_token = my_sample['anns'][0]
my_annotation_metadata =  nusc.get('sample_annotation', my_annotation_token)
# print("my_annotation_metadata:",my_annotation_metadata)
# my_annotation_metadata

# print("nusc.render_annotation(my_annotation_token):",my_annotation_token)
nusc.render_annotation(my_annotation_token)

# #
# # print("my_instance:",nusc.instance[0])
my_instance = nusc.instance[-1]
my_instance

instance_token = my_instance['token']
nusc.render_instance(instance_token)

# print("First annotated sample of this instance:",my_instance['first_annotation_token'])
nusc.render_annotation(my_instance['first_annotation_token'], out_path="_INS_FIRST.jpg")

# print("Last annotated sample of this instance:",my_instance['last_annotation_token'])
nusc.render_annotation(my_instance['last_annotation_token'], out_path="_INS_LAST.jpg")

# nusc.list_categories()

# nusc.category[9]

# nusc.list_attributes()

# my_instance = nusc.instance[0]
# first_token = my_instance['first_annotation_token']
# last_token = my_instance['last_annotation_token']
# nbr_samples = my_instance['nbr_annotations']
# current_token = first_token

# i = 0
# found_change = False
# while current_token != last_token:
#     current_ann = nusc.get('sample_annotation', current_token)
#     current_attr = nusc.get('attribute', current_ann['attribute_tokens'][0])['name']
    
#     if i == 0:
#         pass
#     elif current_attr != last_attr:
#         print("Changed from `{}` to `{}` at timestamp {} out of {} annotated timestamps".format(last_attr, current_attr, i, nbr_samples))
#         found_change = True

#     next_token = current_ann['next']
#     current_token = next_token
#     last_attr = current_attr
#     i += 1

# #
# my_sample = nusc.sample[10]
# nusc.render_pointcloud_in_image(my_sample['token'], pointsensor_channel='LIDAR_TOP')

# nusc.render_pointcloud_in_image(my_sample['token'], pointsensor_channel='LIDAR_TOP', render_intensity=True)

# my_sample = nusc.sample[20]

# # The rendering command below is commented out because it may crash in notebooks
# # nusc.render_sample(my_sample['token'])

# nusc.render_sample_data(my_sample['data']['CAM_FRONT'])
