# -*- coding: utf-8 -*-
"""
五龙镇配送优化系统
车辆-无人机协同配送路径优化系统

主要模块:
- config: 配置管理
- data: 数据处理
- algorithms: 优化算法
- visualization: 可视化工具
- utils: 工具函数
"""

__version__ = "1.0.0"
__author__ = "配送优化研究团队"
__description__ = "基于车辆-无人机协同配送的县域农村电商物流优化系统"

from .delivery_optimizer import DeliveryOptimizationSystem, run_optimization_pipeline
from .config import get_config_manager, get_config
from .data import DataLoader
from .algorithms import create_vehicle_drone_optimizer
from .visualization import DeliveryVisualizer
from .utils import FuzzyEvaluator, GeographicCalculator

__all__ = [
    # 主要类
    'DeliveryOptimizationSystem',

    # 配置管理
    'get_config_manager',
    'get_config',

    # 数据处理
    'DataLoader',

    # 算法
    'create_vehicle_drone_optimizer',

    # 可视化
    'DeliveryVisualizer',

    # 工具
    'FuzzyEvaluator',
    'GeographicCalculator',

    # 便捷函数
    'run_optimization_pipeline'
]
