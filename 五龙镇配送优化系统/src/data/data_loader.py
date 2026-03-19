# -*- coding: utf-8 -*-
"""
五龙镇配送优化系统 - 数据加载器
负责Excel文件读取、数据验证和预处理
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import logging
import os

try:
    from ..config import get_config
    from ..utils.geographic_utils import GeographicCalculator
    from ..utils.map_api import SmartDistanceManager, BaiduMapAPI, DroneDistanceCalculator
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys
    import os
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)
    try:
        from config import get_config
        from utils.geographic_utils import GeographicCalculator
        from utils.map_api import SmartDistanceManager, BaiduMapAPI, DroneDistanceCalculator
    except ImportError:
        # 最后尝试
        sys.path.insert(0, current_dir)
        from config import get_config
        from utils.geographic_utils import GeographicCalculator
        from utils.map_api import SmartDistanceManager, BaiduMapAPI, DroneDistanceCalculator


class DataLoader:
    """数据加载器类"""

    def __init__(self, baidu_api_key: str = None):
        self.logger = logging.getLogger(__name__)
        self.calc = GeographicCalculator()
        self.smart_distance_manager = SmartDistanceManager(baidu_api_key)
        self.baidu_api_key = baidu_api_key

    def load_excel_data(self, file_path: str,
                       sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        加载Excel文件数据

        Args:
            file_path: 文件路径
            sheet_name: 工作表名称

        Returns:
            数据框
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")

            result = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # 当sheet_name=None时，pandas可能返回字典或DataFrame
            if isinstance(result, dict):
                # 如果返回字典，取第一个工作表的DataFrame
                df = list(result.values())[0]
                sheet_names = list(result.keys())
                self.logger.info(f"Excel文件包含多个工作表: {sheet_names}，使用第一个: {sheet_names[0]}")
            else:
                # 如果返回DataFrame，直接使用
                df = result
            
            self.logger.info(f"成功加载Excel文件: {file_path}")
            self.logger.info(f"数据形状: {df.shape}")
            return df

        except Exception as e:
            self.logger.error(f"加载Excel文件失败 {file_path}: {e}")
            raise

    def load_vehicle_distance_matrix(self, file_path: Optional[str] = None) -> np.ndarray:
        """
        加载车辆距离矩阵

        Args:
            file_path: 文件路径，如果为None则使用配置中的路径

        Returns:
            距离矩阵
        """
        if file_path is None:
            file_path = get_config('file_paths.vehicle_distance_file')

        try:
            df = self.load_excel_data(file_path)

            # 尝试不同的数据格式
            if 'from' in df.columns:
                # 格式1：from列 + 目的地列
                locations = get_config('locations', {})
                names = list(locations.keys())
                matrix = np.zeros((len(names), len(names)))

                for i, a in enumerate(names):
                    for j, b in enumerate(names):
                        if i == j:
                            matrix[i, j] = 0.0
                            continue
                        try:
                            val = df.loc[df['from'] == a, b].values[0]
                            if pd.isna(val):
                                # 使用直线距离的1.2倍作为替代
                                lat1, lon1 = locations[a]
                                lat2, lon2 = locations[b]
                                val = self.calc.haversine_distance(lat1, lon1, lat2, lon2) * 1.2
                            matrix[i, j] = float(val)
                        except (KeyError, IndexError):
                            # 回退到直线距离
                            lat1, lon1 = locations[a]
                            lat2, lon2 = locations[b]
                            matrix[i, j] = self.calc.haversine_distance(lat1, lon1, lat2, lon2) * 1.2
            else:
                # 格式2：标准矩阵格式
                df.set_index(df.columns[0], inplace=True)
                locations = get_config('locations', {})
                names = list(locations.keys())
                matrix = np.zeros((len(names), len(names)))

                for i, a in enumerate(names):
                    for j, b in enumerate(names):
                        if i == j:
                            matrix[i, j] = 0.0
                        else:
                            try:
                                val = df.loc[a, b]
                                if pd.isna(val):
                                    lat1, lon1 = locations[a]
                                    lat2, lon2 = locations[b]
                                    val = self.calc.haversine_distance(lat1, lon1, lat2, lon2) * 1.2
                                matrix[i, j] = float(val)
                            except KeyError:
                                lat1, lon1 = locations[a]
                                lat2, lon2 = locations[b]
                                matrix[i, j] = self.calc.haversine_distance(lat1, lon1, lat2, lon2) * 1.2

            self.logger.info("成功加载车辆距离矩阵")
            return matrix

        except Exception as e:
            self.logger.warning(f"加载车辆距离矩阵失败: {e}")
            self.logger.info("使用直线距离的1.2倍作为替代")
            locations = get_config('locations', {})
            matrix = self.calc.calculate_distance_matrix(locations)
            return matrix * 1.2

    def load_village_distance_matrix(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        加载村庄距离矩阵

        Args:
            file_path: 文件路径

        Returns:
            距离矩阵数据框
        """
        if file_path is None:
            file_path = get_config('file_paths.village_distance_file')

        try:
            df = self.load_excel_data(file_path)
            self.logger.info("成功加载村庄距离矩阵")
            return df
        except Exception as e:
            self.logger.error(f"加载村庄距离矩阵失败: {e}")
            return pd.DataFrame()

    def validate_data_consistency(self, demands: Dict[str, float],
                                locations: Dict[str, Tuple[float, float]]) -> bool:
        """
        验证数据一致性

        Args:
            demands: 需求量字典
            locations: 位置字典

        Returns:
            是否一致
        """
        demand_locations = set(demands.keys())
        location_names = set(locations.keys())

        # 检查是否有需求但没有位置的村庄
        missing_locations = demand_locations - location_names
        if missing_locations:
            self.logger.warning(f"以下村庄缺少位置信息: {missing_locations}")
            return False

        # 检查是否有位置但没有需求的村庄
        extra_locations = location_names - demand_locations
        if extra_locations:
            self.logger.info(f"以下村庄有位置但无需求数据: {extra_locations}")

        return len(missing_locations) == 0

    def preprocess_demands(self, demands: Dict[str, float]) -> Dict[str, float]:
        """
        预处理需求数据

        Args:
            demands: 原始需求数据

        Returns:
            处理后的需求数据
        """
        processed = {}

        for village, demand in demands.items():
            # 确保需求为非负数
            processed[village] = max(0.0, float(demand))

        self.logger.info(f"预处理需求数据完成，共{len(processed)}个村庄")
        return processed

    def calculate_supply_capacity(self, recyclables: Dict[str, Dict[str, float]],
                                package_weight: float = 2.0) -> Dict[str, float]:
        """
        计算回收品供应能力

        Args:
            recyclables: 回收品数据
            package_weight: 件重（kg）

        Returns:
            供应能力字典（kg）
        """
        capacity = {}

        for village, data in recyclables.items():
            short_kg = data.get('short', 0) * package_weight
            long_kg = data.get('long', 0) * package_weight
            capacity[village] = short_kg + long_kg

        self.logger.info(f"计算供应能力完成，共{len(capacity)}个村庄")
        return capacity
    
    def load_cargo_details(self) -> Dict[str, Dict[str, int]]:
        """
        加载详细货物分类数据

        Returns:
            货物详细分类数据
        """
        try:
            cargo_details = get_config('cargo_details', {})
            self.logger.info(f"加载货物详细分类数据，共{len(cargo_details)}个村庄")
            return cargo_details
        except Exception as e:
            self.logger.error(f"加载货物详细分类数据失败: {e}")
            return {}
    
    def load_upstream_packages(self) -> Dict[str, Dict[str, Dict[str, int]]]:
        """
        加载上行包裹详细数据

        Returns:
            上行包裹详细数据
        """
        try:
            upstream_packages = get_config('upstream_packages', {})
            self.logger.info(f"加载上行包裹详细数据，共{len(upstream_packages)}个村庄")
            return upstream_packages
        except Exception as e:
            self.logger.error(f"加载上行包裹详细数据失败: {e}")
            return {}
    
    def load_transfer_station_data(self) -> Dict[str, Any]:
        """
        加载五龙镇中转站数据

        Returns:
            中转站数据
        """
        try:
            transfer_station = get_config('wulong_transfer_station', {})
            self.logger.info(f"加载五龙镇中转站数据：总下行包裹{transfer_station.get('total_downstream_packages', 0)}件")
            return transfer_station
        except Exception as e:
            self.logger.error(f"加载五龙镇中转站数据失败: {e}")
            return {}
    
    def calculate_cargo_weights(self, cargo_details: Dict[str, Dict[str, int]], 
                               weight_config: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        根据货物详细分类计算各村庄的总重量

        Args:
            cargo_details: 货物详细分类数据
            weight_config: 重量配置 {'light_packages': 0.5, 'heavy_packages': 2.0, 'fragile_items': 1.0}

        Returns:
            各村庄的总货物重量（kg）
        """
        if weight_config is None:
            weight_config = {
                'light_packages': 0.5,  # 轻包裹：0.5kg/件
                'heavy_packages': 2.0,  # 重包裹：2.0kg/件
                'fragile_items': 1.0    # 易碎物品：1.0kg/件
            }
        
        weights = {}
        
        for village, details in cargo_details.items():
            total_weight = 0.0
            for cargo_type, count in details.items():
                unit_weight = weight_config.get(cargo_type, 1.0)
                total_weight += count * unit_weight
            
            weights[village] = total_weight
        
        self.logger.info(f"计算货物重量完成，共{len(weights)}个村庄")
        return weights
    
    def calculate_upstream_weights(self, upstream_packages: Dict[str, Dict[str, Dict[str, int]]],
                                 weight_config: Optional[Dict[str, Dict[str, float]]] = None) -> Dict[str, float]:
        """
        根据上行包裹详细数据计算各村庄的上行重量

        Args:
            upstream_packages: 上行包裹详细数据
            weight_config: 各类型物品的单位重量配置

        Returns:
            各村庄的上行包裹总重量（kg）
        """
        if weight_config is None:
            weight_config = {
                'recyclables': {'paper': 0.1, 'plastic': 0.05, 'electronics': 2.0},
                'agricultural_products': {'fruits': 0.2, 'vegetables': 0.15, 'grains': 0.5},
                'handmade_crafts': {'textiles': 0.3, 'woodwork': 1.0, 'pottery': 0.8},
                'return_packages': {'damaged': 1.0, 'wrong_delivery': 0.5}
            }
        
        weights = {}
        
        for village, categories in upstream_packages.items():
            total_weight = 0.0
            
            for category, items in categories.items():
                category_config = weight_config.get(category, {})
                for item_type, count in items.items():
                    unit_weight = category_config.get(item_type, 1.0)
                    total_weight += count * unit_weight
            
            weights[village] = total_weight
        
        self.logger.info(f"计算上行包裹重量完成，共{len(weights)}个村庄")
        return weights
    
    def get_village_list(self, exclude_transfer_station: bool = True) -> List[str]:
        """
        获取村庄列表（不包括配送中心和中转站）

        Args:
            exclude_transfer_station: 是否排除中转站

        Returns:
            村庄名称列表
        """
        demands = get_config('demands_piece', {})
        villages = list(demands.keys())
        
        if exclude_transfer_station:
            # 排除配送中心和五龙镇中转站
            exclude_list = ['配送中心', '五龙镇']
            villages = [v for v in villages if v not in exclude_list]
        
        self.logger.info(f"获取村庄列表，共{len(villages)}个村庄")
        return villages

    def generate_summary_report(self, demands: Dict[str, float],
                              locations: Dict[str, Tuple[float, float]],
                              distance_matrix: np.ndarray) -> Dict[str, Any]:
        """
        生成数据摘要报告

        Args:
            demands: 需求数据
            locations: 位置数据
            distance_matrix: 距离矩阵

        Returns:
            摘要报告字典
        """
        report = {
            'total_villages': len(demands),
            'total_demand': sum(demands.values()),
            'avg_demand': np.mean(list(demands.values())),
            'max_demand': max(demands.values()),
            'min_demand': min(demands.values()),
            'demand_std': np.std(list(demands.values())),
            'max_distance': np.max(distance_matrix),
            'avg_distance': np.mean(distance_matrix[distance_matrix > 0]),
            'median_distance': np.median(distance_matrix[distance_matrix > 0])
        }

        # 距离分布统计
        distances = distance_matrix[distance_matrix > 0].flatten()
        report['distance_ranges'] = {
            'near': len(distances[distances <= 10]),
            'medium': len(distances[(distances > 10) & (distances <= 15)]),
            'far': len(distances[distances > 15])
        }

        self.logger.info("数据摘要报告生成完成")
        return report

    def export_data_summary(self, report: Dict[str, Any],
                          output_path: str = "data_summary.txt"):
        """
        导出数据摘要到文件

        Args:
            report: 摘要报告
            output_path: 输出路径
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=" * 50 + "\n")
                f.write("五龙镇配送优化系统 - 数据摘要\n")
                f.write("=" * 50 + "\n\n")

                f.write("基本信息:\n")
                f.write(f"  服务村庄数: {report['total_villages']} 个\n")
                f.write(f"  总需求量: {report['total_demand']:.0f} 件\n")
                f.write(f"  平均需求: {report['avg_demand']:.1f} 件\n")
                f.write(f"  最大需求: {report['max_demand']:.0f} 件\n")
                f.write(f"  最小需求: {report['min_demand']:.0f} 件\n\n")

                f.write("距离统计:\n")
                f.write(f"  最大距离: {report['max_distance']:.2f} km\n")
                f.write(f"  平均距离: {report['avg_distance']:.2f} km\n")
                f.write(f"  中位距离: {report['median_distance']:.2f} km\n\n")

                f.write("距离分布:\n")
                dist_ranges = report['distance_ranges']
                total = sum(dist_ranges.values())
                f.write(f"  近程(≤10km): {dist_ranges['near']} ({dist_ranges['near']/total*100:.1f}%)\n")
                f.write(f"  中程(10-15km): {dist_ranges['medium']} ({dist_ranges['medium']/total*100:.1f}%)\n")
                f.write(f"  远程(>15km): {dist_ranges['far']} ({dist_ranges['far']/total*100:.1f}%)\n")

            self.logger.info(f"数据摘要已导出到: {output_path}")

        except Exception as e:
            self.logger.error(f"导出数据摘要失败: {e}")

    def generate_smart_distance_matrices(self, locations: Dict[str, Tuple[float, float]], 
                                       use_baidu_api: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """
        智能生成车辆和无人机距离矩阵
        
        Args:
            locations: 地点坐标字典
            use_baidu_api: 是否使用百度地图API获取车辆距离
            
        Returns:
            (车辆距离矩阵, 无人机距离矩阵)
        """
        try:
            self.logger.info("开始生成智能距离矩阵...")
            
            if use_baidu_api and self.baidu_api_key:
                self.logger.info("使用百度地图API获取车辆真实行驶距离")
                vehicle_matrix, drone_matrix = self.smart_distance_manager.generate_distance_matrices(
                    locations, use_api=True
                )
            else:
                self.logger.info("使用坐标计算估算距离")
                vehicle_matrix, drone_matrix = self.smart_distance_manager.generate_distance_matrices(
                    locations, use_api=False
                )
            
            self.logger.info("智能距离矩阵生成完成")
            return vehicle_matrix, drone_matrix
            
        except Exception as e:
            self.logger.error(f"智能距离矩阵生成失败: {e}")
            # 降级到传统方法
            self.logger.info("降级使用传统坐标计算方法")
            matrix = self.calc.calculate_distance_matrix(locations)
            return matrix * 1.3, matrix  # 车辆距离为直线距离的1.3倍

    def load_locations_from_text(self, location_descriptions: List[str], 
                               city: str = "济源市") -> Dict[str, Tuple[float, float]]:
        """
        从地点描述文本加载坐标（通过百度地图API）
        
        Args:
            location_descriptions: 地点描述列表
            city: 城市名称
            
        Returns:
            地点名称到坐标的映射
        """
        locations = {}
        
        if not self.baidu_api_key:
            self.logger.warning("未配置百度地图API密钥，无法进行地址解析")
            return locations
        
        for desc in location_descriptions:
            try:
                coord = self.smart_distance_manager.baidu_api.geocode_address(desc, city)
                if coord:
                    locations[desc] = coord
                    self.logger.info(f"地址解析成功: {desc} -> {coord}")
                else:
                    self.logger.warning(f"地址解析失败: {desc}")
            except Exception as e:
                self.logger.error(f"地址解析出错 {desc}: {e}")
        
        return locations

    def save_smart_distance_matrices(self, vehicle_matrix: np.ndarray, 
                                   drone_matrix: np.ndarray,
                                   location_names: List[str],
                                   output_dir: str = "data"):
        """
        保存智能生成的距离矩阵
        
        Args:
            vehicle_matrix: 车辆距离矩阵
            drone_matrix: 无人机距离矩阵
            location_names: 地点名称列表
            output_dir: 输出目录
        """
        try:
            self.smart_distance_manager.save_distance_matrices(
                vehicle_matrix, drone_matrix, location_names, output_dir
            )
            self.logger.info("智能距离矩阵保存完成")
        except Exception as e:
            self.logger.error(f"保存距离矩阵失败: {e}")

    def validate_api_key(self) -> bool:
        """
        验证百度地图API密钥是否有效
        
        Returns:
            是否有效
        """
        if not self.baidu_api_key:
            return False
        
        try:
            # 尝试解析一个测试地址
            test_coord = self.smart_distance_manager.baidu_api.geocode_address("天安门", "北京市")
            return test_coord is not None
        except Exception:
            return False

    def set_baidu_api_key(self, api_key: str):
        """
        设置百度地图API密钥
        
        Args:
            api_key: API密钥
        """
        self.baidu_api_key = api_key
        self.smart_distance_manager = SmartDistanceManager(api_key)
        self.logger.info("百度地图API密钥已更新")


# 便捷函数
def load_vehicle_distance_matrix(file_path: Optional[str] = None) -> np.ndarray:
    """便捷的车辆距离矩阵加载函数"""
    loader = DataLoader()
    return loader.load_vehicle_distance_matrix(file_path)

def load_excel_data(file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
    """便捷的Excel数据加载函数"""
    loader = DataLoader()
    return loader.load_excel_data(file_path, sheet_name)

def validate_data_consistency(demands: Dict[str, float],
                            locations: Dict[str, Tuple[float, float]]) -> bool:
    """便捷的数据一致性验证函数"""
    loader = DataLoader()
    return loader.validate_data_consistency(demands, locations)
