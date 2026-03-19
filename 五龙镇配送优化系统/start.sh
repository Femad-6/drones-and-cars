#!/bin/bash
# 五龙镇配送优化系统 - Linux/Mac启动脚本
# 此脚本用于在Linux或macOS系统上快速启动系统

echo "================================================"
echo "    五龙镇配送优化系统"
echo "    车辆-无人机协同配送路径优化"
echo "================================================"

# 检查Python是否安装
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ 错误: 未找到Python环境"
    echo "请确保已安装Python 3.8或更高版本"
    echo "安装命令: sudo apt install python3 python3-pip  (Ubuntu/Debian)"
    echo "          brew install python3                 (macOS)"
    exit 1
fi

# 使用python3或python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

# 检查Python版本
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oP '\d+\.\d+')
if [[ $(echo "$PYTHON_VERSION < 3.8" | bc -l) -eq 1 ]]; then
    echo "❌ 错误: Python版本过低 ($PYTHON_VERSION)"
    echo "需要Python 3.8或更高版本"
    exit 1
fi

# 检查依赖文件
if [ ! -f "requirements.txt" ]; then
    echo "❌ 错误: 找不到requirements.txt文件"
    echo "请确保在正确的目录中运行此脚本"
    exit 1
fi

# 安装依赖（如果需要）
echo "📦 检查依赖包..."
$PYTHON_CMD -m pip install -r requirements.txt --quiet

# 创建输出目录
if [ ! -d "output" ]; then
    mkdir -p output
fi

# 运行系统
echo "🚀 启动五龙镇配送优化系统..."
$PYTHON_CMD main.py "$@"

echo ""
echo "================================================"
echo "系统运行完成！"
echo "请查看 output/ 目录中的结果文件"
echo "================================================"
