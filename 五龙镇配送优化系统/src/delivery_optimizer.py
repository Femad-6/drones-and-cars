# -*- coding: utf-8 -*-
"""
五龙镇配送优化系统 - 主优化器
整合所有模块提供完整的配送优化解决方案
"""

import logging
import time
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import json
import numpy as np

try:
    from .config import get_config, ConfigManager
    from .data import DataLoader
    from .algorithms import create_vehicle_drone_optimizer
    from .visualization import create_visualization_report
    from .utils import evaluate_time_constraint
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys
    import os
    current_dir = os.path.dirname(__file__)
    sys.path.insert(0, current_dir)
    try:
        from config import get_config, ConfigManager
        from data import DataLoader
        from algorithms import create_vehicle_drone_optimizer
        from visualization import create_visualization_report
        from utils import evaluate_time_constraint
    except ImportError:
        # 最后尝试
        parent_dir = os.path.dirname(current_dir)
        sys.path.insert(0, parent_dir)
        from config import get_config, ConfigManager
        from data import DataLoader
        from algorithms import create_vehicle_drone_optimizer
        from visualization import create_visualization_report
        from utils import evaluate_time_constraint


class DeliveryOptimizationSystem:
    """五龙镇配送优化系统主类"""

    def __init__(self, config_file: Optional[str] = None, baidu_api_key: str = None):
        """
        初始化配送优化系统

        Args:
            config_file: 配置文件路径
            baidu_api_key: 百度地图API密钥（用于智能距离计算）
        """
        self.logger = logging.getLogger(__name__)

        # 初始化配置
        self.config_manager = ConfigManager(config_file)
        self.config = self.config_manager.get_all_config()

        # 初始化组件
        self.data_loader = DataLoader(baidu_api_key)
        self.optimizer = None
        self.results = {}
        
        # 扩展数据存储
        self.cargo_details = {}
        self.upstream_packages = {}
        self.transfer_station_data = {}
        self.village_list = []

        self.logger.info("五龙镇配送优化系统初始化完成")

    def load_data(self, distance_matrices: Optional[Tuple[np.ndarray, np.ndarray]] = None) -> bool:
        """
        加载系统数据

        Args:
            distance_matrices: 可选的距离矩阵元组 (车辆距离矩阵, 无人机距离矩阵)

        Returns:
            是否加载成功
        """
        try:
            self.logger.info("开始加载数据...")

            # 获取配置
            file_paths = self.config.get('file_paths', {})

            # 加载位置数据
            self.locations = self.config['locations']
            self.logger.info(f"加载位置数据: {len(self.locations)} 个地点")

            # 加载需求数据（不包括五龙镇）
            self.demands = self.config['demands_piece']
            self.logger.info(f"加载需求数据: {len(self.demands)} 个村庄")

            # 加载回收品数据（保持向后兼容）
            self.recyclables = self.config['recyclables']
            self.logger.info(f"加载回收品数据: {len(self.recyclables)} 个村庄")

            # 加载扩展数据
            self.cargo_details = self.data_loader.load_cargo_details()
            self.upstream_packages = self.data_loader.load_upstream_packages()
            self.transfer_station_data = self.data_loader.load_transfer_station_data()
            
            # 获取村庄列表（排除中转站）
            self.village_list = self.data_loader.get_village_list(exclude_transfer_station=True)
            self.logger.info(f"获取村庄列表: {len(self.village_list)} 个村庄")

            # 加载距离矩阵（优先使用传入的矩阵）
            if distance_matrices is not None:
                self.distance_matrix, self.drone_distance_matrix = distance_matrices
                self.logger.info("使用智能API距离矩阵")
            else:
                self.distance_matrix = self.data_loader.load_vehicle_distance_matrix()
                self.drone_distance_matrix = None  # 可以使用默认的计算方法
                self.logger.info("使用默认距离矩阵")
            
            self.logger.info(f"车辆距离矩阵: {self.distance_matrix.shape}")

            # 数据验证（使用村庄列表而不是包含五龙镇的需求数据）
            village_demands = {v: self.demands[v] for v in self.village_list if v in self.demands}
            is_valid = self.data_loader.validate_data_consistency(village_demands, self.locations)
            if not is_valid:
                self.logger.warning("数据一致性检查失败，但继续执行")

            # 计算货物重量
            if self.cargo_details:
                self.cargo_weights = self.data_loader.calculate_cargo_weights(self.cargo_details)
                self.logger.info(f"计算货物重量完成: 总重量 {sum(self.cargo_weights.values()):.2f} kg")
            else:
                self.cargo_weights = {}

            # 计算上行包裹重量
            if self.upstream_packages:
                self.upstream_weights = self.data_loader.calculate_upstream_weights(self.upstream_packages)
                self.logger.info(f"计算上行包裹重量完成: 总重量 {sum(self.upstream_weights.values()):.2f} kg")
            else:
                self.upstream_weights = {}

            # 生成数据摘要
            report = self.data_loader.generate_summary_report(
                village_demands, self.locations, self.distance_matrix
            )

            self.logger.info("数据加载完成")
            self.logger.info(f"服务村庄数: {report['total_villages']}")
            self.logger.info(f"总需求量: {report['total_demand']} 件")
            self.logger.info(f"平均距离: {report['avg_distance']:.2f} km")
            
            # 输出中转站信息
            if self.transfer_station_data:
                total_packages = self.transfer_station_data.get('total_downstream_packages', 0)
                service_areas = len(self.transfer_station_data.get('service_areas', []))
                self.logger.info(f"五龙镇中转站: 总包裹{total_packages}件，服务{service_areas}个村庄")

            return True

        except Exception as e:
            self.logger.error(f"数据加载失败: {e}")
            return False

    def initialize_optimizer(self) -> bool:
        """
        初始化优化器

        Returns:
            是否初始化成功
        """
        try:
            self.logger.info("初始化优化器...")

            # 创建村庄需求数据（排除五龙镇中转站）
            village_demands = {v: self.demands[v] for v in self.village_list if v in self.demands}
            
            # 创建优化器
            self.optimizer = create_vehicle_drone_optimizer(
                locations=self.locations,
                demands=village_demands,  # 只传递村庄需求，不包括五龙镇
                distance_matrix=self.distance_matrix,
                drone_distance_matrix=getattr(self, 'drone_distance_matrix', None)
            )

            self.logger.info(f"优化器初始化完成，服务村庄数: {len(village_demands)}")
            return True

        except Exception as e:
            self.logger.error(f"优化器初始化失败: {e}")
            return False

    def run_optimization(self) -> bool:
        """
        运行优化算法

        Returns:
            是否优化成功
        """
        if self.optimizer is None:
            self.logger.error("优化器未初始化")
            return False

        try:
            self.logger.info("开始运行配送优化...")

            start_time = time.time()

            # 运行遗传算法
            best_solution, fitness_history = self.optimizer.optimize()

            optimization_time = time.time() - start_time

            if best_solution is None:
                self.logger.error("未找到可行解")
                return False

            self.logger.info(f"优化完成，耗时: {optimization_time:.2f} 秒")
            self.logger.info(f"最优目标值: {self.optimizer.best_fitness:.2f}")

            # 存储结果
            self.results = {
                'best_solution': best_solution,
                'best_fitness': self.optimizer.best_fitness,
                'optimization_history': fitness_history,
                'optimization_time': optimization_time,
                'config': self.config
            }

            return True

        except Exception as e:
            self.logger.error(f"优化过程失败: {e}")
            return False

    def analyze_solution(self) -> Dict[str, Any]:
        """
        分析优化结果

        Returns:
            分析结果字典
        """
        if not self.results or 'best_solution' not in self.results:
            self.logger.error("没有可用的解决方案")
            return {}

        try:
            self.logger.info("开始分析解决方案...")

            solution = self.results['best_solution']
            chromosome = solution.chromosome

            # 解析解决方案
            vehicle_routes = self._parse_vehicle_routes(chromosome)
            drone_assignments = self._parse_drone_assignments(chromosome)

            # 计算配送时间
            delivery_times = self._calculate_delivery_times(vehicle_routes, drone_assignments)

            # 评估时间约束
            time_threshold = self.config.get('time_constraints', {}).get('time_tag', 2.0)
            time_constraint_value = evaluate_time_constraint(delivery_times, time_threshold)

            # 计算成本
            cost_breakdown = self._calculate_cost_breakdown(vehicle_routes, drone_assignments)

            # 汇总分析结果
            analysis = {
                'vehicle_routes': vehicle_routes,
                'drone_assignments': drone_assignments,
                'delivery_times': delivery_times,
                'time_constraint_value': time_constraint_value,
                'cost_breakdown': cost_breakdown,
                'total_cost': sum(cost_breakdown.values()),
                'time_threshold': time_threshold,
                'locations': self.locations,
                'demands': self.demands,
                'optimization_history': self.results.get('optimization_history', [])
            }

            self.results['analysis'] = analysis

            # 打印分析摘要
            self._print_analysis_summary(analysis)

            return analysis

        except Exception as e:
            self.logger.error(f"解决方案分析失败: {e}")
            return {}

    def _parse_vehicle_routes(self, chromosome: Dict[str, Any]) -> Dict[int, List[str]]:
        """解析车辆路径"""
        villages = [v for v in self.demands.keys() if v not in ["配送中心", "五龙镇"]]
        vehicle_routes = {}

        # 按车辆分配分组
        for i, village in enumerate(villages):
            vehicle_id = int(chromosome['vehicle_assignment'][i])
            if chromosome['drone_assignment'][i] == 0:  # 非无人机配送
                if vehicle_id not in vehicle_routes:
                    vehicle_routes[vehicle_id] = []
                vehicle_routes[vehicle_id].append(village)

        # 按最优顺序排序
        ordered_villages = [villages[i] for i in chromosome['route_order']]
        order_map = {village: pos for pos, village in enumerate(ordered_villages)}

        for vehicle_id in vehicle_routes:
            vehicle_routes[vehicle_id].sort(key=lambda v: order_map.get(v, -1))

        return vehicle_routes

    def _parse_drone_assignments(self, chromosome: Dict[str, Any]) -> Dict[str, int]:
        """解析无人机分配"""
        villages = [v for v in self.demands.keys() if v not in ["配送中心", "五龙镇"]]
        drone_assignments = {}

        for i, village in enumerate(villages):
            if chromosome['drone_assignment'][i] == 1:
                vehicle_id = int(chromosome['vehicle_assignment'][i])
                drone_assignments[village] = vehicle_id

        return drone_assignments

    def _calculate_delivery_times(self, vehicle_routes: Dict[int, List[str]],
                                drone_assignments: Dict[str, int]) -> Dict[str, float]:
        """计算各村庄配送时间"""
        delivery_times = {}
        vehicle_params = self.config.get('vehicle_params', {})
        drone_params = self.config.get('drone_params', {})

        # 获取位置索引
        location_indices = {name: i for i, name in enumerate(self.locations.keys())}
        depot_idx = location_indices.get("配送中心")
        wulong_idx = location_indices.get("五龙镇")

        if depot_idx is None or wulong_idx is None:
            return delivery_times

        depot_to_wulong_time = self.distance_matrix[depot_idx, wulong_idx] / vehicle_params.get('speed', 50.0)

        # 计算车辆配送时间
        for vehicle_id, route in vehicle_routes.items():
            if not route:
                continue

            current_time = depot_to_wulong_time
            current_pos = wulong_idx

            for village in route:
                village_idx = location_indices[village]
                travel_time = self.distance_matrix[current_pos, village_idx] / vehicle_params.get('speed', 50.0)
                current_time += travel_time
                delivery_times[village] = current_time
                current_pos = village_idx

        # 计算无人机配送时间
        for village, vehicle_id in drone_assignments.items():
            village_idx = location_indices[village]

            # 简化为从五龙镇起飞
            takeoff_idx = wulong_idx
            start_time = depot_to_wulong_time

            # 无人机飞行时间
            distance = self.distance_matrix[takeoff_idx, village_idx]
            flight_time = (2 * distance) / drone_params.get('speed', 60.0)  # 往返时间

            delivery_times[village] = start_time + flight_time

        return delivery_times

    def _calculate_cost_breakdown(self, vehicle_routes: Dict[int, List[str]],
                                drone_assignments: Dict[str, int]) -> Dict[str, float]:
        """计算成本构成"""
        cost_breakdown = {
            'vehicle_fuel': 0.0,
            'vehicle_time': 0.0,
            'vehicle_fixed': 0.0,
            'drone_energy': 0.0,
            'drone_fixed': 0.0,
            'drone_time': 0.0
        }

        vehicle_params = self.config.get('vehicle_params', {})
        drone_params = self.config.get('drone_params', {})
        location_indices = {name: i for i, name in enumerate(self.locations.keys())}

        depot_idx = location_indices.get("配送中心")
        wulong_idx = location_indices.get("五龙镇")

        if depot_idx is None or wulong_idx is None:
            return cost_breakdown

        # 车辆成本计算
        depot_to_wulong_dist = self.distance_matrix[depot_idx, wulong_idx]

        for vehicle_id, route in vehicle_routes.items():
            # 配送中心到五龙镇的距离
            vehicle_distance = depot_to_wulong_dist

            # 村庄配送距离
            current_pos = wulong_idx
            for village in route:
                village_idx = location_indices[village]
                vehicle_distance += self.distance_matrix[current_pos, village_idx]
                current_pos = village_idx

            # 返回五龙镇
            if route:
                vehicle_distance += self.distance_matrix[current_pos, wulong_idx]

            # 燃油成本
            fuel_cost = vehicle_distance * vehicle_params.get('fuel_consumption', 0.252) * vehicle_params.get('fuel_price', 6.89)
            cost_breakdown['vehicle_fuel'] += fuel_cost

            # 时间成本
            travel_time = vehicle_distance / vehicle_params.get('speed', 50.0)
            time_cost = travel_time * vehicle_params.get('driver_time_price', 60.0)
            cost_breakdown['vehicle_time'] += time_cost

            # 固定成本
            cost_breakdown['vehicle_fixed'] += vehicle_params.get('deploy_fixed_cost', 20.0)

        # 无人机成本计算
        for village in drone_assignments.keys():
            village_idx = location_indices[village]
            takeoff_idx = wulong_idx  # 简化为五龙镇起飞

            distance = self.distance_matrix[takeoff_idx, village_idx]
            demand = self.demands.get(village, 0)

            # 计算架次
            trips = max(1, int(np.ceil(demand / drone_params.get('max_payload', 80))))

            # 每架次成本
            energy_per_trip = (drone_params.get('power_kwh_per_km_base', 0.164) +
                             drone_params.get('power_kwh_per_km_slope', 0.191) *
                             (demand / trips) / drone_params.get('max_payload', 80)) * 2 * distance

            total_energy = energy_per_trip * trips
            energy_cost = total_energy * drone_params.get('electricity_price', 0.6)
            cost_breakdown['drone_energy'] += energy_cost

            # 固定成本
            fixed_cost = trips * drone_params.get('trip_fixed_cost', 5.0)
            cost_breakdown['drone_fixed'] += fixed_cost

            # 时间成本
            flight_time = (2 * distance / drone_params.get('speed', 60.0)) * trips
            time_cost = flight_time * drone_params.get('time_price', 20.0)
            cost_breakdown['drone_time'] += time_cost

        return cost_breakdown

    def _print_analysis_summary(self, analysis: Dict[str, Any]):
        """打印分析摘要"""
        print("\n" + "="*60)
        print("五龙镇配送优化系统 - 解决方案分析")
        print("="*60)

        print(f"总成本: {analysis['total_cost']:.2f} 元")
        print(f"时间约束评估值: {analysis['time_constraint_value']:.3f}")

        # 车辆使用情况
        vehicle_routes = analysis['vehicle_routes']
        print(f"\n车辆使用情况:")
        for vehicle_id, route in vehicle_routes.items():
            if route:
                print(f"  车辆{vehicle_id+1}: {len(route)}个村庄 - {', '.join(route)}")

        # 无人机使用情况
        drone_assignments = analysis['drone_assignments']
        if drone_assignments:
            print(f"\n无人机配送村庄: {', '.join(drone_assignments.keys())}")

        # 时间分析
        delivery_times = analysis['delivery_times']
        if delivery_times:
            avg_time = sum(delivery_times.values()) / len(delivery_times)
            max_time = max(delivery_times.values())
            on_time_count = sum(1 for t in delivery_times.values() if t <= analysis['time_threshold'])

            print(f"\n时间分析:")
            print(f"  平均配送时间: {avg_time:.2f} 小时")
            print(f"  最长配送时间: {max_time:.2f} 小时")
            print(f"  准时配送村庄: {on_time_count}/{len(delivery_times)} ({on_time_count/len(delivery_times)*100:.1f}%)")

        print("="*60)

    def generate_report(self, output_dir: str = "output") -> bool:
        """
        生成完整报告

        Args:
            output_dir: 输出目录

        Returns:
            是否生成成功
        """
        try:
            self.logger.info(f"生成报告到目录: {output_dir}")

            # 创建输出目录
            Path(output_dir).mkdir(exist_ok=True)

            # 生成可视化报告
            if 'analysis' in self.results:
                create_visualization_report(self.results['analysis'], output_dir)

            # 保存结果到JSON
            results_file = Path(output_dir) / "optimization_results.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                # 转换不可序列化的对象
                serializable_results = {}
                for key, value in self.results.items():
                    if key == 'best_solution':
                        serializable_results[key] = {
                            'chromosome': {k: v.tolist() if isinstance(v, np.ndarray) else v
                                         for k, v in value.chromosome.items()},
                            'fitness': value.fitness
                        }
                    else:
                        try:
                            json.dumps(value)  # 测试是否可序列化
                            serializable_results[key] = value
                        except:
                            serializable_results[key] = str(value)

                json.dump(serializable_results, f, indent=2, ensure_ascii=False)

            # 保存配置摘要
            self.config_manager.print_config_summary()

            self.logger.info("报告生成完成")
            return True

        except Exception as e:
            self.logger.error(f"报告生成失败: {e}")
            return False

    def run_complete_optimization(self, output_dir: str = "output") -> bool:
        """
        运行完整的优化流程

        Args:
            output_dir: 输出目录

        Returns:
            是否执行成功
        """
        self.logger.info("开始执行完整的配送优化流程...")

        # 1. 加载数据
        if not self.load_data():
            return False

        # 2. 初始化优化器
        if not self.initialize_optimizer():
            return False

        # 3. 运行优化
        if not self.run_optimization():
            return False

        # 4. 分析结果
        analysis = self.analyze_solution()
        if not analysis:
            return False

        # 5. 生成报告
        if not self.generate_report(output_dir):
            return False

        self.logger.info("完整的优化流程执行完成！")
        return True


# 便捷函数
def create_delivery_system(config_file: Optional[str] = None) -> DeliveryOptimizationSystem:
    """创建配送优化系统实例"""
    return DeliveryOptimizationSystem(config_file)

def run_optimization_pipeline(config_file: Optional[str] = None,
                            output_dir: str = "output") -> bool:
    """运行完整的优化流程"""
    system = create_delivery_system(config_file)
    return system.run_complete_optimization(output_dir)
