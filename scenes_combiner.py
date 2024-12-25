import os
import shutil
from tqdm import tqdm

def merge_temp_directories(version, temp_dir, target_dir, required_samples, required_sweeps, required_json_files):
    """
    合并 temp 目录下的所有子目录内容到 target_dir 中。

    :param temp_dir: 源目录路径，例如 'temp'
    :param target_dir: 目标目录路径，例如 'v1.0-mini'
    :param required_samples: samples 目录下需要合并的子文件夹列表
    :param required_sweeps: sweeps 目录下需要合并的子文件夹列表
    :param scenes_id_required_files: 需要合并的 scenes_id 子目录下的 JSON 文件列表
    """
    
    # 获取 temp 目录下所有子目录
    subdirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]

    # 创建目标目录
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        os.makedirs(os.path.join(target_dir, 'maps'))

    copy_flag = True

    merged_json = {}
    for file_name in required_json_files:
        merged_json[file_name] = []
    json_dst = os.path.join(target_dir, version)
    print(json_dst)
    os.makedirs(os.path.dirname(os.path.join(json_dst, version)), exist_ok=True)

    # 初始化 tqdm 进度条
    for subdir in tqdm(subdirs, desc="Processing directories", unit="dir"):
        src_path = os.path.join(temp_dir, subdir)
        
        # 1. 复制 can_bus 目录中的所有 json 文件
        can_bus_src = os.path.join(src_path, 'can_bus')
        can_bus_dst = os.path.join(target_dir, 'can_bus')
        if not os.path.exists(can_bus_dst):
            os.makedirs(can_bus_dst)
        for file in os.listdir(can_bus_src):
            if file.endswith('.json'):
                shutil.copy(os.path.join(can_bus_src, file), can_bus_dst)

        # 2. 复制 samples 目录下的指定子文件夹内容
        samples_src = os.path.join(src_path, 'samples')
        samples_dst = os.path.join(target_dir, 'samples')
        if not os.path.exists(samples_dst):
            os.makedirs(samples_dst)
        for folder in required_samples:
            src_folder = os.path.join(samples_src, folder)
            dst_folder = os.path.join(samples_dst, folder)
            if os.path.exists(src_folder):
                if not os.path.exists(dst_folder):
                    os.makedirs(dst_folder)
                for item in os.listdir(src_folder):
                    s = os.path.join(src_folder, item)
                    d = os.path.join(dst_folder, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        shutil.copy2(s, d)
        
        # 3. 复制 sweeps 目录下的指定子文件夹内容
        sweeps_src = os.path.join(src_path, 'sweeps')
        sweeps_dst = os.path.join(target_dir, 'sweeps')
        if not os.path.exists(sweeps_dst):
            os.makedirs(sweeps_dst)
        for folder in required_sweeps:
            src_folder = os.path.join(sweeps_src, folder)
            dst_folder = os.path.join(sweeps_dst, folder)
            if os.path.exists(src_folder):
                if not os.path.exists(dst_folder):
                    os.makedirs(dst_folder)
                for item in os.listdir(src_folder):
                    s = os.path.join(src_folder, item)
                    d = os.path.join(dst_folder, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        shutil.copy2(s, d)
        
        # 4. 合并 scenes_id 子目录下的指定 JSON 文件
        if os.path.exists(src_path):
            scene_path = os.path.join(src_path, subdir)
            for file in os.listdir(scene_path): # 遍历所有 JSON 文件 
                if file.endswith('.json') and file in required_json_files:
                    with open(os.path.join(scene_path, file), 'r', encoding='utf-8') as f:
                        merged_json[file].append(json.load(f))
                        print("file len:",file," ",len(merged_json[file]))

        # 5. 把不需要合并的 JSON 文件原样拷贝到新目录下
        if copy_flag:
            for file in os.listdir(scene_path):
                if file.endswith('.json') and file not in required_json_files:
                    shutil.copy(os.path.join(scene_path, file), json_dst)
            copy_flag = False
        
    # 将合并后的 JSON 数据写入目标文件  
    for file_name in required_json_files:
        path_file_name = os.path.join(json_dst, file_name)
        merged_list = [item for sublist in merged_json[file_name] for item in sublist]
        # print("file:",path_file_name)
        with open(path_file_name, 'w', encoding='utf-8') as outfile:
            json.dump(merged_list, outfile, ensure_ascii=False, indent=4)
    # for key, value in merged_json.items():
    #     print('\n\n\n\n\n')
    #     print(key)
    #     print(merged_json[file_name])

if __name__ == "__main__":
    import json

    version = 'v1.0-mini'
    temp_directory = 'temp'
    target_directory = os.path.join(temp_directory, version)

    # 预先定义需要合并的 samples 和 sweeps 子文件夹名称
    required_samples = ['CAM_BACK', 'CAM_BACK_LEFT', 'CAM_BACK_RIGHT', 'CAM_FRONT', 'CAM_FRONT_LEFT', 'CAM_FRONT_RIGHT', 'LIDAR_TOP']
    required_sweeps = ['CAM_BACK', 'CAM_BACK_LEFT', 'CAM_BACK_RIGHT', 'CAM_FRONT', 'CAM_FRONT_LEFT', 'CAM_FRONT_RIGHT', 'LIDAR_TOP']

    # 预先定义需要合并的 scenes_id 子目录下的 JSON 文件名列表
    required_json_files = ['ego_pose.json', 
                            'instance.json', 
                            'log.json', 
                            'sample.json', 
                            'sample_annotation.json', 
                            'sample_data.json', 
                            'scene.json']

    merge_temp_directories(version, temp_directory, target_directory, required_samples, required_sweeps, required_json_files)

    print("Combine finished!")