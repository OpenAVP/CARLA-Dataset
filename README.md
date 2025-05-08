# CARLA-Dataset
[![Python Version](https://img.shields.io/badge/python-3.8.19%2B-blue)]()
[![CARLA Version](https://img.shields.io/badge/Carla-0.9.15-B3)]()

一个基于CARLA仿真环境的数据采集工具，方便快捷地生成符合nuScenes格式的自动驾驶数据集。

## 功能特性
- 🚗 自动场景载入、随机化其他交通参与者生成与自车车辆控制
- 📷 多传感器同步采集（RGB相机、LIDAR、RADAR、CANBUS）
- 🗂️ 自动生成符合nuScenes基本格式的元数据和标注文件
- ⚙️ 可调的采集参数
- 🎯 方便的路径采集与回放功能

## 安装

### 环境需求
- Ubuntu 20.04
- Python 3.8.19
- CARLA 0.9.13+

### 安装Carla仿真器
Download the specified CARLA version with SUSTC_Parkinglot Map. (BaiduCloud | GoogleDrive)
安装特定版本的带有南科大地下车库地图的Carla 0.9.13+ 。
下载链接：[Carla](http://gofile.me/6MDrn/UOvykgikS)
下载链接：[BaiduCloud](https://pan.baidu.com/share/init?surl=iLcAsa1yJSYNcisP1ymfow&pwd=b5au)

### 下载 CARLA-Dataset
```bash
# 克隆仓库
git clone https://github.com/OpenAVP/CARLA-Dataset.git -b dev
cd CARLA-Dataset

# 安装依赖
pip install -r requirements.txt
```

### 下载 carla1s
```bash
# 下载carla1s工具库
cd packages
git clone https://github.com/OpenAVP/carla1s.git -b dev@waypoint
```

## 采集 nuScenes 格式数据
启动CARLA服务器：
```bash
cd $CARLA_ROOT
./CarlaUE4.sh
```
运行nuScenes格式数据采集脚本：
```bash
python nuscenes_lidarseg.py
```
或连续采集多组自车生成点不同的单场景数据集：
```bash
bash ./collect_nuscenes.sh $START_POINT $END_POINT
```
其中，`$START_POINT`和`$END_POINT`分别为每次采集时自车在Carla仿真地图内的生成点初值和终值。脚本会遍历所有范围内的生成点，采集多组数据集。

### 数据目录结构
假设设置的采集版本号为v1.0-demo，以nuScenes格式采集的数据目录结构如下：
```
.
└── v1.0-demo
    ├── can_bus	# can_bus数据，包含自车位姿和移动数据
    │   ├── v1.0-demo_pose.json
    │   └── v1.0-demo_steeranglefeedback.json
    ├── lidarseg	# 雷达点云数据，存储每一帧的雷达点云
    │   └── v1.0-demo
    │       ├── 36b94aa4152d486692d109dae3da90ef_lidarseg.bin
    │       ├── ……
    ├── maps
    ├── nuscences.db	# nuscenes数据库文件
    ├── samples	# 存储六环视相机和激光雷达每一帧的原始数据
    │   ├── CAM_BACK
    │   │   ├── ego_vehicle-2024-11-27-23-06-14__CAM_BACK__1650000.jpg
    │   │   ├── ……
    │   ├── CAM_BACK_LEFT
    │   │   ├── ego_vehicle-2024-11-27-23-06-14__CAM_BACK_LEFT__1650000.jpg
    │   │   ├── ……
    │   ├── CAM_BACK_RIGHT
    │   │   ├── ego_vehicle-2024-11-27-23-06-14__CAM_BACK_RIGHT__1650000.jpg
    │   │   ├── ……
    │   ├── CAM_FRONT
    │   │   ├── ego_vehicle-2024-11-27-23-06-14__CAM_FRONT__1650000.jpg
    │   │   ├── ……
    │   ├── CAM_FRONT_LEFT
    │   │   ├── ego_vehicle-2024-11-27-23-06-14__CAM_FRONT_LEFT__1650000.jpg
    │   │   ├── ……
    │   ├── CAM_FRONT_RIGHT
    │   │   ├── ego_vehicle-2024-11-27-23-06-14__CAM_FRONT_RIGHT__1650000.jpg
    │   │   ├── ……
    │   └── LIDAR_TOP
    │       ├── ego_vehicle-2024-11-27-23-06-14__LIDAR_TOP__1650000.bin
    │       ├── ……
    ├── sweeps	# 未标注帧
    │   ├── CAM_BACK -> ./temp/v1.0-demo/samples/CAM_BACK
    │   ├── CAM_BACK_LEFT -> ./temp/v1.0-demo/samples/CAM_BACK_LEFT
    │   ├── CAM_BACK_RIGHT -> ./temp/v1.0-demo/samples/CAM_BACK_RIGHT
    │   ├── CAM_FRONT -> ./temp/v1.0-demo/samples/CAM_FRONT
    │   ├── CAM_FRONT_LEFT -> ./temp/v1.0-demo/samples/CAM_FRONT_LEFT
    │   ├── CAM_FRONT_RIGHT -> ./temp/v1.0-demo/samples/CAM_FRONT_RIGHT
    │   └── LIDAR_TOP -> ./temp/v1.0-demo/samples/LIDAR_TOP
    └── v1.0-demo
        ├── attribute.json	# 描述实例属性
        ├── calibrated_sensor.json	# 传感器参数信息
        ├── category.json	# 描述目标种类
        ├── ego_pose.json	# 记录车辆位姿
        ├── instance.json	# 描述实例对象
        ├── lidarseg.json	# 记录雷达点云数据索引
        ├── log.json	# 提取数据日志文件
        ├── map.json	# 地图数据
        ├── sample_annotation.json	# 样本标注信息
        ├── sample_data.json	# 描述传感器记录的数据
        ├── sample.json	# 样本数据
        ├── scene.json	# 场景数据
        ├── sensor.json	# 描述传感器信息
        └── visibility.json	# 描述实例可见性
```
### 配置选项
在启动采集工具时输入可选参数，或修改代码以进行自定义采集设置：

可选参数：
```bash
python nuscenes_lidarseg.py \
--fps=$YOUR_FPS \	# 模拟器帧率，默认为2
--map=$YOUR_MAP \	# 加载地图的名称，默认为SUSTech_COE_ParkingLot(南科大地下车库)
--output=$YOUR_OUTPUT \	# 采集到的数据集输出目录，默认为/temp/
--host=$YOUR_HOST \	# Carla模拟器的host，默认为2000
--point_num=$YOUR_POINT_NUM \	# 自车生成点
--port=$YOUR_PORT \	# 端口,默认为2000
--debug=$YOUR_DEBUG \	# 是否启动debug模式
--control=$YOUR_CONTROL \	# 控制自车的方法 auto: 启用Carla自动驾驶 replay：启用轨迹回放
--create_vehicle=$YOUR_CREATE_VEHICLE	# 是否在地图中生成停泊着的/行驶中的车辆
```

代码中可修改的自定义设置与默认值：
```bash
frame_num = 100 # 采集帧数

```

### 轨迹记录与回放

轨迹记录：
启动脚本。按E开始记录行车轨迹，再按下E保存记录的轨迹。脚本运行过程中可以使用WSAD键控制车辆行驶。
```bash
# 启动Carla仿真器
cd Carla
./CarlaUE4.sh

# 启动手动控制脚本
cd CARLA-Dataset
python manual_control.py --save_path=$PATH
```

轨迹绘制：
启动脚本。然后可以使用鼠标在生成的鸟瞰视图上进行绘制。按键说明：
- WSAD：移动视图
- 鼠标滚轮：调整高度
- B：对绘制的轨迹进行自动平滑
- H：恢复相机高度为默认值
- Y：保存偏航角数据
- C：保存当前轨迹数据
- P：清空轨迹
- E：Carla仿真器内启动小车沿绘制的轨迹行驶
默认保存的文件名为tf.npy。

```bash
# 启动Carla仿真器
cd Carla
./CarlaUE4.sh

# 启动轨迹绘制脚本
python draw_line_class.py
```

轨迹重放：
将轨迹文件（默认读取的文件名为tf.npy）复制到CARLA-Dataset根目录，然后启动采集工具。车辆会按照保存的轨迹行驶。
```bash
python nuscenes_lidarseg.py --control=replay
```

### 场景合并
启动脚本，自动合并给定目录（默认为/temp/）下的单场景数据集文件，生成近似多场景数据集。生成的数据集目录名默认为nuscenes。
```bash
python scenes_combiner.py
```
场景合并后，需要修改`$CARLA_ROOT/envs/$ENV_NAME/lib/python3.8/site-packages/nuscenes/utils/splits.py`数据集分组文件，以使当前分组与场景文件匹配。

## 采集 KITTI 格式数据

启动CARLA服务器：
```bash
cd ${CARLA_ROOT}
./CarlaUE4.sh 
```
运行采集脚本：
```bash
python semantic_kitti.py
```

### 数据目录结构
以KITTI格式采集的数据目录结构如下：
```
.
├── calib.txt	# 相机参数
├── image_0	# image_0和image_1目录存储深度相机数据
│   ├── 000001.png
│   ├── ……
├── image_1
│   ├── 000001.png
│   ├── ……
├── image_2	# image_2和image_3目录存储RGB相机数据
│   ├── 000001.png
│   ├── ……
├── image_3
│   ├── 000001.png
│   ├── ……
├── labels	# 雷达点云语义
│   ├── 000001.label
│   ├── ……
├── poses.txt	# 车辆位姿
├── times.txt	# 时间戳
└── velodyne	# 雷达点云
    ├── 000001.bin
    ├── ……

```

### 配置选项

采集可选参数：
```bash
python semantic_kitti.py \
--fps=$YOUR_FPS \	# 模拟器帧率，默认为20
--map=$YOUR_MAP \	# 加载地图的名称，默认为Town01
--output=$YOUR_OUTPUT \	# 采集到的数据集输出目录，默认为/temp/
--host=$YOUR_HOST \	# Carla模拟器的host，默认为2000
--port=$YOUR_PORT \	# 端口,默认为2000
--debug=$YOUR_DEBUG \	# 是否启动debug模式
```

## CARLA-Dataset 代码目录
```
CARLA-Dataset
    ├── nuscenes_lidarseg.py	# nuScenes格式数据采集脚本
    ├── packages	# 工具库目录
    │   └── carla1s	# 封装原生Carla对象并提供采集工具使用的接口
    │       ├── actors	# 封装Actor类
    │       ├── context.py
    │       ├── errors
    │       ├── executors
    │       ├── generate_registry.py
    │       ├── __init__.py
    │       ├── __pycache__
    │       ├── README.md
    │       ├── registry
    │       ├── requirements.txt
    │       ├── tf	# 封装Transform类
    │       └── utils	# 封装Waypoints类
    ├── README.md
    ├── requirements.txt
    ├── scenes_combiner.py	# nuScenes格式数据场景合并工具
    ├── semantic_kitti.py	# KITTI格式数据采集脚本
    ├── src
    │   ├── dataset_dumper.py	# 管理数据存储与线程池
    │   ├── nuscenes
    │   │   ├── __init__.py
    │   │   ├── nuscences_db.py	# 管理nuScenes数据库
    │   │   └── nuscences_lidarseg_dumper.py	# 管理传感器数据并将数据库内容生成为nuScenes格式数据集
    │   └── semantic_kitti
    │       ├── __init__.py
    │       └── semantic_kitti_dumper.py	# 管理传感器数据并将数据库内容生成为KITTI格式数据集
    └── temp
```

## 数据格式说明
生成的数据库遵循基本的nuScenes或KITTI数据标准。完整格式规范请参考nuScenes数据集和KITTI数据集官方文档。

在Carla仿真器内采集到的原始数据统一转换为ndarray格式进行处理。中间数据格式如下：

- RGB相机：
```
shape:(height,width,3)
```
数据格式:（B、G、R）
Carla原数据包含A通道，已去除。

- Lidar：
```
shape:(点云点数,4)
```
数据格式：(x、y、z、intensity)

- Semantic Lidar：
```
shape:(点云点数,4)
```
数据格式：
(x、y、z、语义标记(unsigned int))

- Radar：
```
shape:(点云点数,4)
```
数据格式：
```
(相对速度、方位角（弧度）、高度角（弧度）、距离（米）)
```

- BoundingBox：
```
shape:(9,)
```
数据格式：
```
(x,y,z,pitch,yaw,roll,extend_x,extend_y,extend_z)
```
坐标系基于Carla世界坐标系。

- transform：
```
shape:(帧数,10)
```
数据格式：
```
(x、y、z、pitch、yaw、roll、frame、elapsed_seconds、delta_seconds、platform_timestamp)
```
frame：模拟器启动以来经过帧数
elapsed_seconds：仿真经过秒数
delta_seconds：从上一帧开始经过秒数
platform_timestamp：以秒为单位给出测量帧的寄存器
上一帧的elapsed_seconds+这一帧的delta_seconds=这一帧的elapsed_seconds

## 更新记录
v1.0.0 完成所有基本功能

v1.0.1 2025.5.8 修复instance和sample_annotation的数据错误 
