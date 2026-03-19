@echo off
REM 五龙镇配送优化系统 - Windows启动脚本
REM 此脚本用于在Windows系统上快速启动系统

echo ================================================
echo     五龙镇配送优化系统
echo     车辆-无人机协同配送路径优化
echo ================================================

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python环境
    echo 请确保已安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/
    pause
    exit /b 1
)

REM 检查依赖是否安装
if not exist "requirements.txt" (
    echo ❌ 错误: 找不到requirements.txt文件
    echo 请确保在正确的目录中运行此脚本
    pause
    exit /b 1
)

REM 安装依赖（如果需要）
echo 📦 检查依赖包...
pip install -r requirements.txt --quiet

REM 创建输出目录
if not exist "output" (
    mkdir output
)

REM 运行系统
echo 🚀 启动五龙镇配送优化系统...
python main.py %*

REM 保持窗口打开以查看结果
echo.
echo ================================================
echo 系统运行完成！
echo 请查看 output/ 目录中的结果文件
echo ================================================
pause
