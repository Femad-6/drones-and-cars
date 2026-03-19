# -*- coding: utf-8 -*-
"""
五龙镇配送优化系统 - 配置管理器
负责配置文件的加载、验证和管理
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

from .default_config import *


class ConfigManager:
    """配置管理器类"""

    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置管理器

        Args:
            config_file: 用户配置文件路径，如果为None则使用默认配置
        """
        self.config_file = config_file
        self.config = {}
        self.logger = logging.getLogger(__name__)
        self._load_config()

    def _load_config(self):
        """加载配置"""
        # 首先加载默认配置
        self.config = self._get_default_config()

        # 如果指定了用户配置文件，则加载并合并
        if self.config_file and os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                self._merge_config(user_config)
                self.logger.info(f"成功加载用户配置文件: {self.config_file}")
            except Exception as e:
                self.logger.error(f"加载用户配置文件失败: {e}")
                self.logger.info("使用默认配置")

        # 验证配置
        self._validate_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'system_info': SYSTEM_INFO,
            'locations': LOCATIONS,
            'demands_piece': DEMANDS_PIECE,
            'cargo_details': CARGO_DETAILS,
            'upstream_packages': UPSTREAM_PACKAGES,
            'recyclables': RECYCLABLES,
            'wulong_transfer_station': WULONG_TRANSFER_STATION,
            'vehicle_params': VEHICLE_PARAMS,
            'drone_params': DRONE_PARAMS,
            'time_constraints': TIME_CONSTRAINTS,
            'subsidy_policy': SUBSIDY_POLICY,
            'integrated_params': INTEGRATED_PARAMS,
            'ga_params': GA_PARAMS,
            'target_procurement': TARGET_PROCUREMENT,
            'fuzzy_weights': FUZZY_WEIGHTS,
            'file_paths': FILE_PATHS,
            'visualization_params': VISUALIZATION_PARAMS
        }

    def _merge_config(self, user_config: Dict[str, Any]):
        """递归合并用户配置到默认配置"""
        def merge_dict(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
            return base

        self.config = merge_dict(self.config, user_config)

    def _validate_config(self):
        """验证配置的有效性"""
        # 检查必需的参数
        required_keys = [
            'locations', 'vehicle_params', 'drone_params',
            'time_constraints', 'ga_params'
        ]

        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"缺少必需的配置项: {key}")

        # 验证车辆参数
        vp = self.config['vehicle_params']
        if vp['num_vehicles'] <= 0:
            raise ValueError("车辆数量必须大于0")

        # 验证无人机参数
        dp = self.config['drone_params']
        if dp['max_payload'] <= 0:
            raise ValueError("无人机最大载荷必须大于0")

        # 验证时间约束
        tc = self.config['time_constraints']
        if tc['time_tag'] <= 0:
            raise ValueError("时间阈值必须大于0")

        self.logger.info("配置验证通过")

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项

        Args:
            key: 配置键，支持点分隔的嵌套键，如 'vehicle_params.speed'
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config

        try:
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any):
        """
        设置配置项

        Args:
            key: 配置键，支持点分隔的嵌套键
            value: 配置值
        """
        keys = key.split('.')
        config = self.config

        # 创建嵌套字典结构
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save_config(self, file_path: str):
        """
        保存当前配置到文件

        Args:
            file_path: 保存路径
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"配置已保存到: {file_path}")
        except Exception as e:
            self.logger.error(f"保存配置文件失败: {e}")

    def reload_config(self):
        """重新加载配置"""
        self._load_config()
        self.logger.info("配置已重新加载")

    def get_all_config(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.config.copy()

    def print_config_summary(self):
        """打印配置摘要"""
        print("=" * 60)
        print("五龙镇配送优化系统 - 配置摘要")
        print("=" * 60)

        print(f"系统版本: {self.get('system_info.version')}")
        print(f"车辆数量: {self.get('vehicle_params.num_vehicles')}")
        print(f"无人机最大载荷: {self.get('drone_params.max_payload')} kg")
        print(f"时间阈值: {self.get('time_constraints.time_tag')} 小时")
        print(f"GA种群大小: {self.get('ga_params.population_size')}")
        print(f"GA迭代代数: {self.get('ga_params.generations')}")

        print("\n配送中心位置:", self.get('locations.配送中心'))
        print("五龙镇位置:", self.get('locations.五龙镇'))

        print("\n服务村庄数量:", len(self.get('demands_piece', {})) - 1)  # 排除五龙镇本身
        print("总需求量:", sum(self.get('demands_piece', {}).values()), "件")

        print("=" * 60)


# 全局配置管理器实例
_config_manager = None

def get_config_manager(config_file: Optional[str] = None) -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_file)
    return _config_manager

def get_config(key: str, default: Any = None) -> Any:
    """获取配置项的便捷函数"""
    return get_config_manager().get(key, default)

def set_config(key: str, value: Any):
    """设置配置项的便捷函数"""
    get_config_manager().set(key, value)
