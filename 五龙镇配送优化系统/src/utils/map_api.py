# -*- coding: utf-8 -*-
"""
地图API模块 - 百度地图API调用
用于获取车辆实际行驶距离和路径信息
"""

import requests
import json
import time
import logging
from typing import Dict, List, Tuple, Optional, Union
import numpy as np
from math import radians, cos, sin, asin, sqrt

class BaiduMapAPI:
    """百度地图API调用类"""
    
    def __init__(self, api_key: str = None):
        """
        初始化百度地图API
        
        Args:
            api_key: 百度地图API密钥
        """
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        
        # API端点
        self.base_url = "https://api.map.baidu.com"
        self.direction_api = f"{self.base_url}/direction/v2/driving"
        self.geocoding_api = f"{self.base_url}/geocoding/v3"
        
        # 请求间隔（避免频率限制）
        self.request_interval = 0.1  # 秒
        self.last_request_time = 0
    
    def _wait_for_rate_limit(self):
        """等待请求间隔"""
        current_time = time.time()
        time_diff = current_time - self.last_request_time
        if time_diff < self.request_interval:
            time.sleep(self.request_interval - time_diff)
        self.last_request_time = time.time()
    
    def geocode_address(self, address: str, city: str = "济源市") -> Optional[Tuple[float, float]]:
        """
        地址转坐标
        
        Args:
            address: 地址描述
            city: 城市名称
            
        Returns:
            (纬度, 经度) 或 None
        """
        if not self.api_key:
            self.logger.warning("未配置百度地图API密钥，无法进行地址解析")
            return None
        
        self._wait_for_rate_limit()
        
        params = {
            'address': f"{city}{address}",
            'output': 'json',
            'ak': self.api_key,
            'city': city
        }
        
        try:
            response = requests.get(self.geocoding_api, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 0 and data.get('result'):
                location = data['result']['location']
                # 百度地图返回的是 lng, lat
                return (location['lat'], location['lng'])
            else:
                self.logger.warning(f"地址解析失败: {address}, 状态: {data.get('status')}")
                return None
                
        except Exception as e:
            self.logger.error(f"地址解析API调用失败: {e}")
            return None
    
    def get_driving_distance(self, origin: Tuple[float, float], 
                           destination: Tuple[float, float]) -> Optional[float]:
        """
        获取车辆行驶距离
        
        Args:
            origin: 起点坐标 (纬度, 经度)
            destination: 终点坐标 (纬度, 经度)
            
        Returns:
            距离（公里）或 None
        """
        if not self.api_key:
            self.logger.warning("未配置百度地图API密钥，无法获取行驶距离")
            return None
        
        self._wait_for_rate_limit()
        
        # 转换为百度地图格式 (lng,lat)
        origin_str = f"{origin[1]},{origin[0]}"
        destination_str = f"{destination[1]},{destination[0]}"
        
        params = {
            'origin': origin_str,
            'destination': destination_str,
            'output': 'json',
            'ak': self.api_key,
            'coord_type': 'wgs84'  # 使用WGS84坐标系
        }
        
        try:
            response = requests.get(self.direction_api, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 0 and data.get('result'):
                routes = data['result'].get('routes', [])
                if routes:
                    # 获取第一条路线的距离（米）
                    distance_m = routes[0].get('distance', 0)
                    distance_km = distance_m / 1000.0  # 转换为公里
                    
                    self.logger.debug(f"获取行驶距离: {origin} -> {destination} = {distance_km:.2f}km")
                    return distance_km
                else:
                    self.logger.warning(f"未找到路线: {origin} -> {destination}")
                    return None
            else:
                self.logger.warning(f"路线查询失败: 状态 {data.get('status')}")
                return None
                
        except Exception as e:
            self.logger.error(f"行驶距离API调用失败: {e}")
            return None
    
    def batch_get_driving_distances(self, locations: Dict[str, Tuple[float, float]], 
                                  max_retries: int = 3) -> np.ndarray:
        """
        批量获取车辆行驶距离矩阵
        
        Args:
            locations: 地点名称到坐标的映射
            max_retries: 最大重试次数
            
        Returns:
            距离矩阵 (numpy数组)
        """
        location_names = list(locations.keys())
        n = len(location_names)
        distance_matrix = np.zeros((n, n))
        
        total_requests = n * (n - 1)  # 不包括对角线
        completed_requests = 0
        
        self.logger.info(f"开始批量获取车辆距离矩阵，共需 {total_requests} 次API调用")
        
        for i, origin_name in enumerate(location_names):
            for j, dest_name in enumerate(location_names):
                if i == j:
                    distance_matrix[i][j] = 0.0
                    continue
                
                origin_coord = locations[origin_name]
                dest_coord = locations[dest_name]
                
                # 尝试获取距离，带重试机制
                distance = None
                for retry in range(max_retries):
                    distance = self.get_driving_distance(origin_coord, dest_coord)
                    if distance is not None:
                        break
                    else:
                        self.logger.warning(f"重试 {retry + 1}/{max_retries}: {origin_name} -> {dest_name}")
                        time.sleep(1)  # 重试前等待
                
                if distance is not None:
                    distance_matrix[i][j] = distance
                else:
                    # API失败时使用直线距离的1.3倍作为估算
                    straight_distance = self.calculate_haversine_distance(origin_coord, dest_coord)
                    estimated_distance = straight_distance * 1.3
                    distance_matrix[i][j] = estimated_distance
                    self.logger.warning(f"API失败，使用估算距离: {origin_name} -> {dest_name} = {estimated_distance:.2f}km")
                
                completed_requests += 1
                if completed_requests % 10 == 0:
                    self.logger.info(f"进度: {completed_requests}/{total_requests} ({completed_requests/total_requests*100:.1f}%)")
        
        self.logger.info("车辆距离矩阵获取完成")
        return distance_matrix

class DroneDistanceCalculator:
    """无人机距离计算器（基于坐标直线距离）"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    @staticmethod
    def calculate_haversine_distance(coord1: Tuple[float, float], 
                                   coord2: Tuple[float, float]) -> float:
        """
        使用Haversine公式计算两点间直线距离
        
        Args:
            coord1: 坐标1 (纬度, 经度)
            coord2: 坐标2 (纬度, 经度)
            
        Returns:
            距离（公里）
        """
        lat1, lon1 = radians(coord1[0]), radians(coord1[1])
        lat2, lon2 = radians(coord2[0]), radians(coord2[1])
        
        # Haversine公式
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # 地球半径（公里）
        R = 6371
        return R * c
    
    def calculate_distance_matrix(self, locations: Dict[str, Tuple[float, float]]) -> np.ndarray:
        """
        计算无人机距离矩阵
        
        Args:
            locations: 地点名称到坐标的映射
            
        Returns:
            距离矩阵 (numpy数组)
        """
        location_names = list(locations.keys())
        n = len(location_names)
        distance_matrix = np.zeros((n, n))
        
        self.logger.info(f"计算无人机直线距离矩阵，共 {n} 个地点")
        
        for i, origin_name in enumerate(location_names):
            for j, dest_name in enumerate(location_names):
                if i == j:
                    distance_matrix[i][j] = 0.0
                else:
                    origin_coord = locations[origin_name]
                    dest_coord = locations[dest_name]
                    distance = self.calculate_haversine_distance(origin_coord, dest_coord)
                    distance_matrix[i][j] = distance
        
        self.logger.info("无人机距离矩阵计算完成")
        return distance_matrix

class SmartDistanceManager:
    """智能距离管理器 - 整合车辆和无人机距离计算"""
    
    def __init__(self, baidu_api_key: str = None):
        """
        初始化距离管理器
        
        Args:
            baidu_api_key: 百度地图API密钥
        """
        self.baidu_api = BaiduMapAPI(baidu_api_key)
        self.drone_calc = DroneDistanceCalculator()
        self.logger = logging.getLogger(__name__)
    
    def generate_distance_matrices(self, locations: Dict[str, Tuple[float, float]], 
                                 use_api: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """
        生成车辆和无人机距离矩阵
        
        Args:
            locations: 地点坐标字典
            use_api: 是否使用百度地图API
            
        Returns:
            (车辆距离矩阵, 无人机距离矩阵)
        """
        self.logger.info("开始生成智能距离矩阵...")
        
        # 计算无人机距离矩阵（直线距离）
        drone_matrix = self.drone_calc.calculate_distance_matrix(locations)
        
        # 计算车辆距离矩阵
        if use_api and self.baidu_api.api_key:
            self.logger.info("使用百度地图API获取车辆实际行驶距离")
            vehicle_matrix = self.baidu_api.batch_get_driving_distances(locations)
        else:
            self.logger.info("使用直线距离估算车辆行驶距离")
            # 使用直线距离的1.3倍作为车辆距离估算
            vehicle_matrix = drone_matrix * 1.3
        
        self.logger.info("智能距离矩阵生成完成")
        return vehicle_matrix, drone_matrix
    
    def save_distance_matrices(self, vehicle_matrix: np.ndarray, 
                             drone_matrix: np.ndarray,
                             location_names: List[str],
                             output_dir: str = "data"):
        """
        保存距离矩阵到文件
        
        Args:
            vehicle_matrix: 车辆距离矩阵
            drone_matrix: 无人机距离矩阵  
            location_names: 地点名称列表
            output_dir: 输出目录
        """
        import pandas as pd
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存车辆距离矩阵
        vehicle_df = pd.DataFrame(vehicle_matrix, 
                                index=location_names, 
                                columns=location_names)
        vehicle_file = os.path.join(output_dir, "车辆距离矩阵_API.xlsx")
        vehicle_df.to_excel(vehicle_file)
        
        # 保存无人机距离矩阵
        drone_df = pd.DataFrame(drone_matrix,
                              index=location_names,
                              columns=location_names)
        drone_file = os.path.join(output_dir, "无人机距离矩阵.xlsx")
        drone_df.to_excel(drone_file)
        
        self.logger.info(f"距离矩阵已保存: {vehicle_file}, {drone_file}")

# 向后兼容的函数
def calculate_haversine_distance(coord1: Tuple[float, float], 
                               coord2: Tuple[float, float]) -> float:
    """计算两点间直线距离（向后兼容）"""
    return DroneDistanceCalculator.calculate_haversine_distance(coord1, coord2)

BaiduMapAPI.calculate_haversine_distance = staticmethod(calculate_haversine_distance)


