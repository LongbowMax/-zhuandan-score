@echo off
chcp 65001 > nul
echo ==========================================
echo   转蛋计分助手 - 签名密钥生成工具
echo ==========================================
echo.

set KEYSTORE_FILE=release.keystore
set KEY_ALIAS=zhuandan
set KEYSTORE_PASSWORD=zhuandan123
set KEY_PASSWORD=zhuandan123

if exist %KEYSTORE_FILE% (
    echo 密钥库文件已存在: %KEYSTORE_FILE%
    echo 如需重新生成，请先删除该文件
    pause
    exit /b 1
)

echo 正在生成签名密钥...
keytool -genkey -v ^
    -keystore %KEYSTORE_FILE% ^
    -alias %KEY_ALIAS% ^
    -keyalg RSA ^
    -keysize 2048 ^
    -validity 10000 ^
    -storepass %KEYSTORE_PASSWORD% ^
    -keypass %KEY_PASSWORD% ^
    -dname "CN=ZhuanDan Score, OU=App, O=Developer, L=Local, ST=State, C=CN"

if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo   ✅ 签名密钥生成成功！
    echo ==========================================
    echo.
    echo 📄 文件: %KEYSTORE_FILE%
    echo 🔑 密钥别名: %KEY_ALIAS%
    echo 🔒 密钥库密码: %KEYSTORE_PASSWORD%
    echo 🔒 密钥密码: %KEY_PASSWORD%
    echo.
    echo ⚠️  请妥善保管这些信息！
    echo.
    echo 下一步：将密钥配置到 GitHub Secrets
    echo.
    echo 1. 将 %KEYSTORE_FILE% 转换为 base64:
    echo    certutil -encode %KEYSTORE_FILE% temp.b64 && findstr /v /c:- temp.b64 > keystore.b64 && del temp.b64
    echo.
    echo 2. 在 GitHub 仓库设置中添加以下 Secrets:
    echo    - KEYSTORE_BASE64: (keystore.b64 文件内容)
    echo    - KEYSTORE_PASSWORD: %KEYSTORE_PASSWORD%
    echo    - KEY_ALIAS: %KEY_ALIAS%
    echo    - KEY_PASSWORD: %KEY_PASSWORD%
    echo.
) else (
    echo ❌ 生成失败
    pause
    exit /b 1
)

pause
