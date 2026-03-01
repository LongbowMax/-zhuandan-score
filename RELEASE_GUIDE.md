# 转蛋计分助手 - 发布指南

## 📦 快速获取 APK

每次推送代码到 GitHub 后，Actions 会自动构建签名 APK。

**下载地址：** https://github.com/LongbowMax/-zhuandan-score/actions

1. 点击最新的 workflow run
2. 在 Artifacts 部分下载 "转蛋计分助手-v1.0.0"
3. 解压得到已签名的 APK 文件

---

## 🔐 配置签名密钥（可选）

如果你想自己配置签名密钥，请按以下步骤操作：

### 步骤1：生成签名密钥

**Windows:**
```cmd
generate-keystore.bat
```

**Mac/Linux:**
```bash
chmod +x generate-keystore.sh
./generate-keystore.sh
```

这将生成 `release.keystore` 文件，并显示密码信息。

### 步骤2：转换为 Base64

**Windows:**
```cmd
certutil -encode release.keystore temp.b64 && findstr /v /c:- temp.b64 > keystore.b64 && del temp.b64
type keystore.b64
```

**Mac/Linux:**
```bash
base64 -w 0 release.keystore
```

### 步骤3：配置 GitHub Secrets

1. 打开 GitHub 仓库页面
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**，依次添加：

| Secret 名称 | 值 |
|------------|-----|
| `KEYSTORE_BASE64` | Base64 编码的密钥库内容 |
| `KEYSTORE_PASSWORD` | zhuandan123 |
| `KEY_ALIAS` | zhuandan |
| `KEY_PASSWORD` | zhuandan123 |

### 步骤4：重新构建

推送任意代码更改触发新的构建，或手动触发 Actions。

---

## 📱 安装说明

1. 下载 APK 文件
2. 在 Android 手机上允许"安装未知来源应用"：
   - 设置 → 安全 → 未知来源 → 允许
3. 点击 APK 文件安装

---

## 🚀 应用功能

- ✅ 支持多玩家管理
- ✅ 每局选择4人上台
- ✅ 自动排名分配
- ✅ 自动家族配对
- ✅ 支持炸和天王炸计分
- ✅ 历史记录查看
- ✅ 结算统计

---

## 📝 版本历史

### v1.0.0
- 首次发布
- 支持4人以上轮换
- 完整的计分功能

---

**开发者：** 鬼哥  
**开源协议：** MIT
