# GitHub Releases 上传指南

## 快速指南 (Quick Start)

### 方法 1：使用 GitHub CLI（推荐）

#### 1. 安装 GitHub CLI

**Windows**:
```powershell
winget install GitHub.cli
```

**macOS**:
```bash
brew install gh
```

**Ubuntu/Debian**:
```bash
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
sudo apt update
sudo apt install gh
```

#### 2. 认证

```bash
gh auth login
# 选择 GitHub.com
# 选择 HTTPS
# 选择 Y 使用 git credential manager
```

#### 3. 创建 Release 并上传文件

```bash
# 创建标签
git tag -a v1.0 -m "Release v1.0 - Large files and documentation"
git push origin v1.0

# 创建 Release 并上传文件
cd /path/to/yahboomcar_ws

gh release create v1.0 \
  --title "YahBoomCar Large Files - v1.0" \
  --notes "包含所有大于100MB的数据文件" \
  src/yahboomcar_slam/param/ORBvoc.txt \
  src/yahboomcar_slam/resultPointCloudFile.pcd \
  src/yahboomcar_mediapipe/scripts/file/shape_predictor_68_face_landmarks.dat \
  src/yahboomcar_visual/detection/frozen_inference_graph.pb
```

### 方法 2：网页界面上传（不需要任何工具）

#### 1. 访问 Releases 页面

打开: https://github.com/zlxxxw/yahboomcar_ws/releases

#### 2. 创建新 Release

- 点击 "Draft a new release"
- 填写版本号: `v1.0`
- 添加标题: "YahBoomCar Large Files - v1.0"
- 添加描述:

```markdown
包含所有超过GitHub大小限制的文件：

- ORBvoc.txt (138.52 MB) - ORB-SLAM 词汇表
- resultPointCloudFile.pcd (178.46 MB) - 3D 点云地图
- shape_predictor_68_face_landmarks.dat (95.08 MB) - 人脸检测模型
- frozen_inference_graph.pb (66.46 MB) - 目标检测模型

## 使用方法

1. 下载本 Release 中的文件
2. 解压到项目根目录
3. 文件将自动进入正确的目录结构
```

#### 3. 上传文件

- 拖拽或点击选择以下文件:
  1. `src/yahboomcar_slam/param/ORBvoc.txt`
  2. `src/yahboomcar_slam/resultPointCloudFile.pcd`
  3. `src/yahboomcar_mediapipe/scripts/file/shape_predictor_68_face_landmarks.dat`
  4. `src/yahboomcar_visual/detection/frozen_inference_graph.pb`

- 点击 "Publish release"

### 方法 3：创建压缩包后上传

```bash
# 创建压缩包
cd yahboomcar_ws
tar czf yahboomcar_large_files_v1.0.tar.gz \
  src/yahboomcar_slam/param/ORBvoc.txt \
  src/yahboomcar_slam/resultPointCloudFile.pcd \
  src/yahboomcar_mediapipe/scripts/file/shape_predictor_68_face_landmarks.dat \
  src/yahboomcar_visual/detection/frozen_inference_graph.pb

# 然后上传 yahboomcar_large_files_v1.0.tar.gz 到 Release
```

## Release 发布后的步骤

### 更新 README

在项目根目录的 `README.md` 中添加:

```markdown
## 下载大文件

大文件已发布到 Releases，请访问:

🔗 [GitHub Releases - v1.0](https://github.com/zlxxxw/yahboomcar_ws/releases/tag/v1.0)

### 快速下载和安装

```bash
# 下载最新 Release
# 解压文件到项目根目录

# 验证文件位置
ls src/yahboomcar_slam/param/ORBvoc.txt
ls src/yahboomcar_slam/resultPointCloudFile.pcd
```
```

### 更新 .gitignore

确保这些大文件不会再次被提交到 git:

```
# 大文件 - 已通过 Releases 发布
src/yahboomcar_slam/param/ORBvoc.txt
src/yahboomcar_slam/resultPointCloudFile.pcd
src/yahboomcar_mediapipe/scripts/file/shape_predictor_68_face_landmarks.dat
src/yahboomcar_visual/detection/frozen_inference_graph.pb
```

## 验证清单

- [ ] Release 已创建并发布
- [ ] 所有 4 个文件已上传
- [ ] Release 描述已完善
- [ ] README 已更新下载链接
- [ ] .gitignore 已更新
- [ ] main 分支不包含大文件（在 .gitignore 中）

## 使用者安装指南

给想使用该项目的人提供:

```markdown
### 获取完整项目

1. 克隆仓库:
   git clone https://github.com/zlxxxw/yahboomcar_ws.git
   cd yahboomcar_ws

2. 下载大文件:
   - 访问 Releases: https://github.com/zlxxxw/yahboomcar_ws/releases
   - 下载最新版本的文件
   - 解压到项目根目录

3. 构建项目:
   source /opt/ros/<distro>/setup.bash
   catkin build
```

## 常见问题 (FAQ)

### Q: 为什么大文件不在 GitHub 上?
A: GitHub 对单文件有 100MB 的硬限制，这些文件超过此限制。通过 Releases 分发是官方推荐的做法。

### Q: 文件会一直保存在 Releases 上吗?
A: 是的，Release 文件会永久保存，就像源代码一样。

### Q: 可以从 git clone 直接获取这些文件吗?
A: 不能直接 clone。必须从 Releases 单独下载。

### Q: 如何从 Releases 以编程方式下载文件?
A: 使用 GitHub API:

```bash
# 获取最新 Release
curl -s https://api.github.com/repos/zlxxxw/yahboomcar_ws/releases/latest | jq '.assets[].browser_download_url'

# 下载单个文件
wget https://github.com/zlxxxw/yahboomcar_ws/releases/download/v1.0/ORBvoc.txt
```

---

**需要帮助?** 提交 Issue: https://github.com/zlxxxw/yahboomcar_ws/issues
