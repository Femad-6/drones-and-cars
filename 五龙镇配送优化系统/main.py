#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
五龙镇配送优化系统 - 主程序入口
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from delivery_optimizer import DeliveryOptimizationSystem, run_optimization_pipeline
except ImportError:
    # 如果导入失败，尝试添加当前目录到路径
    sys.path.insert(0, str(Path(__file__).parent))
    from src.delivery_optimizer import DeliveryOptimizationSystem, run_optimization_pipeline


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """设置日志配置"""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"无效的日志级别: {log_level}")

    # 配置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)

    # 文件处理器（如果指定）
    file_handler = None
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)

    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # 清除现有处理器
    root_logger.handlers.clear()

    # 添加处理器
    root_logger.addHandler(console_handler)
    if file_handler:
        root_logger.addHandler(file_handler)

    return root_logger


def create_argument_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description='五龙镇配送优化系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py                                    # 使用默认配置运行
  python main.py -c config/my_config.json          # 使用自定义配置文件
  python main.py -o results/                       # 指定输出目录
  python main.py -v DEBUG                          # 设置调试日志级别
  python main.py --help                            # 显示帮助信息
        """
    )

    parser.add_argument(
        '-c', '--config',
        type=str,
        help='配置文件路径'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default='output',
        help='输出目录路径 (默认: output)'
    )

    parser.add_argument(
        '-v', '--verbose',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='日志级别 (默认: INFO)'
    )

    parser.add_argument(
        '--log-file',
        type=str,
        help='日志文件路径'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='五龙镇配送优化系统 v1.0.0'
    )

    return parser


def print_welcome_message():
    """打印欢迎信息"""
    print("=" * 60)
    print("        五龙镇配送优化系统        ")
    print("    车辆-无人机协同配送路径优化    ")
    print("=" * 60)
    print("系统版本: 1.0.0")
    print("开发单位: 配送优化研究团队")
    print("技术支持: 基于遗传算法的智能优化")
    print("=" * 60)


def print_completion_message(success: bool, output_dir: str):
    """打印完成信息"""
    print("\n" + "=" * 60)
    if success:
        print("✅ 优化流程执行完成！")
        print(f"📁 结果已保存到目录: {output_dir}")
        print("\n生成的文件包括:")
        print("  - 配送网络路径图")
        print("  - 成本构成分析图")
        print("  - 配送时间分布图")
        print("  - 优化历史曲线图")
        print("  - 需求分布分析图")
        print("  - 详细结果报告 (JSON)")
    else:
        print("❌ 优化流程执行失败！")
        print("请检查日志信息获取详细错误原因")
    print("=" * 60)


def main():
    """主函数"""
    # 解析命令行参数
    parser = create_argument_parser()
    args = parser.parse_args()

    # 设置日志
    setup_logging(args.verbose, args.log_file)

    # 打印欢迎信息
    print_welcome_message()

    # 创建输出目录
    output_path = Path(args.output)
    output_path.mkdir(exist_ok=True)

    # 设置日志文件（如果未指定）
    if not args.log_file:
        log_file = output_path / "system.log"
        # 重新设置日志以包含文件输出
        setup_logging(args.verbose, str(log_file))

    logger = logging.getLogger(__name__)
    logger.info("开始执行五龙镇配送优化系统")
    logger.info(f"输出目录: {args.output}")
    logger.info(f"配置文件: {args.config if args.config else '使用默认配置'}")

    try:
        # 运行优化流程
        success = run_optimization_pipeline(args.config, args.output)

        # 打印完成信息
        print_completion_message(success, args.output)

        # 返回退出码
        return 0 if success else 1

    except KeyboardInterrupt:
        logger.info("用户中断执行")
        print("\n⚠️  执行被用户中断")
        return 1
    except Exception as e:
        logger.error(f"程序执行出错: {e}", exc_info=True)
        print(f"\n❌ 程序执行出错: {e}")
        print("请查看日志文件获取详细信息")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
