#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
五龙镇配送优化系统 - 演示脚本
展示系统的基本功能和使用方法
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def show_system_info():
    """显示系统信息"""
    print("=" * 60)
    print("        五龙镇配送优化系统        ")
    print("    车辆-无人机协同配送路径优化    ")
    print("=" * 60)
    print("版本: 1.0.0")
    print("开发团队: 五龙镇配送优化研究团队")
    print("功能: 智能配送路径优化、成本效益分析、多模态配送")
    print("=" * 60)

def show_usage_examples():
    """显示使用示例"""
    print("\n📖 使用示例:")
    print("-" * 40)

    examples = [
        ("基本运行", "python main.py"),
        ("Web应用", "python start_webapp.py"),
        ("Windows启动", "双击 start_webapp.bat"),
        ("使用自定义配置", "python main.py -c config/example_config.json"),
        ("快速演示", "python run_example.py"),
        ("系统测试", "python test_system.py"),
        ("生成源程序文档", "python generate_source_doc.py")
    ]

    for desc, cmd in examples:
        print(f"   {desc:<15} {cmd}")

def show_features():
    """显示系统特性"""
    print("\n✨ 主要特性:")
    print("-" * 40)

    features = [
        "✅ 遗传算法优化",
        "✅ 车辆-无人机协同配送",
        "✅ 智能距离计算（百度地图API）",
        "✅ 时间约束评估",
        "✅ 成本效益分析",
        "✅ 交互式Web界面（Streamlit）",
        "✅ 数据可视化（Plotly）",
        "✅ 模糊评价系统",
        "✅ 模块化设计",
        "✅ 完整文档和用户手册"
    ]

    for feature in features:
        print(f"   {feature}")

def show_file_structure():
    """显示文件结构"""
    print("\n📁 项目结构:")
    print("-" * 40)

    structure = """
五龙镇配送优化系统/
├── src/                    # 源代码目录
│   ├── algorithms/        # 算法模块（遗传算法）
│   ├── config/            # 配置管理模块
│   ├── data/              # 数据处理模块
│   ├── utils/             # 工具模块（地图API、地理工具、模糊评价）
│   └── visualization/     # 可视化模块
├── config/                # 配置文件
├── data/                  # 数据文件（距离矩阵、需求数据）
├── output/                # 输出结果（图表、报告）
├── docs/                  # 文档
├── main.py               # 主程序
├── webapp.py             # Web应用界面
├── start_webapp.py       # Web应用启动脚本
├── start_webapp.bat      # Windows启动脚本
├── setup.py              # 安装脚本
├── requirements.txt      # 依赖包
└── README.md             # 使用说明
    """

    print(structure)

def show_quick_start():
    """显示快速开始指南"""
    print("\n🚀 快速开始:")
    print("-" * 40)

    steps = [
        "1. 确保安装Python 3.8+",
        "2. 安装依赖: pip install -r requirements.txt",
        "3. 准备数据文件（物流车配送距离.xlsx、无人机距离矩阵.xlsx等）",
        "4. 选择启动方式:",
        "   - 命令行: python main.py",
        "   - Web界面: python start_webapp.py",
        "   - Windows: 双击 start_webapp.bat",
        "5. 查看结果: output/ 目录"
    ]

    for step in steps:
        print(f"   {step}")

def show_web_app_features():
    """显示Web应用特性"""
    print("\n🌐 Web应用特性:")
    print("-" * 40)

    web_features = [
        "📊 交互式配置界面",
        "🗺️  智能距离计算（百度地图API）",
        "📈 实时优化进度显示",
        "🎯 多参数配置调整",
        "📋 结果可视化展示",
        "💾 数据导入导出",
        "📱 响应式设计，支持移动端"
    ]

    for feature in web_features:
        print(f"   {feature}")

def show_data_files():
    """显示数据文件说明"""
    print("\n📁 数据文件说明:")
    print("-" * 40)

    data_files = [
        ("物流车配送距离.xlsx", "车辆配送距离矩阵数据"),
        ("无人机距离矩阵.xlsx", "无人机配送距离数据"),
        ("车辆距离矩阵_API.xlsx", "API获取的距离数据"),
        ("测试包裹需求数据.xlsx", "测试用的需求数据"),
        ("config/*.json", "系统配置文件")
    ]

    for filename, description in data_files:
        print(f"   {filename:<25} {description}")

def show_support():
    """显示技术支持信息"""
    print("\n🆘 技术支持:")
    print("-" * 40)

    support = [
        "📚 用户手册: docs/用户手册.md",
        "🌐 Web使用指南: WEB_GUIDE.md",
        "🗺️  智能距离功能: SMART_DISTANCE_GUIDE.md",
        "🔧 功能实现总结: 功能实现总结.md",
        "📦 包裹需求编辑: 包裹需求编辑功能说明.md",
        "💡 问题反馈: 查看系统日志 output/system.log"
    ]

    for item in support:
        print(f"   {item}")

def show_recent_updates():
    """显示最近更新"""
    print("\n🆕 最近更新:")
    print("-" * 40)

    updates = [
        "✨ 新增智能距离计算功能（百度地图API集成）",
        "🌐 完整的Web应用界面（Streamlit）",
        "📊 交互式数据可视化（Plotly）",
        "🗺️  地理信息处理和路径规划",
        "📱 响应式Web界面设计",
        "🔧 模块化架构重构",
        "📋 完整的用户文档和指南"
    ]

    for update in updates:
        print(f"   {update}")

def main():
    """主函数"""
    show_system_info()
    show_features()
    show_web_app_features()
    show_file_structure()
    show_data_files()
    show_usage_examples()
    show_quick_start()
    show_recent_updates()
    show_support()

    print("\n" + "=" * 60)
    print("🎯 准备开始使用五龙镇配送优化系统了吗？")
    print("推荐使用Web界面: python start_webapp.py")
    print("或命令行模式: python main.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
