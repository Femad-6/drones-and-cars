@echo off
chcp 65001 >nul
title 五龙镇配送优化系统 - Web应用启动器

echo.
echo ================================================================
echo           🚚 五龙镇配送优化系统 Web应用启动器 🚚
echo ================================================================
echo.

echo 📋 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python环境
    echo 请确保已安装Python 3.7或更高版本
    pause
    exit /b 1
)

echo ✅ Python环境检查通过

echo.
echo 📦 正在检查依赖包...
python start_webapp.py

echo.
echo 👋 应用已退出，按任意键关闭窗口...
pause >nul
