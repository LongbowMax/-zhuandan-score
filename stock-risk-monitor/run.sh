#!/bin/bash
# A股风险预警系统 - Linux/Mac 启动脚本

echo ""
echo "============================================"
echo "   山鬼之锤 - A股风险预警系统"
echo "============================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python3，请先安装"
    exit 1
fi

# 检查依赖
echo "[1/3] 检查依赖..."
if ! python3 -c "import tushare" 2>/dev/null; then
    echo "  正在安装依赖..."
    pip3 install -r requirements.txt
fi

# 运行检查
echo ""
echo "[2/3] 启动风险检查..."
echo ""
cd "$(dirname "$0")"
python3 main.py

echo ""
echo "[3/3] 检查完成"
echo ""
