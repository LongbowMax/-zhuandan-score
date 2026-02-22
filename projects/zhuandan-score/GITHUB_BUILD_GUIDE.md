# GitHub Actions 自动构建指南

## 方案B：云端自动构建（无需安装Android Studio）

### 第1步：创建GitHub仓库

1. 访问 https://github.com/new
2. 仓库名称填写：`zhuandan-score`
3. 选择 **Public**（公开）或 **Private**（私有）
4. 不要勾选 "Initialize this repository with a README"
5. 点击 **Create repository**

### 第2步：推送代码到GitHub

在命令行中执行以下命令：

```bash
cd projects/zhuandan-score

# 添加远程仓库（将YOUR_USERNAME替换为你的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/zhuandan-score.git

# 推送代码
git push -u origin master
```

如果提示输入用户名密码：
- 用户名：你的GitHub用户名
- 密码：**不是登录密码**，需要创建 Personal Access Token
  - 访问 https://github.com/settings/tokens
  - 点击 "Generate new token (classic)"
  - 勾选 `repo` 权限
  - 生成后复制token作为密码

### 第3步：触发自动构建

推送完成后，GitHub会自动开始构建：

1. 打开你的仓库页面 `https://github.com/YOUR_USERNAME/zhuandan-score`
2. 点击顶部的 **Actions** 标签
3. 你会看到 "Build Android APK" 工作流正在运行
4. 等待约 3-5 分钟，构建完成

### 第4步：下载APK文件

构建完成后：

1. 在Actions页面点击最新的一次运行
2. 滚动到底部，看到 **Artifacts** 区域
3. 下载：
   - `app-debug` → 调试版本（推荐测试用）
   - `app-release` → 发布版本（推荐分享用）
4. 解压下载的zip文件，得到 `.apk` 文件
5. 发送到手机安装即可

### 第5步：后续更新（修改代码后）

每次修改代码后，只需：

```bash
cd projects/zhuandan-score
git add .
git commit -m "描述你的修改"
git push
```

推送后GitHub会自动重新构建，你只需去Actions页面下载新的APK。

### 手动触发构建

如果不想推送代码就想重新构建：

1. 打开仓库的 Actions 页面
2. 点击左侧的 "Build Android APK"
3. 点击右侧的 "Run workflow" 按钮
4. 选择分支，点击 "Run workflow"

---

## 常见问题

**Q: 构建失败怎么办？**
A: 点击失败的构建记录，查看日志，通常是依赖问题或配置错误。

**Q: 可以自动发布到Release吗？**
A: 可以，需要配置额外的 workflow，需要时可以添加。

**Q: 别人能下载我的APK吗？**
A: 如果仓库是Public，任何人都能看到Actions构建的APK。如果是Private，只有你能看到。

---

## 需要帮助？

如果遇到问题，随时问我！
