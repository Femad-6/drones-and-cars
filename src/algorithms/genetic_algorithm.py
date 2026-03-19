# -*- coding: utf-8 -*-
"""
五龙镇配送优化系统 - 遗传算法模块
实现车辆-无人机协同配送的遗传算法优化
"""

import numpy as np
import random
from typing import Dict, List, Tuple, Any, Optional, Callable
from abc import ABC, abstractmethod
import logging
import copy

try:
    from ..config import get_config
    from ..utils import evaluate_time_constraint
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from config import get_config
    from utils import evaluate_time_constraint


class Individual:
    """遗传算法个体类"""

    def __init__(self, chromosome: Dict[str, np.ndarray]):
        """
        初始化个体

        Args:
            chromosome: 染色体，包含车辆分配、无人机分配、路径顺序等
        """
        self.chromosome = chromosome
        self.fitness = None
        self.feasible = True

    def copy(self):
        """创建个体的深拷贝"""
        return Individual({
            key: (value.copy() if isinstance(value, np.ndarray) else value)
            for key, value in self.chromosome.items()
        })


class GeneticAlgorithm(ABC):
    """遗传算法基类"""

    def __init__(self, population_size: int = 150,
                 generations: int = 500,
                 crossover_rate: float = 0.85,
                 mutation_rate: float = 0.25,
                 elite_size: int = 10):
        """
        初始化遗传算法

        Args:
            population_size: 种群大小
            generations: 迭代代数
            crossover_rate: 交叉概率
            mutation_rate: 变异概率
            elite_size: 精英个体数量
        """
        self.population_size = population_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elite_size = int(elite_size)

        self.logger = logging.getLogger(__name__)
        self.best_individual = None
        self.best_fitness = float('inf')
        self.fitness_history = []

    @abstractmethod
    def create_individual(self) -> Individual:
        """创建随机个体"""
        pass

    @abstractmethod
    def evaluate_fitness(self, individual: Individual) -> float:
        """评估个体适应度"""
        pass

    @abstractmethod
    def crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """交叉操作"""
        pass

    @abstractmethod
    def mutate(self, individual: Individual) -> Individual:
        """变异操作"""
        pass

    def select_parents(self, population: List[Individual],
                      fitness_values: List[float]) -> Tuple[Individual, Individual]:
        """选择父代个体（轮盘赌选择）"""
        # 计算适应度（转换为最小化问题）
        min_fitness = min(fitness_values)
        max_fitness = max(fitness_values)

        if min_fitness == max_fitness:
            # 所有个体适应度相同，随机选择
            return random.choice(population), random.choice(population)

        # 转换为选择概率（适应度越小越好）
        inverted_fitness = [max_fitness - f + 1e-6 for f in fitness_values]
        total_fitness = sum(inverted_fitness)
        probabilities = [f / total_fitness for f in inverted_fitness]

        # 轮盘赌选择
        parent1 = random.choices(population, weights=probabilities)[0]
        parent2 = random.choices(population, weights=probabilities)[0]

        return parent1, parent2

    def evolve(self, initial_population: Optional[List[Individual]] = None) -> Tuple[Individual, List[float]]:
        """
        进化过程

        Args:
            initial_population: 初始种群（可选）

        Returns:
            最优个体和适应度历史
        """
        if initial_population is None:
            population = [self.create_individual() for _ in range(self.population_size)]
        else:
            population = initial_population.copy()

        self.best_individual = None
        self.best_fitness = float('inf')
        self.fitness_history = []

        for generation in range(self.generations):
            # 评估种群适应度
            fitness_values = []
            for individual in population:
                fitness = self.evaluate_fitness(individual)
                fitness_values.append(fitness)

                if fitness < self.best_fitness:
                    self.best_fitness = fitness
                    self.best_individual = individual.copy()

            self.fitness_history.append(self.best_fitness)

            # 检查是否所有个体都不可行
            if all(f == float('inf') for f in fitness_values):
                self.logger.warning(f"第{generation}代：全体不可行，重置种群")
                population = [self.create_individual() for _ in range(self.population_size)]
                continue

            # 创建新种群
            new_population = []

            # 精英保留
            elite_indices = np.argsort(fitness_values)[:self.elite_size]
            for idx in elite_indices:
                new_population.append(population[idx].copy())

            # 生成剩余个体
            while len(new_population) < self.population_size:
                # 选择父代
                parent1, parent2 = self.select_parents(population, fitness_values)

                # 交叉
                if random.random() < self.crossover_rate:
                    child1, child2 = self.crossover(parent1, parent2)
                else:
                    child1, child2 = parent1.copy(), parent2.copy()

                # 变异
                child1 = self.mutate(child1)
                if len(new_population) < self.population_size:
                    child2 = self.mutate(child2)

                new_population.extend([child1, child2][:self.population_size - len(new_population)])

            population = new_population

            # 记录进度
            if generation % 20 == 0:
                self.logger.info(f"第 {generation} 代，最优适应度: {self.best_fitness:.2f}")

        self.logger.info(f"遗传算法完成！最优适应度: {self.best_fitness:.2f}")
        return self.best_individual, self.fitness_history


class VehicleDroneGA(GeneticAlgorithm):
    """车辆-无人机协同配送遗传算法"""

    def __init__(self, locations: Dict[str, Tuple[float, float]],
                 demands: Dict[str, float],
                 vehicle_params: Dict[str, Any],
                 drone_params: Dict[str, Any],
                 distance_matrix: np.ndarray,
                 **kwargs):
        """
        初始化车辆-无人机GA

        Args:
            locations: 位置字典
            demands: 需求字典
            vehicle_params: 车辆参数
            drone_params: 无人机参数
            distance_matrix: 距离矩阵
        """
        super().__init__(**kwargs)

        self.locations = locations
        self.demands = demands
        self.vehicle_params = vehicle_params
        self.drone_params = drone_params
        self.distance_matrix = distance_matrix

        # 村庄列表（排除配送中心和五龙镇）
        self.villages = [v for v in demands.keys() if v not in ["配送中心", "五龙镇"]]
        self.num_villages = len(self.villages)
        self.num_vehicles = vehicle_params['num_vehicles']

        # 位置索引映射
        self.location_indices = {name: i for i, name in enumerate(locations.keys())}

    def create_individual(self) -> Individual:
        """创建随机个体"""
        chromosome = {
            'vehicle_assignment': np.random.randint(0, self.num_vehicles, self.num_villages),
            'drone_assignment': np.zeros(self.num_villages, dtype=int),
            'route_order': np.random.permutation(self.num_villages)
        }

        # 启发式：远距离村庄倾向于使用无人机
        wulong_idx = self.location_indices.get("五龙镇")
        if wulong_idx is not None:
            for i, village in enumerate(self.villages):
                if village in self.location_indices:
                    village_idx = self.location_indices[village]
                    if isinstance(wulong_idx, int) and isinstance(village_idx, int):
                        distance = self.distance_matrix[wulong_idx, village_idx]
                        demand = self.demands.get(village, 0)
                        
                        # 远且需求少的村庄使用无人机
                        if distance > 10 and demand <= self.drone_params['max_payload'] * 0.5:
                            chromosome['drone_assignment'][i] = 1

        return Individual(chromosome)

    def evaluate_fitness(self, individual: Individual) -> float:
        """评估个体适应度"""
        try:
            return self._calculate_cost(individual)
        except Exception as e:
            self.logger.error(f"适应度评估失败: {e}")
            return float('inf')

    def _calculate_cost(self, individual: Individual) -> float:
        """计算总成本"""
        chromosome = individual.chromosome

        # 初始化车辆状态
        vehicle_routes = [[] for _ in range(self.num_vehicles)]
        vehicle_loads = [0.0] * self.num_vehicles
        vehicle_used = [False] * self.num_vehicles
        vehicle_has_drone = [False] * self.num_vehicles

        # 分配村庄到车辆/无人机
        for i, village in enumerate(self.villages):
            vehicle_idx = int(chromosome['vehicle_assignment'][i])
            is_drone = chromosome['drone_assignment'][i] == 1

            if is_drone:
                vehicle_has_drone[vehicle_idx] = True
            else:
                vehicle_routes[vehicle_idx].append(village)
                vehicle_loads[vehicle_idx] += self.demands[village]

            vehicle_used[vehicle_idx] = True

        # 容量约束检查
        for i, load in enumerate(vehicle_loads):
            if load > self.vehicle_params['capacity']:
                return float('inf')

        # 按顺序排序路径
        ordered_villages = [self.villages[i] for i in chromosome['route_order']]
        order_map = {village: pos for pos, village in enumerate(ordered_villages)}

        for i in range(self.num_vehicles):
            if vehicle_routes[i]:
                vehicle_routes[i].sort(key=lambda v: order_map.get(v, -1))

        # 计算车辆成本
        total_vehicle_cost = 0.0
        depot_idx = self.location_indices.get("配送中心")
        wulong_idx = self.location_indices.get("五龙镇")

        if depot_idx is None or wulong_idx is None:
            return float('inf')
        
        if not isinstance(depot_idx, int) or not isinstance(wulong_idx, int):
            return float('inf')

        depot_to_wulong_dist = self.distance_matrix[depot_idx, wulong_idx]

        for i in range(self.num_vehicles):
            if not vehicle_used[i] and not vehicle_has_drone[i]:
                continue

            # 车辆行驶距离计算
            vehicle_distance = 0.0
            current_pos = wulong_idx

            if vehicle_routes[i]:
                for village in vehicle_routes[i]:
                    village_idx = self.location_indices.get(village)
                    if village_idx is not None and isinstance(village_idx, int) and isinstance(current_pos, int):
                        vehicle_distance += self.distance_matrix[current_pos, village_idx]
                        current_pos = village_idx
                    else:
                        return float('inf')
                # 返回五龙镇
                if isinstance(current_pos, int) and isinstance(wulong_idx, int):
                    vehicle_distance += self.distance_matrix[current_pos, wulong_idx]
                else:
                    return float('inf')
            else:
                # 仅携机：近似计算到最远无人机的距离
                max_dist = 0.0
                for j, village in enumerate(self.villages):
                    if chromosome['drone_assignment'][j] == 1 and int(chromosome['vehicle_assignment'][j]) == i:
                        village_idx = self.location_indices.get(village)
                        if village_idx is not None and isinstance(village_idx, int) and isinstance(wulong_idx, int):
                            dist = self.distance_matrix[wulong_idx, village_idx]
                            if dist > max_dist:
                                max_dist = dist
                if max_dist > 0:
                    vehicle_distance = 2.0 * max_dist

            # 燃油成本
            fuel_cost = vehicle_distance * self.vehicle_params['fuel_consumption'] * self.vehicle_params['fuel_price']

            # 时间成本
            travel_time = vehicle_distance / self.vehicle_params['speed']
            time_cost = travel_time * self.vehicle_params['driver_time_price']

            # 固定成本
            fixed_cost = self.vehicle_params['deploy_fixed_cost']

            total_vehicle_cost += fuel_cost + time_cost + fixed_cost

        # 计算无人机成本
        drone_cost = 0.0
        for i, village in enumerate(self.villages):
            if chromosome['drone_assignment'][i] == 0:
                continue

            vehicle_idx = int(chromosome['vehicle_assignment'][i])
            village_idx = self.location_indices.get(village)
            
            if village_idx is None or not isinstance(village_idx, int):
                return float('inf')

            # 选择起降点
            takeoff_options = [wulong_idx]
            if vehicle_routes[vehicle_idx]:
                for v in vehicle_routes[vehicle_idx]:
                    v_idx = self.location_indices.get(v)
                    if v_idx is not None and isinstance(v_idx, int):
                        takeoff_options.append(v_idx)

            # 过滤有效的起降点
            valid_takeoff_options = [x for x in takeoff_options if isinstance(x, int)]
            if not valid_takeoff_options:
                return float('inf')

            best_takeoff = min(valid_takeoff_options,
                             key=lambda x: self.distance_matrix[x, village_idx] if isinstance(x, int) else float('inf'))

            # 无人机成本计算
            demand_weight = self.demands[village]
            drone_feasible, energy_cost, fixed_cost, trips, flight_time = self._calculate_drone_cost(
                best_takeoff, village_idx, demand_weight)

            if not drone_feasible:
                return float('inf')

            drone_cost += energy_cost + fixed_cost + flight_time * self.drone_params['time_price']

        return total_vehicle_cost + drone_cost

    def _calculate_drone_cost(self, takeoff_idx: int, village_idx: int,
                            demand_weight: float) -> Tuple[bool, float, float, int, float]:
        """计算无人机单次配送成本"""
        if not isinstance(takeoff_idx, int) or not isinstance(village_idx, int):
            return False, 0.0, 0.0, 0, 0.0
            
        distance = self.distance_matrix[takeoff_idx, village_idx]

        # 航程约束
        if distance > self.drone_params['max_range']:
            return False, 0.0, 0.0, 0, 0.0

        # 计算架次
        trips = max(1, int(np.ceil(demand_weight / self.drone_params['max_payload'])))

        # 每架次成本
        energy_per_trip = (self.drone_params['power_kwh_per_km_base'] +
                          self.drone_params['power_kwh_per_km_slope'] *
                          (demand_weight / trips) / self.drone_params['max_payload']) * 2 * distance

        total_energy = energy_per_trip * trips
        total_fixed = trips * self.drone_params['trip_fixed_cost']
        total_time = (2 * distance / self.drone_params['speed']) * trips

        # 电池容量约束
        if total_energy > self.drone_params['battery_capacity'] * trips:
            return False, 0.0, 0.0, 0, 0.0

        return True, total_energy * self.drone_params['electricity_price'], total_fixed, trips, total_time

    def crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """交叉操作"""
        if random.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()

        # 单点交叉
        crossover_point = random.randint(1, self.num_villages - 1)

        child1_chromosome = {}
        child2_chromosome = {}

        for key in parent1.chromosome.keys():
            if isinstance(parent1.chromosome[key], np.ndarray):
                child1_chromosome[key] = np.concatenate([
                    parent1.chromosome[key][:crossover_point],
                    parent2.chromosome[key][crossover_point:]
                ])
                child2_chromosome[key] = np.concatenate([
                    parent2.chromosome[key][:crossover_point],
                    parent1.chromosome[key][crossover_point:]
                ])
            else:
                child1_chromosome[key] = parent1.chromosome[key]
                child2_chromosome[key] = parent2.chromosome[key]

        return Individual(child1_chromosome), Individual(child2_chromosome)

    def mutate(self, individual: Individual) -> Individual:
        """变异操作"""
        mutated = individual.copy()
        chromosome = mutated.chromosome

        # 车辆分配变异
        if random.random() < self.mutation_rate:
            idx = random.randint(0, self.num_villages - 1)
            chromosome['vehicle_assignment'][idx] = random.randint(0, self.num_vehicles - 1)

        # 无人机分配变异
        if random.random() < self.mutation_rate:
            idx = random.randint(0, self.num_villages - 1)
            chromosome['drone_assignment'][idx] = 1 - chromosome['drone_assignment'][idx]

        # 路径顺序变异
        if random.random() < self.mutation_rate:
            idx1, idx2 = random.sample(range(self.num_villages), 2)
            chromosome['route_order'][idx1], chromosome['route_order'][idx2] = \
                chromosome['route_order'][idx2], chromosome['route_order'][idx1]

        return mutated

    def select_parents(self, population: List[Individual], fitness_values: List[float]) -> Tuple[Individual, Individual]:
        """轮盘赌选择父代个体"""
        # 转换适应度为权重（适应度越小越好，所以要反转）
        fitness_array = np.array(fitness_values)
        
        # 处理无穷大值
        finite_mask = np.isfinite(fitness_array)
        if not finite_mask.any():
            # 如果都是无穷大，随机选择
            idx1, idx2 = np.random.choice(len(population), 2, replace=False)
            return population[idx1], population[idx2]
        
        # 只考虑有限值
        min_finite_fitness = np.min(fitness_array[finite_mask])
        max_finite_fitness = np.max(fitness_array[finite_mask])
        
        # 转换为权重（越小的适应度权重越大）
        if max_finite_fitness == min_finite_fitness:
            # 如果所有适应度相等，均匀权重
            weights = np.ones(len(population))
        else:
            weights = np.where(finite_mask, 
                             max_finite_fitness - fitness_array + 1e-10,
                             0.0)
        
        # 归一化权重
        weights = weights / np.sum(weights)
        
        # 选择两个父代
        parent_indices = np.random.choice(len(population), 2, p=weights, replace=False)
        return population[parent_indices[0]], population[parent_indices[1]]

    def optimize(self, initial_population: Optional[List[Individual]] = None) -> Tuple[Individual, List[float]]:
        """
        优化方法（为了兼容性）
        """
        return self.evolve(initial_population)


# 便捷函数
def create_vehicle_drone_optimizer(locations: Dict[str, Tuple[float, float]],
                                 demands: Dict[str, float],
                                 distance_matrix: Optional[np.ndarray] = None,
                                 drone_distance_matrix: Optional[np.ndarray] = None,
                                 **kwargs) -> VehicleDroneGA:
    """
    创建车辆-无人机配送优化器
    
    Args:
        locations: 位置字典
        demands: 需求字典（只包含村庄，不包括五龙镇中转站）
        distance_matrix: 可选的车辆距离矩阵
        drone_distance_matrix: 可选的无人机距离矩阵
        **kwargs: 其他参数
        
    Returns:
        VehicleDroneGA实例
    """
    vehicle_params = get_config('vehicle_params', {})
    drone_params = get_config('drone_params', {})
    ga_params = get_config('ga_params', {})

    # 合并参数，传入的参数优先
    optimizer_params = {**ga_params}
    for key, value in kwargs.items():
        if key not in ['distance_matrix', 'drone_distance_matrix']:
            optimizer_params[key] = value

    # 处理距离矩阵
    if distance_matrix is None:
        # 创建默认距离矩阵
        try:
            from ..utils.geographic_utils import GeographicCalculator
        except ImportError:
            try:
                from utils.geographic_utils import GeographicCalculator
            except ImportError:
                import sys
                import os
                current_dir = os.path.dirname(__file__)
                parent_dir = os.path.dirname(current_dir)
                sys.path.insert(0, parent_dir)
                from utils.geographic_utils import GeographicCalculator
        
        calc = GeographicCalculator()
        distance_matrix = calc.calculate_distance_matrix(locations)
        
        # 记录使用默认距离矩阵
        logger = logging.getLogger(__name__)
        logger.info("使用默认坐标计算的距离矩阵")
    else:
        # 记录使用传入的距离矩阵
        logger = logging.getLogger(__name__)
        logger.info(f"使用传入的距离矩阵，形状: {distance_matrix.shape}")

    return VehicleDroneGA(
        locations=locations,
        demands=demands,
        vehicle_params=vehicle_params,
        drone_params=drone_params,
        distance_matrix=distance_matrix,
        **optimizer_params
    )
