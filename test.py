#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修改后的车辆-无人机协同配送模型
"""

import sys
import os
import numpy as np

# 添加当前目录到Python路径
sys.path.append(os.getcwd())

try:
    from code_1 import VehicleDroneDeliveryOptimizer
    
    print("=== 测试修改后的车辆-无人机协同配送模型 ===")
    
    # 创建优化器实例
    optimizer = VehicleDroneDeliveryOptimizer()
    
    print("\n1. 测试新的能耗公式:")
    print("-" * 30)
    
    # 测试不同载重下的能耗
    test_weights = [10, 30, 50, 70, 80]  # kg
    for weight in test_weights:
        # 实际耗电（kWh/km）= 0.164 + 0.191 ×（实际载重 / 80）
        energy_consumption = 0.164 + 0.191 * (weight / 80)
        print(f"载重 {weight}kg: 能耗 {energy_consumption:.3f} kWh/km")
    
    print("\n2. 测试个体创建:")
    print("-" * 30)
    
    # 测试创建几个个体
    for i in range(3):
        individual = optimizer._create_individual()
        fitness = optimizer._calculate_fitness(individual)
        print(f"个体 {i+1}: 适应度 = {fitness:.2f}")
        
        # 检查个体结构
        customers = list(optimizer.demands.keys())
        vehicle_count = len(set(individual['vehicle_assignment']))
        drone_count = np.sum(individual['drone_assignment'])
        print(f"  车辆分配: {vehicle_count} 种, 无人机分配: {drone_count} 个")
    
    print("\n3. 测试适应度计算:")
    print("-" * 30)
    
    # 创建一个简单的测试个体
    test_individual = optimizer._create_individual()
    
    # 手动设置一些合理的分配
    customers = list(optimizer.demands.keys())
    test_individual['vehicle_assignment'] = np.array([0, 0, 1, 1, 2] + [0] * (len(customers) - 5))
    test_individual['drone_assignment'] = np.zeros(len(customers), dtype=int)
    test_individual['drone_assignment'][5:10] = 1  # 前5个村庄使用无人机
    
    fitness = optimizer._calculate_fitness(test_individual)
    print(f"测试个体适应度: {fitness:.2f}")
    
    if np.isinf(fitness):
        print("警告：适应度为无穷大，可能存在约束违反")
    else:
        print("✓ 适应度计算正常")
    
    print("\n4. 测试小规模优化:")
    print("-" * 30)
    
    # 临时减小种群规模和代数进行快速测试
    original_pop_size = optimizer.population_size
    original_generations = optimizer.generations
    
    optimizer.population_size = 20
    optimizer.generations = 10
    
    try:
        best_solution, best_fitness, fitness_history = optimizer.optimize()
        print(f"小规模优化完成，最优适应度: {best_fitness:.2f}")
        
        if np.isinf(best_fitness):
            print("警告：最优解仍为无穷大")
        else:
            print("✓ 优化过程正常")
            
            # 分析解决方案
            analysis_result = optimizer.analyze_solution(best_solution)
            
            print(f"\n5. 解决方案分析:")
            print(f"车辆直接配送村庄数: {sum(len(route) for route in analysis_result['vehicle_routes'])}")
            print(f"无人机配送村庄数: {len(analysis_result['drone_deliveries'])}")
            print(f"携带无人机车辆数: {sum(analysis_result['vehicle_has_drone'])}")
            print(f"车辆燃油成本: {sum(dist * optimizer.vehicle_params['fuel_consumption'] * optimizer.vehicle_params['fuel_price'] for dist in analysis_result['vehicle_distances']):.2f} 元")
            print(f"无人机电力成本: {analysis_result['drone_cost']:.2f} 元")
            
    except Exception as e:
        print(f"优化过程出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 恢复原始参数
        optimizer.population_size = original_pop_size
        optimizer.generations = original_generations
    
    print("\n6. 测试约束检查:")
    print("-" * 30)
    
    # 测试车辆容量约束
    total_demand = sum(optimizer.demands.values()) * optimizer.package_weight
    vehicle_capacity = optimizer.vehicle_params['capacity']
    print(f"总需求重量: {total_demand:.1f} kg")
    print(f"单车容量: {vehicle_capacity} kg")
    print(f"车辆数量: {optimizer.vehicle_params['num_vehicles']}")
    print(f"总容量: {vehicle_capacity * optimizer.vehicle_params['num_vehicles']} kg")
    
    if total_demand <= vehicle_capacity * optimizer.vehicle_params['num_vehicles']:
        print("✓ 车辆容量约束可满足")
    else:
        print("⚠ 车辆容量可能不足")
    
    # 测试无人机电池容量约束
    print(f"无人机电池容量: {optimizer.drone_params['battery_capacity']} kWh")
    
    # 测试最远距离的无人机配送
    max_distance = 0
    for customer in customers:
        customer_idx = list(optimizer.locations.keys()).index(customer)
        air_distance = optimizer._air_distance(0, customer_idx)
        if air_distance > max_distance:
            max_distance = air_distance
    
    max_weight = optimizer.drone_params['max_payload']
    # 使用新的能耗公式
    energy_consumption_per_km = 0.164 + 0.191 * (max_weight / 80)
    max_energy_required = energy_consumption_per_km * max_distance
    
    print(f"最远距离: {max_distance:.2f} km")
    print(f"最大能耗: {energy_consumption_per_km:.3f} kWh/km")
    print(f"最大能量需求: {max_energy_required:.3f} kWh")
    
    if max_energy_required <= optimizer.drone_params['battery_capacity']:
        print("✓ 无人机电池容量约束可满足")
    else:
        print("⚠ 无人机电池容量可能不足")
    
    print("\n=== 测试完成 ===")
    
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保code_1.py文件存在且语法正确")
except Exception as e:
    print(f"测试过程中出现错误: {e}")
    import traceback
    traceback.print_exc()
