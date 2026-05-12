# 🚀 快速上传步骤 (Quick Release Upload Steps)

## 你已完成的工作 ✅

- ✅ 源代码已上传到 GitHub main 分支 (~310 MB)
- ✅ v1.0 标签已创建和推送
- ✅ 完整的文档已编写

## 📦 接下来：创建并发布 Release

### 🟢 推荐方法：使用 GitHub CLI（最简单）

#### 第 1 步：安装 GitHub CLI

**Windows (PowerShell)**:
```powershell
winget install GitHub.cli
```

**验证安装**:
```bash
gh --version
```

#### 第 2 步：认证到 GitHub

```bash
gh auth login
# 按照提示操作
```

#### 第 3 步：一键创建 Release 并上传文件

```bash
# 进入项目目录
cd C:\Users\dell\Desktop\新建文件夹\GSE\yahboomcar_ws

# 创建 Release 并上传 4 个大文件
gh release create v1.0 \
  --title "YahBoomCar Large Files - v1.0" \
  --notes "包含所有大于100MB的数据文件。

📋 文件清单：
- ORBvoc.txt (138.52 MB) - ORB-SLAM词汇表
- resultPointCloudFile.pcd (178.46 MB) - 3D点云地图  
- shape_predictor_68_face_landmarks.dat (95.08 MB) - 人脸检测模型
- frozen_inference_graph.pb (66.46 MB) - 目标检测模型

📖 详见 RELEASES_GUIDE.md" \
  src/yahboomcar_slam/param/ORBvoc.txt \
  src/yahboomcar_slam/resultPointCloudFile.pcd \
  src/yahboomcar_mediapipe/scripts/file/shape_predictor_68_face_landmarks.dat \
  src/yahboomcar_visual/detection/frozen_inference_graph.pb
```

✨ **完成！** Release 将在 ~2 分钟内显示在:
🔗 https://github.com/zlxxxw/yahboomcar_ws/releases

---

### 🔵 替代方法：网页界面（不需要工具）

如果你更喜欢使用网页：

1. 打开: https://github.com/zlxxxw/yahboomcar_ws/releases
2. 点击 "Draft a new release"
3. 选择标签: `v1.0`
4. 标题: "YahBoomCar Large Files - v1.0"
5. 描述: （见下方）
6. 拖拽上传 4 个文件
7. 点击 "Publish release"

**发布描述内容**:
```markdown
## 📦 YahBoomCar Large Files Release

包含所有超过 GitHub 100MB 文件大小限制的文件。

### 📋 包含文件

| 文件 | 大小 | 用途 |
|------|------|------|
| ORBvoc.txt | 138.52 MB | ORB-SLAM 词汇表 |
| resultPointCloudFile.pcd | 178.46 MB | 3D 点云地图 |
| shape_predictor_68_face_landmarks.dat | 95.08 MB | 人脸检测模型 |
| frozen_inference_graph.pb | 66.46 MB | TensorFlow 目标检测 |

### 🚀 使用方法

1. 下载此 Release 中的文件
2. 解压到项目根目录
3. 文件将自动进入正确的目录结构
4. 现在可以构建和运行项目

### 📖 更多信息

- 详见 [RELEASES_GUIDE.md](https://github.com/zlxxxw/yahboomcar_ws/blob/main/RELEASES_GUIDE.md)
- 源代码: [main 分支](https://github.com/zlxxxw/yahboomcar_ws/tree/main)
- 问题/反馈: [Issues](https://github.com/zlxxxw/yahboomcar_ws/issues)
```

---

## ✨ 完成后的验证

发布完成后，验证以下项目：

```bash
# 检查 Release 是否可见
curl -s https://api.github.com/repos/zlxxxw/yahboomcar_ws/releases/latest | jq '.tag_name, .assets | length'
# 应该输出: "v1.0" 和 4 (4 个文件)

# 或直接访问
https://github.com/zlxxxw/yahboomcar_ws/releases/tag/v1.0
```

---

## 📝 发布后的文件整理

发布完后，为了保持 git 仓库干净，可以从本地工作区删除这些大文件：

```bash
# 删除本地工作区的大文件（已发布到 Release）
rm src/yahboomcar_slam/param/ORBvoc.txt
rm src/yahboomcar_slam/resultPointCloudFile.pcd
rm src/yahboomcar_mediapipe/scripts/file/shape_predictor_68_face_landmarks.dat
rm src/yahboomcar_visual/detection/frozen_inference_graph.pb

# 确认 .gitignore 包含这些文件（防止重新提交）
git status  # 应该显示 nothing to commit
```

---

## 🎯 总结清单

- [ ] GitHub CLI 已安装
- [ ] 已认证到 GitHub
- [ ] Release v1.0 已创建
- [ ] 4 个文件已上传到 Release
- [ ] Release 已发布
- [ ] 可以在网页上看到 Release 和文件
- [ ] 下载文件测试（可选）

---

## 📚 相关文档

- [README.md](./README.md) - 项目概述
- [LARGE_FILES_GUIDE.md](./LARGE_FILES_GUIDE.md) - 大文件处理完整指南
- [RELEASES_GUIDE.md](./RELEASES_GUIDE.md) - Release 创建详细步骤

---

**需要帮助?** 提交 Issue: https://github.com/zlxxxw/yahboomcar_ws/issues
