# -*- coding: utf-8 -*-
"""
五龙镇配送优化系统 - 模糊评估工具
包含时间约束评估、效益评估等模糊逻辑函数
"""

import math
from typing import Dict, List, Optional
import logging

try:
    from ..config import get_config
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys
    import os
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)
    try:
        from config import get_config
    except ImportError:
        # 最后尝试
        sys.path.insert(0, current_dir)
        from config import get_config


class FuzzyEvaluator:
    """模糊评估器类"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.weights = get_config('fuzzy_weights', {
            'T_avg_weight': 0.444,
            'T_max_weight': 0.084,
            'R_high_weight': 0.472
        })

    def T_avg(self, x: float) -> float:
        """
        平均配送时间隶属度函数

        Args:
            x: 平均配送时间（小时）

        Returns:
            隶属度值 ∈ [0,1]
        """
        if 0 <= x and x <= 1:
            return 1.0
        elif 1 < x and x <= 1.5:
            return (1.5 - x) / 0.5
        else:
            return 0.0

    def T_max(self, x: float) -> float:
        """
        最大配送时间隶属度函数

        Args:
            x: 最大配送时间（小时）

        Returns:
            隶属度值 ∈ [0,1]
        """
        if 0 <= x and x <= 1.5:
            return 1.0
        elif 1.5 < x and x <= 2:
            return (2 - x) / 0.5
        else:
            return 0.0

    def R_high(self, x: float) -> float:
        """
        高比例配送准时率隶属度函数

        Args:
            x: 准时配送比例 ∈ [0,1]

        Returns:
            隶属度值 ∈ [0,1]
        """
        if 0 <= x and x <= 0.5:
            return 0.0
        elif 0.5 < x and x <= 0.9:
            return (x - 0.5) / 0.4
        else:
            return 1.0

    def evaluate_time_constraint(self, delivery_times: Dict[str, float],
                                time_tag: Optional[float] = None) -> float:
        """
        评估时间约束的可行性（模糊评价值）

        Args:
            delivery_times: 村庄名称 -> 配送时间(小时)
            time_tag: 时间阈值，如果为None则使用配置中的值

        Returns:
            模糊评估值 m ∈ [0,1]
        """
        if not delivery_times:
            return 1.0

        if time_tag is None:
            time_tag = get_config('time_constraints.time_tag', 2.0)

        # 计算统计指标
        t_avg = sum(delivery_times.values()) / len(delivery_times)  # 平均配送时间
        t_max = max(delivery_times.values())  # 最大配送时间
        t_m = sum(1 for time in delivery_times.values() if time < time_tag) / len(delivery_times)

        # 模糊逻辑评估
        m = (self.weights['T_avg_weight'] * self.T_avg(t_avg) +
             self.weights['T_max_weight'] * self.T_max(t_max) +
             self.weights['R_high_weight'] * self.R_high(t_m))

        return max(0.0, min(1.0, m))

    def evaluate_efficiency(self, distance: float, demand: float,
                          method: str = 'vehicle') -> float:
        """
        评估配送效率

        Args:
            distance: 配送距离（km）
            demand: 需求量
            method: 配送方式 ('vehicle' 或 'drone')

        Returns:
            效率评分
        """
        base_efficiency = demand / distance

        if method == 'drone':
            # 无人机效率更高（直线距离，速度快）
            return base_efficiency * 1.2
        else:
            return base_efficiency

    def evaluate_cost_effectiveness(self, cost: float, service_level: float) -> float:
        """
        评估成本效益比

        Args:
            cost: 总成本
            service_level: 服务水平评分 ∈ [0,1]

        Returns:
            成本效益评分
        """
        if cost <= 0:
            return 0.0

        # 简单的成本效益模型：服务水平/成本
        return service_level / cost

    def classify_delivery_urgency(self, distance: float, demand: float) -> str:
        """
        根据距离和需求分类配送紧急程度

        Args:
            distance: 距离（km）
            demand: 需求量

        Returns:
            紧急程度分类：'high', 'medium', 'low'
        """
        # 简单的分类规则
        if distance > 15 and demand < 20:
            return 'low'  # 适合无人机
        elif distance < 5 and demand > 30:
            return 'high'  # 需要优先处理
        else:
            return 'medium'

    def calculate_service_satisfaction(self, delivery_times: Dict[str, float],
                                     demands: Dict[str, float]) -> float:
        """
        计算服务满意度

        Args:
            delivery_times: 配送时间字典
            demands: 需求量字典

        Returns:
            满意度评分 ∈ [0,1]
        """
        if not delivery_times or not demands:
            return 0.0

        total_weighted_satisfaction = 0.0
        total_weight = 0.0

        time_tag = get_config('time_constraints.time_tag', 2.0)

        for village, time in delivery_times.items():
            demand = demands.get(village, 1.0)

            # 时间满意度
            if time <= time_tag * 0.8:  # 很准时
                time_satisfaction = 1.0
            elif time <= time_tag:  # 准时
                time_satisfaction = 0.8
            elif time <= time_tag * 1.2:  # 稍晚
                time_satisfaction = 0.6
            else:  # 很晚
                time_satisfaction = 0.3

            total_weighted_satisfaction += time_satisfaction * demand
            total_weight += demand

        if total_weight == 0:
            return 0.0

        return total_weighted_satisfaction / total_weight


# 便捷函数
def evaluate_time_constraint(delivery_times: Dict[str, float],
                           time_tag: Optional[float] = None) -> float:
    """便捷的时间约束评估函数"""
    evaluator = FuzzyEvaluator()
    return evaluator.evaluate_time_constraint(delivery_times, time_tag)

def evaluate_efficiency(distance: float, demand: float, method: str = 'vehicle') -> float:
    """便捷的效率评估函数"""
    evaluator = FuzzyEvaluator()
    return evaluator.evaluate_efficiency(distance, demand, method)

def calculate_service_satisfaction(delivery_times: Dict[str, float],
                                 demands: Dict[str, float]) -> float:
    """便捷的服务满意度计算函数"""
    evaluator = FuzzyEvaluator()
    return evaluator.calculate_service_satisfaction(delivery_times, demands)
