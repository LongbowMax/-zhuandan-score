#!/bin/bash
# 生成签名密钥脚本

KEYSTORE_FILE="release.keystore"
KEY_ALIAS="zhuandan"
KEYSTORE_PASSWORD="zhuandan123"
KEY_PASSWORD="zhuandan123"

# 检查是否已存在
if [ -f "$KEYSTORE_FILE" ]; then
    echo "密钥库文件已存在: $KEYSTORE_FILE"
    echo "如需重新生成，请先删除该文件"
    exit 1
fi

# 生成密钥库
echo "正在生成签名密钥..."
keytool -genkey -v \
    -keystore "$KEYSTORE_FILE" \
    -alias "$KEY_ALIAS" \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000 \
    -storepass "$KEYSTORE_PASSWORD" \
    -keypass "$KEY_PASSWORD" \
    -dname "CN=ZhuanDan Score, OU=App, O=Developer, L=Local, ST=State, C=CN"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 签名密钥生成成功！"
    echo ""
    echo "📄 文件: $KEYSTORE_FILE"
    echo "🔑 密钥别名: $KEY_ALIAS"
    echo "🔒 密钥库密码: $KEYSTORE_PASSWORD"
    echo "🔒 密钥密码: $KEY_PASSWORD"
    echo ""
    echo "⚠️  请妥善保管这些信息！"
    echo ""
    echo "下一步：将密钥配置到 GitHub Secrets"
    echo "1. 将 $KEYSTORE_FILE 转换为 base64:"
    echo "   base64 -w 0 $KEYSTORE_FILE"
    echo ""
    echo "2. 在 GitHub 仓库设置中添加以下 Secrets:"
    echo "   - KEYSTORE_BASE64: (base64 编码的密钥库内容)"
    echo "   - KEYSTORE_PASSWORD: $KEYSTORE_PASSWORD"
    echo "   - KEY_ALIAS: $KEY_ALIAS"
    echo "   - KEY_PASSWORD: $KEY_PASSWORD"
else
    echo "❌ 生成失败"
    exit 1
fi
