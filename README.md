# YahBoomCar ROS 工作区 (YahBoomCar ROS Workspace)

## 概述 (Overview)

这是一个完整的 ROS（机器人操作系统）工作区，包含 15 个 ROS 包，用于控制和操作 YahBoomCar 移动机器人。

**仓库地址**: https://github.com/zlxxxw/yahboomcar_ws

## 项目结构 (Project Structure)

### 包列表 (Packages)

```
src/
├── yahboomcar_astra/          # Astra 相机驱动
├── yahboomcar_autodrive/      # 自动驾驶模块
├── yahboomcar_bringup/        # 启动文件
├── yahboomcar_ctrl/           # 控制模块
├── yahboomcar_description/    # 机器人描述
├── yahboomcar_gazebo/         # Gazebo 仿真
├── yahboomcar_laser/          # 激光雷达驱动
├── yahboomcar_linefollw/      # 循迹模块
├── yahboomcar_mediapipe/      # MediaPipe 视觉处理
├── yahboomcar_msgs/           # 自定义消息
├── yahboomcar_multi/          # 多机器人
├── yahboomcar_nav/            # 导航模块
├── yahboomcar_slam/           # SLAM 模块
├── yahboomcar_visual/         # 视觉处理
├── yahboomcar_voice_ctrl/     # 语音控制
├── yahboomcar_yolov4_tiny/    # YOLOv4 Tiny 目标检测
└── yahboomcar_yolov5/         # YOLOv5 目标检测
```

## 快速开始 (Quick Start)

### 1. 克隆仓库

```bash
git clone https://github.com/zlxxxw/yahboomcar_ws.git
cd yahboomcar_ws
```

### 2. 初始化 ROS 环境

```bash
# 设置 ROS 环境变量
source /opt/ros/<your_distro>/setup.bash

# 安装依赖
rosdep install --from-paths src --ignore-src -r -y

# 构建项目
catkin build
# 或使用 catkin_make
# catkin_make
```

### 3. 设置环境

```bash
# 添加到 bashrc（可选）
echo "source ~/yahboomcar_ws/devel/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

## 大文件处理 (Large Files Handling)

本项目包含一些超过 100MB 的大文件。由于 GitHub 的限制，这些文件通过以下方式处理：

### 大文件列表

| 文件路径 | 大小 | 用途 |
|---------|------|------|
| `src/yahboomcar_slam/param/ORBvoc.txt` | 138.52 MB | ORB-SLAM 词汇表 |
| `src/yahboomcar_slam/resultPointCloudFile.pcd` | 178.46 MB | 3D 点云地图文件 |
| `src/yahboomcar_mediapipe/scripts/file/shape_predictor_68_face_landmarks.dat` | 95.08 MB | 人脸关键点检测模型 |
| `src/yahboomcar_visual/detection/frozen_inference_graph.pb` | 66.46 MB | TensorFlow 目标检测模型 |

### 获取大文件的方式

#### 方式 1：从 GitHub Releases 下载（推荐）

1. 访问 [Releases 页面](https://github.com/zlxxxw/yahboomcar_ws/releases)
2. 下载最新版本的大文件压缩包
3. 解压到项目根目录
4. 文件会自动进入正确的目录结构

#### 方式 2：手动下载并放置

如果 Releases 中还未发布，可以从以下目录手动复制：

```bash
# 确保以下目录存在
mkdir -p src/yahboomcar_slam/param/
mkdir -p src/yahboomcar_slam/
mkdir -p src/yahboomcar_mediapipe/scripts/file/
mkdir -p src/yahboomcar_visual/detection/

# 然后将文件放入相应目录
```

#### 方式 3：使用数据分支（Git LFS）

如果你已安装 Git LFS：

```bash
# 安装 Git LFS（如果未安装）
# macOS: brew install git-lfs
# Ubuntu: apt-get install git-lfs
# Windows: 从 https://git-lfs.github.com 下载

# 检查 data/large-files 分支
git checkout data/large-files
git lfs pull
```

## 系统要求 (System Requirements)

- **OS**: Ubuntu 18.04 LTS 或更新版本（推荐）
- **ROS**: ROS Melodic 或更新版本
- **Python**: Python 3.6+
- **CUDA**: 9.0+ (可选，用于 GPU 加速)
- **内存**: 至少 4GB RAM
- **磁盘空间**: 至少 2GB（包含所有大文件）

## 依赖项 (Dependencies)

主要依赖包括：

- ROS core packages
- OpenCV
- TensorFlow / PyTorch
- MediaPipe
- PCL (Point Cloud Library)
- ORB-SLAM
- YOLOv4 / YOLOv5

## 构建与运行 (Build & Run)

### 构建

```bash
# 使用 catkin build（推荐）
catkin build

# 或使用 catkin_make
catkin_make
```

### 运行示例

```bash
# 启动主节点
roslaunch yahboomcar_bringup yahboomcar_start.launch

# 启动视觉处理
roslaunch yahboomcar_visual visual.launch

# 启动 SLAM
roslaunch yahboomcar_slam slam.launch

# 启动导航
roslaunch yahboomcar_nav navigation.launch
```

## 分支说明 (Branches)

- **main**: 主分支，包含所有源代码（已清理大文件）
- **clean-start**: 干净的起始分支
- **data/large-files**: 包含大文件的 Git LFS 分支（需要 LFS 支持）

## 许可证 (License)

请查看项目根目录的 LICENSE 文件。

## 故障排除 (Troubleshooting)

### 问题 1: 缺少大文件

**症状**: 运行时提示文件不存在

**解决方案**:
1. 检查是否从 Releases 下载了大文件
2. 确认文件在正确的目录
3. 验证文件名和路径

### 问题 2: ROS 环境未配置

**症状**: `roslaunch: command not found`

**解决方案**:
```bash
source /opt/ros/<your_distro>/setup.bash
```

### 问题 3: 构建失败

**症状**: `catkin build` 失败

**解决方案**:
```bash
# 清理构建文件
rm -rf build/ devel/

# 重新构建
catkin build
```

## 文档 (Documentation)

详细的大文件处理说明请查看 [LARGE_FILES_GUIDE.md](./LARGE_FILES_GUIDE.md)

## 联系方式 (Contact)

如有问题，请在 GitHub 上提交 Issue 或 Pull Request。

## 更新日志 (Changelog)

### v1.0 (2026-05-12)
- ✅ 初始化仓库
- ✅ 上传所有源代码（~310 MB）
- ✅ 配置大文件处理方案
- ✅ 编写完整文档

---

**最后更新**: 2026-05-12
