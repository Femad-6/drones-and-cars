# -*- coding: utf-8 -*-
"""
五龙镇配送优化系统 - 配置模块
"""

from .config_manager import ConfigManager, get_config_manager, get_config, set_config

__all__ = [
    'ConfigManager',
    'get_config_manager',
    'get_config',
    'set_config'
]
