#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
车辆-无人机协同配送优化模型快速运行脚本
"""

import os
import sys
import subprocess

def print_banner():
    """打印欢迎横幅"""
    print("=" * 60)
    print("    车辆-无人机协同配送路径优化模型")
    print("=" * 60)
    print("基于遗传算法的五龙镇26个村庄快递配送优化")
    print("=" * 60)

def check_dependencies():
    """检查依赖库"""
    print("检查依赖库...")
    required_packages = ['numpy', 'pandas', 'matplotlib', 'seaborn']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n缺少以下依赖库: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print("pip install -r requirements.txt")
        return False
    
    print("所有依赖库已安装！\n")
    return True

def run_test():
    """运行测试脚本"""
    print("运行模型测试...")
    try:
        result = subprocess.run([sys.executable, 'test_model.py'], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✓ 测试通过")
            return True
        else:
            print("✗ 测试失败")
            print("错误信息:", result.stderr)
            return False
    except Exception as e:
        print(f"✗ 测试出错: {e}")
        return False

def show_menu():
    """显示菜单"""
    print("\n请选择要运行的模型:")
    print("1. 简化版模型 (快速测试)")
    print("2. 遗传算法优化器 (推荐)")
    print("3. 完整版模型 (详细分析)")
    print("4. 运行测试")
    print("5. 查看帮助")
    print("0. 退出")
    print("-" * 40)

def run_model(model_file):
    """运行指定的模型"""
    print(f"\n正在运行 {model_file}...")
    print("请稍候，优化过程可能需要几分钟...")
    
    try:
        result = subprocess.run([sys.executable, model_file], 
                              capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("✓ 模型运行成功！")
            print("\n输出文件:")
            
            # 检查生成的文件
            output_files = []
            for file in os.listdir('.'):
                if file.endswith(('.png', '.xlsx')) and 'test' not in file:
                    output_files.append(file)
            
            if output_files:
                for file in output_files:
                    print(f"  - {file}")
            else:
                print("  - 未找到输出文件")
                
        else:
            print("✗ 模型运行失败")
            print("错误信息:", result.stderr)
            
    except subprocess.TimeoutExpired:
        print("✗ 模型运行超时")
    except Exception as e:
        print(f"✗ 运行出错: {e}")

def show_help():
    """显示帮助信息"""
    print("\n" + "=" * 60)
    print("帮助信息")
    print("=" * 60)
    print("""
模型说明:
1. 简化版模型 (code_2.py)
   - 基于距离的简单分配策略
   - 快速测试和演示
   - 运行时间: 1-2分钟

2. 遗传算法优化器 (genetic_algorithm_optimizer.py)
   - 完整的遗传算法实现
   - 2-opt路径优化
   - 详细的收敛分析
   - 运行时间: 5-10分钟

3. 完整版模型 (code_1.py)
   - 最完整的优化模型
   - 包含所有约束条件
   - 详细的结果分析
   - 运行时间: 10-15分钟

输出文件:
- *.png: 可视化结果图
- *.xlsx: 详细的配送方案和成本分析

参数设置:
- 车辆数量: 3辆
- 车辆容量: 1000kg
- 无人机载重: 80kg
- 总包裹数: 3123件
- 优化目标: 最小化总成本

注意事项:
- 确保有足够的内存和磁盘空间
- 首次运行可能需要较长时间
- 结果可能因随机种子不同而略有差异
""")

def main():
    """主函数"""
    print_banner()
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 运行测试
    if not run_test():
        print("建议先解决测试问题再运行优化模型")
    
    while True:
        show_menu()
        
        try:
            choice = input("请输入选择 (0-5): ").strip()
            
            if choice == '0':
                print("感谢使用！")
                break
            elif choice == '1':
                run_model('code_2.py')
            elif choice == '2':
                run_model('genetic_algorithm_optimizer.py')
            elif choice == '3':
                run_model('code_1.py')
            elif choice == '4':
                run_test()
            elif choice == '5':
                show_help()
            else:
                print("无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"发生错误: {e}")
        
        input("\n按回车键继续...")

if __name__ == "__main__":
    main()
