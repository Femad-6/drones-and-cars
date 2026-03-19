#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
五龙镇配送优化系统 - Web应用启动脚本
"""

import subprocess
import sys
import os
import socket
from pathlib import Path


def is_port_available(port: int, host: str = "localhost") -> bool:
    """检查端口是否可用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.3)
        return sock.connect_ex((host, port)) != 0


def find_available_port(start_port: int = 8501, host: str = "localhost", max_tries: int = 30) -> int:
    """从起始端口开始查找可用端口"""
    for i in range(max_tries):
        port = start_port + i
        if is_port_available(port, host):
            return port
    raise RuntimeError(f"在 {start_port}-{start_port + max_tries - 1} 范围内未找到可用端口")

def check_requirements():
    """检查依赖包是否安装"""
    required_packages = [
        'streamlit',
        'plotly',
        'pandas',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def start_webapp():
    """启动Web应用"""
    project_dir = Path(__file__).parent
    webapp_file = project_dir / "webapp.py"
    
    if not webapp_file.exists():
        print(f"❌ 找不到Web应用文件: {webapp_file}")
        return
    
    host = "localhost"
    preferred_port = 8501

    try:
        port = find_available_port(preferred_port, host)
    except RuntimeError as e:
        print(f"❌ 端口检查失败: {e}")
        return

    if port != preferred_port:
        print(f"⚠️ 端口 {preferred_port} 已占用，自动切换到 {port}")

    print("🚀 启动五龙镇配送优化系统Web应用...")
    print("📱 应用将在浏览器中自动打开")
    print(f"🔗 如果没有自动打开，请访问: http://{host}:{port}")
    print("⏹️  按 Ctrl+C 停止应用")
    print("=" * 60)
    
    try:
        # 启动Streamlit应用
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(webapp_file),
            f"--server.port={port}",
            f"--server.address={host}",
            "--server.maxUploadSize=50",
            "--browser.gatherUsageStats=false",
            "--theme.primaryColor=#FF6B6B"
        ], cwd=str(project_dir))
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("💡 提示：如果出现端口占用错误，请尝试关闭其他Streamlit应用")

def main():
    """主函数"""
    print("=" * 60)
    print("🚚 五龙镇配送优化系统 - Web应用启动器")
    print("=" * 60)
    
    # 检查依赖
    if not check_requirements():
        return
    
    print("✅ 依赖检查通过")
    
    # 启动应用
    start_webapp()

if __name__ == "__main__":
    main()
