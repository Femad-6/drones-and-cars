# -*- coding: utf-8 -*-
"""
五龙镇配送优化系统 - 数据处理模块
"""

from .data_loader import (
    DataLoader,
    load_vehicle_distance_matrix,
    load_excel_data,
    validate_data_consistency
)

__all__ = [
    'DataLoader',
    'load_vehicle_distance_matrix',
    'load_excel_data',
    'validate_data_consistency'
]
