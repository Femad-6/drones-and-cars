# -*- coding: utf-8 -*-
"""
五龙镇配送优化系统 - 地理计算工具
包含距离计算、路径规划等地理相关功能
"""

import math
import numpy as np
from typing import Dict, List, Tuple, Optional
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


class GeographicCalculator:
    """地理计算器类"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def haversine_distance(self, lat1: float, lon1: float,
                          lat2: float, lon2: float) -> float:
        """
        计算两点间的哈弗辛距离（球面距离）

        Args:
            lat1, lon1: 起点经纬度
            lat2, lon2: 终点经纬度

        Returns:
            距离（公里）
        """
        R = 6371.0  # 地球半径（公里）

        # 转换为弧度
        lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
        lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = (math.sin(dlat/2)**2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return R * c

    def calculate_distance_matrix(self, locations: Dict[str, Tuple[float, float]]) -> np.ndarray:
        """
        计算距离矩阵

        Args:
            locations: 地点名称 -> (纬度, 经度)

        Returns:
            距离矩阵
        """
        names = list(locations.keys())
        n = len(names)
        matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if i == j:
                    matrix[i, j] = 0.0
                else:
                    lat1, lon1 = locations[names[i]]
                    lat2, lon2 = locations[names[j]]
                    matrix[i, j] = self.haversine_distance(lat1, lon1, lat2, lon2)

        return matrix

    def estimate_road_distance(self, air_distance: float,
                              road_factor: float = 1.2) -> float:
        """
        估算道路距离（基于直线距离）

        Args:
            air_distance: 直线距离
            road_factor: 道路系数（通常>1）

        Returns:
            估算的道路距离
        """
        return air_distance * road_factor

    def calculate_route_distance(self, route: List[str],
                               locations: Dict[str, Tuple[float, float]],
                               distance_matrix: Optional[np.ndarray] = None) -> float:
        """
        计算路径总距离

        Args:
            route: 路径节点列表
            locations: 地点坐标
            distance_matrix: 预计算的距离矩阵（可选）

        Returns:
            路径总距离
        """
        if len(route) < 2:
            return 0.0

        total_distance = 0.0

        for i in range(len(route) - 1):
            start, end = route[i], route[i + 1]

            if distance_matrix is not None:
                # 使用距离矩阵
                names = list(locations.keys())
                if start in names and end in names:
                    idx1, idx2 = names.index(start), names.index(end)
                    total_distance += distance_matrix[idx1, idx2]
                else:
                    # 回退到实时计算
                    lat1, lon1 = locations[start]
                    lat2, lon2 = locations[end]
                    total_distance += self.haversine_distance(lat1, lon1, lat2, lon2)
            else:
                # 实时计算
                lat1, lon1 = locations[start]
                lat2, lon2 = locations[end]
                total_distance += self.haversine_distance(lat1, lon1, lat2, lon2)

        return total_distance

    def find_nearest_location(self, target: Tuple[float, float],
                            locations: Dict[str, Tuple[float, float]]) -> str:
        """
        找到最近的地点

        Args:
            target: 目标点坐标（纬度, 经度）
            locations: 候选地点字典

        Returns:
            最近地点的名称
        """
        if not locations:
            raise ValueError("候选地点不能为空")

        target_lat, target_lon = target
        min_distance = float('inf')
        nearest_location = None

        for name, (lat, lon) in locations.items():
            distance = self.haversine_distance(target_lat, target_lon, lat, lon)
            if distance < min_distance:
                min_distance = distance
                nearest_location = name

        return nearest_location

    def calculate_centroid(self, locations: Dict[str, Tuple[float, float]]) -> Tuple[float, float]:
        """
        计算地理中心点

        Args:
            locations: 地点坐标字典

        Returns:
            中心点坐标（纬度, 经度）
        """
        if not locations:
            raise ValueError("地点列表不能为空")

        total_lat = sum(lat for lat, _ in locations.values())
        total_lon = sum(lon for _, lon in locations.values())

        n = len(locations)
        return (total_lat / n, total_lon / n)

    def is_within_range(self, point1: Tuple[float, float],
                       point2: Tuple[float, float],
                       max_distance: float) -> bool:
        """
        检查两点间距离是否在范围内

        Args:
            point1, point2: 两点坐标
            max_distance: 最大距离

        Returns:
            是否在范围内
        """
        distance = self.haversine_distance(point1[0], point1[1], point2[0], point2[1])
        return distance <= max_distance

    def calculate_coverage_area(self, center: Tuple[float, float],
                              radius: float, num_points: int = 36) -> List[Tuple[float, float]]:
        """
        计算覆盖区域的边界点

        Args:
            center: 中心点坐标
            radius: 半径（公里）
            num_points: 边界点数量

        Returns:
            边界点坐标列表
        """
        center_lat, center_lon = center
        boundary_points = []

        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            # 近似计算边界点（简单方法）
            delta_lat = (radius / 111.0) * math.cos(angle)  # 纬度变化
            delta_lon = (radius / (111.0 * math.cos(math.radians(center_lat)))) * math.sin(angle)  # 经度变化

            point_lat = center_lat + delta_lat
            point_lon = center_lon + delta_lon
            boundary_points.append((point_lat, point_lon))

        return boundary_points

    def optimize_route_order(self, locations: List[str],
                           distance_matrix: np.ndarray) -> List[str]:
        """
        简单的路径优化（最近邻算法）

        Args:
            locations: 地点名称列表
            distance_matrix: 距离矩阵

        Returns:
            优化后的路径
        """
        if len(locations) <= 1:
            return locations

        names = list(get_config('locations', {}).keys())
        indices = [names.index(loc) for loc in locations if loc in names]

        if not indices:
            return locations

        # 最近邻算法
        optimized = [locations[0]]
        remaining = locations[1:]

        while remaining:
            last_idx = names.index(optimized[-1])
            min_distance = float('inf')
            next_location = None

            for loc in remaining:
                if loc in names:
                    idx = names.index(loc)
                    distance = distance_matrix[last_idx, idx]
                    if distance < min_distance:
                        min_distance = distance
                        next_location = loc

            if next_location:
                optimized.append(next_location)
                remaining.remove(next_location)
            else:
                # 如果找不到，随机选择
                optimized.extend(remaining)
                break

        return optimized


# 便捷函数
def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """便捷的距离计算函数"""
    calc = GeographicCalculator()
    return calc.haversine_distance(lat1, lon1, lat2, lon2)

def calculate_distance_matrix(locations: Dict[str, Tuple[float, float]]) -> np.ndarray:
    """便捷的距离矩阵计算函数"""
    calc = GeographicCalculator()
    return calc.calculate_distance_matrix(locations)

def calculate_route_distance(route: List[str],
                           locations: Dict[str, Tuple[float, float]],
                           distance_matrix: Optional[np.ndarray] = None) -> float:
    """便捷的路径距离计算函数"""
    calc = GeographicCalculator()
    return calc.calculate_route_distance(route, locations, distance_matrix)
