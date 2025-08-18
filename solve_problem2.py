import numpy as np
import pandas as pd
import random
import math
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt
import seaborn as sns

# 中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


time_tag = 0.56
# ========= 时间约束评估函数 ========= #
def T_avg(x):
    if 0<=x and x<=1:
        return 1
    elif 1<x and x<1.5:
        return (1.5-x)/0.5   
    else:
        return 0

def T_max(x):
    if 0<=x and x<=1.5:
        return 1
    elif 1.5<x and x<2:
        return (2-x)/0.5

    else:
        return 0


def R_high(x):
    if 0<=x and x<=0.5  :
        return 0
    elif 0.5<x and x<0.9:
        return (x-0.5)/0.4
    else:
        return 1

def evaluate_time_constraint(delivery_times):
    """
    评估时间约束的可行性
    Args:
        delivery_times: 字典，村庄名称 -> 配送时间(小时)
    Returns:
        bool: True表示满足时间约束，False表示不满足
    """
    if not delivery_times:
        return True
    
    t_avg = sum(delivery_times.values()) / len(delivery_times)  # 平均配送时间
    t_max = max(delivery_times.values())  # 最大配送时间
    t_tag = 2.0  # 时间阈值（调整为更合理的值）
    
    # 计算按时配送的村庄比例
    t_m = sum(1 for time in delivery_times.values() if time < t_tag) / len(delivery_times)
    
    # 模糊逻辑评估
    m = 0.444 * T_avg(t_avg) + 0.184 * T_max(t_max) + 0.372 * R_high(t_m)
    
    # 判断是否满足约束
    return m 

class VehicleDroneDeliveryOptimizer:
    """车辆-无人机协同配送路径优化器（含固定成本+时间成本+时间软/硬约束）"""
    
    def __init__(self):
        # ---------------- 基础数据 ---------------- #
        self.locations = {
            "配送中心": (35.8236, 113.9715),  # 真正的配送中心
            "五龙镇": (35.7828, 113.9398),  # 五龙镇作为中间配送点
            "丰峪村": (35.8015, 113.9395),
            "上庄村": (35.7951, 113.9582),
            "泽下村": (35.7912, 113.9786),
            "文峪村": (35.8153, 113.9841),
            "罗圈村": (35.8288, 113.9501),
            "城峪村": (35.8142, 113.9213),
            "岭后村": (35.7984, 113.8997),
            "荷花村": (35.7835, 113.8824),
            "渔村": (35.7681, 113.8763),
            "合脉掌村": (35.7533, 113.8902),
            "碾上村": (35.7486, 113.9154),
            "长坡村": (35.7352, 113.9301),
            "南沃村": (35.7411, 113.9576),
            "西蒋村": (35.7630, 113.9688),
            "岭南村": (35.7789, 113.9912),
            "桑峪村": (35.7925, 114.0105),
            "马兰村": (35.7833, 114.0500),
            "中石阵村": (35.7596, 114.0321),
            "栗家洼村": (35.7402, 114.0185),
            "牛家岗村": (35.7268, 114.0011),
            "陈家岗村": (35.7185, 113.9753),
            "薛家岗村": (35.7093, 113.9502),
            "石官村": (35.6987, 113.9314),
            "阳和村": (35.6859, 113.9188),
            "七峪村": (35.6734, 113.9017)
        }

        # 各村快递需求量 - 五龙镇的需求量为3012件
        self.demands = {
            "石官村": 266, "中石阵村": 246, "阳和村": 221, "碾上村": 183, "泽下村": 170,
            "七峪村": 147, "渔村": 142, "合脉掌村": 142, "桑峪村": 141, "荷花村": 132,
            "西蒋村": 125, "岭后村": 123, "五龙镇": 3012, "上庄村": 109, "罗圈村": 99,
            "南沃村": 85, "丰峪村": 84, "岭南村": 83, "马兰村": 82, "城峪村": 80,
            "牛家岗村": 66, "陈家岗村": 65, "薛家岗村": 65, "长坡村": 62, "文峪村": 47, "栗家洼村": 47
        }

        self.package_weight = 0.5  # kg/件

        # ---------------- 车辆参数 ---------------- #
        self.vehicle_params = {
            'fuel_consumption': 0.252,  # L/km
            'fuel_price': 6.89,         # 元/L
            'speed': 50.0,              # km/h
            'capacity': 1500.0,         # kg
            'num_vehicles': 3
        }
        # 司机时间价值 & 工时上限
        self.driver_time_price = 60.0     # 元/小时（时间成本）
        self.vehicle_max_hours = 8.0      # 每辆车最大工时
        # 车辆固定成本
        self.VEHICLE_DEPLOY_FIXED_COST = 20.0  # 元/车次（只要出车一次就计）

        # ---------------- 无人机参数 ---------------- #
        self.drone_params = {
            'max_payload': 80.0,        # kg（货物）
            'max_range': 12.0,          # km（去程满载）
            'empty_range': 26.0,        # km（回程空载）
            'speed': 60.0,              # km/h
            'battery_capacity': 2.132,  # kWh
            'electricity_price': 0.6,   # 元/kWh
            'weight': 10.0              # kg（机体）
        }
        self.drone_time_price = 20.0      # 元/小时
        self.drone_max_hours = 8.0        # 无人机总作业上限（可理解为一天内可用时长）
        self.DRONE_TRIP_FIXED_COST = 5.0  # 元/架次

        # 时间软/硬约束控制
        self.PENALTY_TIME = 200.0            # 超时惩罚权重（元/小时）
        self.USE_HARD_TIME_CONSTRAINT = False  # True 则超时直接判 infeasible

        # ---------------- 距离矩阵 ---------------- #
        self.distance_matrix = self._calculate_distance_matrix()      # 空中直线
        self.vehicle_distance_matrix = self._load_vehicle_distances() # 公路距离（Excel 或 1.2×直线）

        # ---------------- GA 参数 ---------------- #
        self.population_size = 150
        self.generations = 500
        self.mutation_rate = 0.25
        self.crossover_rate = 0.85

    # ========= 距离与载荷 ========= #
    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 6371.0
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1,lon1,lat2,lon2])
        dlon = lon2 - lon1; dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
        return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

    def _calculate_distance_matrix(self):
        locs = list(self.locations.keys())
        n = len(locs)
        M = np.zeros((n,n))
        for i in range(n):
            for j in range(n):
                if i==j: continue
                lat1,lon1 = self.locations[locs[i]]
                lat2,lon2 = self.locations[locs[j]]
                M[i,j] = self._haversine(lat1,lon1,lat2,lon2)
        return M

    def _load_vehicle_distances(self):
        """读取“物流车配送距离.xlsx”，若缺失用直线×1.2"""
        try:
            df = pd.read_excel('物流车配送距离.xlsx')
            df.set_index('Unnamed: 0', inplace=True)
            locs = list(self.locations.keys())
            n = len(locs)
            M = np.zeros((n,n))
            for i,a in enumerate(locs):
                for j,b in enumerate(locs):
                    if i==j: continue
                    try:
                        val = df.loc[a,b]
                        if pd.isna(val): val = self.distance_matrix[i,j]*1.2
                        M[i,j] = float(val)
                    except:
                        M[i,j] = self.distance_matrix[i,j]*1.2
            print("成功加载物流车实际道路距离数据")
            return M
        except Exception as e:
            print(f"读取物流车距离数据失败: {e}\n使用直线距离的1.2倍作为替代")
            return self.distance_matrix * 1.2

    def _road_distance(self,i,j):  return self.vehicle_distance_matrix[i][j]
    def _air_distance(self,i,j):   return self.distance_matrix[i][j]

    # ========= 无人机单村成本（含时间） ========= #
    def _drone_cost_time_for_customer(self, depot_idx:int, takeoff_idx:int, customer_idx:int, demand_weight:float):
        """
        返回：(feasible, 电费元, 固定成本元, 架次数, 总飞行时长h)
        规则：将需求分割为若干架次（<=80kg/架），每架次往返距离=2*空中距离；
              用线性功耗模型估算每架次能耗（kWh/km = 0.164 + 0.191*((机体+载荷)/80)）
              电池容量逐架次校验；时间=距离/速度。
        """
        dist_oneway = self._air_distance(takeoff_idx, customer_idx)
        # 航程约束（去程用满载max_range，回程用empty_range；此处对称距离）
        if dist_oneway > self.drone_params['max_range'] or dist_oneway > self.drone_params['empty_range']:
            return False, 0.0, 0.0, 0, 0.0
        trips = max(1, math.ceil(demand_weight / self.drone_params['max_payload']))
        per_load = demand_weight / trips
        total_energy_cost = 0.0
        total_time_h = 0.0
        for _ in range(trips):
            kwh_per_km = 0.164 + 0.191 * ((self.drone_params['weight'] + per_load)/80.0)
            trip_distance = 2.0 * dist_oneway  # 往返
            trip_energy = kwh_per_km * trip_distance
            # 电池容量约束（单架次）
            if trip_energy > self.drone_params['battery_capacity']:
                return False, 0.0, 0.0, 0, 0.0
            total_energy_cost += trip_energy * self.drone_params['electricity_price']
            total_time_h += trip_distance / self.drone_params['speed']
        fixed_cost = trips * self.DRONE_TRIP_FIXED_COST
        return True, total_energy_cost, fixed_cost, trips, total_time_h

    # ========= 个体编码/变异/交叉 ========= #
    def _create_individual(self):
        customers = list(self.demands.keys())
        # 移除配送中心和五龙镇，只考虑村庄
        customers = [c for c in customers if c not in ["配送中心", "五龙镇"]]
        
        ind = {
            'vehicle_assignment': np.random.randint(0, self.vehicle_params['num_vehicles'], len(customers)),
            'drone_assignment': np.zeros(len(customers), dtype=int),
            'route_order': np.random.permutation(len(customers))
        }
        # 启发式：远且轻尝试无人机
        wulong_idx = list(self.locations.keys()).index("五龙镇")
        for i,c in enumerate(customers):
            c_idx = list(self.locations.keys()).index(c)
            d = self._air_distance(wulong_idx, c_idx)
            w = self.demands[c]*self.package_weight
            if (d>5 and w<=self.drone_params['max_payload'] and np.random.random()<0.4):
                ind['drone_assignment'][i]=1
        return ind

    def _crossover(self, p1, p2):
        if random.random()>self.crossover_rate: return p1,p2
        cp = random.randint(1, len(p1['vehicle_assignment'])-1)
        c1, c2 = {}, {}
        c1['vehicle_assignment'] = np.concatenate([p1['vehicle_assignment'][:cp], p2['vehicle_assignment'][cp:]])
        c2['vehicle_assignment'] = np.concatenate([p2['vehicle_assignment'][:cp], p1['vehicle_assignment'][cp:]])
        c1['drone_assignment']   = np.concatenate([p1['drone_assignment'][:cp],   p2['drone_assignment'][cp:]])
        c2['drone_assignment']   = np.concatenate([p2['drone_assignment'][:cp],   p1['drone_assignment'][cp:]])
        c1['route_order'] = p1['route_order'].copy()
        c2['route_order'] = p2['route_order'].copy()
        return c1,c2

    def _mutate(self, ind):
        if random.random()<self.mutation_rate:
            i = random.randint(0, len(ind['vehicle_assignment'])-1)
            ind['vehicle_assignment'][i] = random.randint(0, self.vehicle_params['num_vehicles']-1)
        if random.random()<self.mutation_rate:
            i = random.randint(0, len(ind['drone_assignment'])-1)
            ind['drone_assignment'][i] = 1 - ind['drone_assignment'][i]
        if random.random()<self.mutation_rate:
            i,j = random.sample(range(len(ind['route_order'])),2)
            ind['route_order'][i],ind['route_order'][j] = ind['route_order'][j],ind['route_order'][i]
        return ind

    # ========= 适应度：成本 + 时间成本 + 软约束惩罚 ========= #
    def _calculate_fitness(self, ind):
        customers = list(self.demands.keys())
        # 移除配送中心和五龙镇，只考虑村庄
        customers = [c for c in customers if c not in ["配送中心", "五龙镇"]]
        
        # 配送中心到五龙镇的距离和成本
        depot_idx = list(self.locations.keys()).index("配送中心")
        wulong_idx = list(self.locations.keys()).index("五龙镇")
        depot_to_wulong_distance = self._road_distance(depot_idx, wulong_idx)
        total_demand_weight = sum(self.demands[c] * self.package_weight for c in customers)
        depot_transport_cost = depot_to_wulong_distance * self.vehicle_params['fuel_consumption'] * self.vehicle_params['fuel_price']
        depot_time_cost = (depot_to_wulong_distance / self.vehicle_params['speed']) * self.driver_time_price
        depot_fixed_cost = self.VEHICLE_DEPLOY_FIXED_COST

        # 车辆数据
        nV = self.vehicle_params['num_vehicles']
        vehicle_routes = [[] for _ in range(nV)]
        vehicle_loads  = [0.0]*nV
        vehicle_used   = [False]*nV
        vehicle_has_dr = [False]*nV  # 是否携机
        # 分配
        for i,c in enumerate(customers):
            v = int(ind['vehicle_assignment'][i])
            if ind['drone_assignment'][i]==0:
                vehicle_routes[v].append(c)
                vehicle_loads[v] += self.demands[c]*self.package_weight
            else:
                vehicle_has_dr[v] = True

        # 容量约束
        for v in range(nV):
            if vehicle_loads[v] > self.vehicle_params['capacity']:
                return float('inf')

        total_cost = depot_transport_cost + depot_time_cost + depot_fixed_cost
        total_vehicle_time = depot_to_wulong_distance / self.vehicle_params['speed']
        # 车辆行驶与时间成本 + 车辆固定成本
        for v in range(nV):
            used = (len(vehicle_routes[v])>0) or vehicle_has_dr[v]
            if not used: continue
            vehicle_used[v] = True
            dist = 0.0
            cur = wulong_idx  # 从五龙镇出发
            if vehicle_routes[v]:
                for c in vehicle_routes[v]:
                    c_idx = list(self.locations.keys()).index(c)
                    dist += self._road_distance(cur, c_idx); cur = c_idx
                dist += self._road_distance(cur, wulong_idx)  # 返回五龙镇
            else:
                # 仅携机：驶到该车负责的无人机服务中最远点的附近（近似）
                max_d = 0.0; best = wulong_idx
                for i,c in enumerate(customers):
                    if ind['drone_assignment'][i]==1 and int(ind['vehicle_assignment'][i])==v:
                        c_idx = list(self.locations.keys()).index(c)
                        d = self._air_distance(wulong_idx, c_idx)
                        if d>max_d: max_d=d; best=c_idx
                if max_d>0: dist = 2.0*self._road_distance(wulong_idx, best)
            # 燃油成本
            fuel = dist * self.vehicle_params['fuel_consumption'] * self.vehicle_params['fuel_price']
            # 时间（小时）
            t_h = dist / self.vehicle_params['speed']
            # 时间成本
            time_cost = t_h * self.driver_time_price
            # 固定成本
            deploy_cost = self.VEHICLE_DEPLOY_FIXED_COST
            total_cost += (fuel + time_cost + deploy_cost)
            total_vehicle_time += t_h

            # 工时约束（软/硬）
            if t_h > self.vehicle_max_hours:
                if self.USE_HARD_TIME_CONSTRAINT:
                    return float('inf')
                total_cost += (t_h - self.vehicle_max_hours) * self.PENALTY_TIME

        # 无人机成本与时间
        drone_energy_cost = 0.0
        drone_fixed_cost  = 0.0
        drone_total_time  = 0.0
        for i,c in enumerate(customers):
            if ind['drone_assignment'][i]==0: continue
            v = int(ind['vehicle_assignment'][i])
            c_idx = list(self.locations.keys()).index(c)
            # 选择起降点：优先该车直送点，否则五龙镇
            candidates = [wulong_idx]
            for j,other in enumerate(customers):
                if (ind['drone_assignment'][j]==0 and int(ind['vehicle_assignment'][j])==v):
                    candidates.append(list(self.locations.keys()).index(other))
            takeoff_idx = min(candidates, key=lambda x: self._air_distance(x, c_idx))
            w = self.demands[c]*self.package_weight
            feasible, e_cost, f_cost, trips, t_h = self._drone_cost_time_for_customer(
                wulong_idx, takeoff_idx, c_idx, w
            )
            if not feasible:
                return float('inf')
            drone_energy_cost += e_cost
            drone_fixed_cost  += f_cost
            drone_total_time  += t_h

        # 无人机时间成本与上限（总作业时长）
        total_cost += drone_total_time * self.drone_time_price
        if drone_total_time > self.drone_max_hours:
            if self.USE_HARD_TIME_CONSTRAINT:
                return float('inf')
            total_cost += (drone_total_time - self.drone_max_hours) * self.PENALTY_TIME

        # ========= 计算各村庄配送时间并评估时间约束 ========= #
        delivery_times = {}  # 存储每个村庄的配送时间
        
        # 配送中心到五龙镇的时间
        depot_to_wulong_time = depot_to_wulong_distance / self.vehicle_params['speed']
        
        # 计算车辆配送村庄的时间
        for v in range(nV):
            if not vehicle_used[v] or not vehicle_routes[v]:
                continue
                
            # 车辆从五龙镇出发的时间
            vehicle_start_time = depot_to_wulong_time
            
            # 计算车辆路径上每个村庄的到达时间
            current_time = vehicle_start_time
            current_pos = wulong_idx
            
            for c in vehicle_routes[v]:
                c_idx = list(self.locations.keys()).index(c)
                # 从当前位置到村庄c的时间
                travel_time = self._road_distance(current_pos, c_idx) / self.vehicle_params['speed']
                current_time += travel_time
                delivery_times[c] = current_time
                current_pos = c_idx
        
        # 计算无人机配送村庄的时间
        for i, c in enumerate(customers):
            if ind['drone_assignment'][i] == 0:
                continue
                
            v = int(ind['vehicle_assignment'][i])
            c_idx = list(self.locations.keys()).index(c)
            
            # 确定起降点
            candidates = [wulong_idx]
            for j, other in enumerate(customers):
                if (ind['drone_assignment'][j] == 0 and int(ind['vehicle_assignment'][j]) == v):
                    candidates.append(list(self.locations.keys()).index(other))
            takeoff_idx = min(candidates, key=lambda x: self._air_distance(x, c_idx))
            
            # 无人机起飞时间：车辆到达起降点的时间
            if takeoff_idx == wulong_idx:
                # 从五龙镇起飞
                drone_start_time = depot_to_wulong_time
            else:
                # 从其他村庄起飞，需要车辆先到达该村庄
                takeoff_village = list(self.locations.keys())[takeoff_idx]
                if takeoff_village in delivery_times:
                    drone_start_time = delivery_times[takeoff_village]
                else:
                    # 如果起降点村庄还没有被配送，使用五龙镇时间
                    drone_start_time = depot_to_wulong_time
            
            # 无人机飞行时间
            w = self.demands[c] * self.package_weight
            feasible, e_cost, f_cost, trips, drone_flight_time = self._drone_cost_time_for_customer(
                wulong_idx, takeoff_idx, c_idx, w
            )
            
            # 村庄c的配送时间 = 无人机起飞时间 + 飞行时间
            delivery_times[c] = drone_start_time + drone_flight_time
        
        # 评估时间约束
        if evaluate_time_constraint(delivery_times)<time_tag:
            total_cost += 200  # 不满足时间约束，总成本增加200元

        return total_cost

    # ========= 遗传算法主流程 ========= #
    def optimize(self):
        print("开始车辆-无人机协同配送路径优化（含时间成本）...")
        print("配送中心 → 五龙镇 → 各村庄")
        pop = [self._create_individual() for _ in range(self.population_size)]
        best_sol, best_fit = None, float('inf')
        history = []
        for g in range(self.generations):
            fits = [self._calculate_fitness(ind) for ind in pop]
            min_idx = int(np.argmin(fits))
            if fits[min_idx] < best_fit:
                best_fit = fits[min_idx]
                best_sol = {k:(v.copy() if isinstance(v, np.ndarray) else v) for k,v in pop[min_idx].items()}
            history.append(best_fit)
            if g%20==0:
                print(f"第 {g} 代，最优目标（含时间）: {best_fit:.2f} 元")

            arr = np.array(fits)
            if np.all(np.isinf(arr)):
                print("警告：全体不可行，重置种群")
                pop = [self._create_individual() for _ in range(self.population_size)]
                continue
            max_finite = np.max(arr[np.isfinite(arr)])
            arr = np.where(np.isinf(arr), max_finite*10, arr)
            arr = np.max(arr) - arr + 1
            probs = arr/arr.sum() if np.isfinite(arr).all() else np.ones(len(pop))/len(pop)

            new_pop=[]
            elite = max(1, int(0.1*self.population_size))
            elite_idx = np.argsort(arr)[-elite:]
            for idx in elite_idx:
                new_pop.append({k:(v.copy() if isinstance(v,np.ndarray) else v) for k,v in pop[idx].items()})
            while len(new_pop)<self.population_size:
                p1 = pop[np.random.choice(len(pop), p=probs)]
                p2 = pop[np.random.choice(len(pop), p=probs)]
                c1,c2 = self._crossover(p1,p2)
                new_pop.append(self._mutate(c1))
                if len(new_pop)<self.population_size:
                    new_pop.append(self._mutate(c2))
            pop = new_pop
        print(f"优化完成！最优目标（含时间）: {best_fit:.2f} 元")
        
        # 如果没有找到有效解，创建一个默认解
        if best_sol is None:
            print("警告：未找到有效解，创建默认解")
            customers = list(self.demands.keys())
            customers = [c for c in customers if c not in ["配送中心", "五龙镇"]]
            
            best_sol = {
                'vehicle_assignment': np.zeros(len(customers), dtype=int),  # 所有客户分配给车辆0
                'drone_assignment': np.zeros(len(customers), dtype=int),  # 不使用无人机
                'route_order': np.arange(len(customers))
            }
            best_fit = self._calculate_fitness(best_sol)
        
        return best_sol, best_fit, history

    # ========= 结果分析（含时间拆解） ========= #
    def analyze_solution(self, sol):
        customers = list(self.demands.keys())
        # 移除配送中心和五龙镇，只考虑村庄
        customers = [c for c in customers if c not in ["配送中心", "五龙镇"]]
        
        depot = "配送中心"
        wulong = "五龙镇"
        depot_idx = list(self.locations.keys()).index(depot)
        wulong_idx = list(self.locations.keys()).index(wulong)
        nV = self.vehicle_params['num_vehicles']

        vehicle_routes = [[] for _ in range(nV)]
        vehicle_loads  = [0.0]*nV
        vehicle_dists  = [0.0]*nV
        vehicle_times  = [0.0]*nV
        vehicle_used   = [False]*nV
        vehicle_has_dr = [False]*nV

        drone_list = []  # (村, 归属车)
        for i,c in enumerate(customers):
            v = int(sol['vehicle_assignment'][i])
            if sol['drone_assignment'][i]:
                drone_list.append((c,v)); vehicle_has_dr[v]=True
            else:
                vehicle_routes[v].append(c)
                vehicle_loads[v] += self.demands[c]*self.package_weight

        # 车辆距离、时间、成本
        # 计算配送中心到五龙镇的运输成本
        depot_to_wulong_distance = self._road_distance(depot_idx, wulong_idx)
        total_demand_weight = sum(self.demands[c] * self.package_weight for c in customers)
        depot_transport_cost = depot_to_wulong_distance * self.vehicle_params['fuel_consumption'] * self.vehicle_params['fuel_price']
        depot_time_cost = (depot_to_wulong_distance / self.vehicle_params['speed']) * self.driver_time_price
        depot_fixed_cost = self.VEHICLE_DEPLOY_FIXED_COST
        
        print(f"\n配送中心到五龙镇运输:")
        print(f"  距离: {depot_to_wulong_distance:.2f} km")
        print(f"  总重量: {total_demand_weight:.1f} kg")
        print(f"  运输成本: {depot_transport_cost:.2f} 元")
        print(f"  时间成本: {depot_time_cost:.2f} 元")
        print(f"  固定成本: {depot_fixed_cost:.2f} 元")
        print()

        vehicle_fuel_cost = depot_transport_cost
        vehicle_fixed_cost = depot_fixed_cost
        vehicle_time_cost = depot_time_cost
        for v in range(nV):
            used = (len(vehicle_routes[v])>0) or vehicle_has_dr[v]
            if not used: continue
            vehicle_used[v]=True
            dist=0.0; cur=wulong_idx  # 从五龙镇出发
            if vehicle_routes[v]:
                for c in vehicle_routes[v]:
                    c_idx = list(self.locations.keys()).index(c)
                    dist += self._road_distance(cur, c_idx); cur=c_idx
                dist += self._road_distance(cur, wulong_idx)  # 返回五龙镇
            else:
                max_d=0.0; best=wulong_idx
                for c, vv in drone_list:
                    if vv!=v: continue
                    c_idx = list(self.locations.keys()).index(c)
                    d = self._air_distance(wulong_idx, c_idx)
                    if d>max_d: max_d=d; best=c_idx
                if max_d>0: dist = 2.0*self._road_distance(wulong_idx, best)
            vehicle_dists[v]=dist
            t = dist / self.vehicle_params['speed']
            vehicle_times[v]=t
            fuel = dist * self.vehicle_params['fuel_consumption'] * self.vehicle_params['fuel_price']
            vehicle_fuel_cost += fuel
            vehicle_time_cost += t * self.driver_time_price
            vehicle_fixed_cost += self.VEHICLE_DEPLOY_FIXED_COST

        # 无人机时间、成本
        drone_energy_cost=0.0
        drone_fixed_cost=0.0
        drone_total_time=0.0
        drone_rows=[]
        for c,v in drone_list:
            c_idx = list(self.locations.keys()).index(c)
            # 起降点：优先该车直送点，否则五龙镇
            candidates=[wulong_idx]
            for j,other in enumerate(customers):
                if sol['drone_assignment'][j]==0 and int(sol['vehicle_assignment'][j])==v:
                    candidates.append(list(self.locations.keys()).index(customers[j]))
            takeoff_idx = min(candidates, key=lambda x: self._air_distance(x, c_idx))
            w = self.demands[c]*self.package_weight
            feasible, e_cost, f_cost, trips, t_h = self._drone_cost_time_for_customer(
                wulong_idx, takeoff_idx, c_idx, w
            )
            drone_energy_cost += e_cost
            drone_fixed_cost  += f_cost
            drone_total_time  += t_h
            drone_rows.append((c, 2*self._air_distance(takeoff_idx, c_idx), w, e_cost, f_cost, trips, t_h))

        drone_time_cost = drone_total_time * self.drone_time_price

        # 计算每个村庄的配送时间Ti
        delivery_times = {}  # 存储每个村庄的配送时间
        
        # 配送中心到五龙镇的时间
        depot_to_wulong_time = depot_to_wulong_distance / self.vehicle_params['speed']
        
        # 计算车辆配送村庄的时间
        for v in range(nV):
            if not vehicle_used[v] or not vehicle_routes[v]:
                continue
                
            # 车辆从五龙镇出发的时间
            vehicle_start_time = depot_to_wulong_time
            
            # 计算车辆路径上每个村庄的到达时间
            current_time = vehicle_start_time
            current_pos = wulong_idx
            
            for c in vehicle_routes[v]:
                c_idx = list(self.locations.keys()).index(c)
                # 从当前位置到村庄c的时间
                travel_time = self._road_distance(current_pos, c_idx) / self.vehicle_params['speed']
                current_time += travel_time
                delivery_times[c] = current_time
                current_pos = c_idx
        
        # 计算无人机配送村庄的时间
        for c, v in drone_list:
            c_idx = list(self.locations.keys()).index(c)
            # 确定起降点
            candidates = [wulong_idx]
            for j, other in enumerate(customers):
                if sol['drone_assignment'][j] == 0 and int(sol['vehicle_assignment'][j]) == v:
                    candidates.append(list(self.locations.keys()).index(other))
            takeoff_idx = min(candidates, key=lambda x: self._air_distance(x, c_idx))
            
            # 无人机起飞时间：车辆到达起降点的时间
            if takeoff_idx == wulong_idx:
                # 从五龙镇起飞
                drone_start_time = depot_to_wulong_time
            else:
                # 从其他村庄起飞，需要车辆先到达该村庄
                takeoff_village = list(self.locations.keys())[takeoff_idx]
                if takeoff_village in delivery_times:
                    drone_start_time = delivery_times[takeoff_village]
                else:
                    # 如果起降点村庄还没有被配送，使用五龙镇时间
                    drone_start_time = depot_to_wulong_time
            
            # 无人机飞行时间
            w = self.demands[c] * self.package_weight
            feasible, e_cost, f_cost, trips, drone_flight_time = self._drone_cost_time_for_customer(
                wulong_idx, takeoff_idx, c_idx, w
            )
            
            # 村庄c的配送时间 = 无人机起飞时间 + 飞行时间
            delivery_times[c] = drone_start_time + drone_flight_time
        
        # 计算平均配送时间和最大配送时间
        if delivery_times:
            avg_delivery_time = sum(delivery_times.values()) / len(delivery_times)
            max_delivery_time = max(delivery_times.values())
        else:
            avg_delivery_time = 0
            max_delivery_time = 0
        
        # 打印配送时间信息
        print(f"\n=== 各村庄配送时间分析 ===")
        print("村庄名称\t\t配送时间(小时)")
        print("-" * 40)
        for village, time in sorted(delivery_times.items(), key=lambda x: x[1]):
            print(f"{village:<15}\t{time:.2f}")
        print("-" * 40)
        print(f"平均配送时间: {avg_delivery_time:.2f} 小时")
        print(f"最大配送时间: {max_delivery_time:.2f} 小时")
        print(f"配送村庄数量: {len(delivery_times)} 个")
         # 计算时间约束评估的详细指标
        t_tag = 2.0
        t_m = sum(1 for time in delivery_times.values() if time < t_tag) / len(delivery_times)
        m_value = 0.444 * T_avg(avg_delivery_time) + 0.084 * T_max(max_delivery_time) + 0.472 * R_high(t_m)
        print(f"m_value: {m_value:.3f}")
        # 评估时间约束
        time_constraint_satisfied = 1 if m_value>=time_tag else 0  # 1表示满足，0表示不满足

        print(f"时间约束评估: {'满足' if time_constraint_satisfied==1 else '不满足'}")
        
       

        print(f"时间约束评估值: {m_value:.3f} ")
        print(f"按时配送比例: {t_m:.3f} ({t_m*100:.1f}%)")
        print(f"t_avg: {avg_delivery_time:.2f}")
        print(f"t_max: {max_delivery_time:.2f}")
        print(f"t_m: {t_m:.3f}")
        print()

        # 超时惩罚（分析阶段仅展示，不加到下方"合计不含惩罚"里）
        vehicle_overtime_pen = sum(max(0.0, vehicle_times[v]-self.vehicle_max_hours)*self.PENALTY_TIME for v in range(nV))
        drone_overtime_pen   = max(0.0, drone_total_time-self.drone_max_hours)*self.PENALTY_TIME

        total_cost = (vehicle_fuel_cost + vehicle_fixed_cost + vehicle_time_cost +
                      drone_energy_cost + drone_fixed_cost + drone_time_cost)

        print("\n=== 解决方案分析（含时间） ===")
        print(f"配送中心: {depot}")
        print(f"中间配送点: {wulong}")
        print(f"车辆数量: {nV}")
        print()
        
        print("五龙镇物流车配送:")
        for v in range(nV):
            if vehicle_used[v]:
                print(f"车辆 {v+1}: 距离 {vehicle_dists[v]:.2f} km | 时间 {vehicle_times[v]:.2f} h | "
                      f"燃油 {vehicle_dists[v]*self.vehicle_params['fuel_consumption']*self.vehicle_params['fuel_price']:.2f} 元 | "
                      f"时间成本 {vehicle_times[v]*self.driver_time_price:.2f} 元 | 固定 {self.VEHICLE_DEPLOY_FIXED_COST:.2f} 元")
                if vehicle_routes[v]:
                    print("  直配送村:", ", ".join(vehicle_routes[v]))
                if vehicle_has_dr[v]:
                    print("  携带无人机: 是")
        print(f"\n无人机：总作业时间 {drone_total_time:.2f} h | 电费 {drone_energy_cost:.2f} 元 | 时间成本 {drone_time_cost:.2f} 元 | 固定 {drone_fixed_cost:.2f} 元")
        print(f"无人机配送村庄: {', '.join([c for c, _ in drone_list])}")
        print(f"无人机配送数量: {len(drone_list)} 个村庄")
        print(f"\n总成本（不含惩罚）: {total_cost:.2f} 元")
        if self.USE_HARD_TIME_CONSTRAINT:
            print("（已启用硬约束：任一超时将被判为不可行解）")
        else:
            print(f"时间超时惩罚（若有）：车辆 {vehicle_overtime_pen:.2f} 元，无人机 {drone_overtime_pen:.2f} 元")
            print(f"若计入惩罚的“软约束总目标”: {(total_cost+vehicle_overtime_pen+drone_overtime_pen):.2f} 元")

        return {
            'vehicle_routes': vehicle_routes,
            'vehicle_loads': vehicle_loads,
            'vehicle_distances': vehicle_dists,
            'vehicle_times': vehicle_times,
            'vehicle_has_drone': vehicle_has_dr,
            'drone_rows': drone_rows,  # (村, 往返km, 货重kg, 电费元, 固定元, 架次, 时间h)
            'vehicle_fuel_cost': vehicle_fuel_cost,
            'vehicle_fixed_cost': vehicle_fixed_cost,
            'vehicle_time_cost': vehicle_time_cost,
            'drone_energy_cost': drone_energy_cost,
            'drone_fixed_cost': drone_fixed_cost,
            'drone_time_cost': drone_time_cost,
            'total_cost_no_penalty': total_cost,
            'depot_transport_cost': depot_transport_cost,
            'depot_time_cost': depot_time_cost,
            'depot_fixed_cost': depot_fixed_cost,
            'depot_to_wulong_distance': depot_to_wulong_distance,
            'delivery_times': delivery_times,  # 各村庄配送时间
            'avg_delivery_time': avg_delivery_time,  # 平均配送时间
            'max_delivery_time': max_delivery_time,   # 最大配送时间
            'time_constraint_satisfied': time_constraint_satisfied,  # 时间约束是否满足
            'time_constraint_value': m_value  # 时间约束评估值
        }

    # ========= 可视化 ========= #
    def visualize_solution(self, sol, ana):
        fig, (ax1, ax2) = plt.subplots(1,2, figsize=(20,10))
        locs = list(self.locations.keys())
        coords = np.array(list(self.locations.values()))
        ax1.scatter(coords[:,1], coords[:,0], s=50, alpha=0.7)
        ax1.scatter(coords[0,1], coords[0,0], s=200, marker='s', label='配送中心')
        ax1.scatter(coords[1,1], coords[1,0], s=150, marker='^', label='五龙镇')

        # 绘制配送中心到五龙镇的路径
        depot_coord = coords[0]  # 配送中心
        wulong_coord = coords[1]  # 五龙镇
        ax1.plot([depot_coord[1], wulong_coord[1]], [depot_coord[0], wulong_coord[0]], 
                 color='red', linewidth=4, linestyle='-', label='配送中心→五龙镇')
        # 添加箭头
        ax1.annotate('', xy=(wulong_coord[1], wulong_coord[0]), xytext=(depot_coord[1], depot_coord[0]),
                     arrowprops=dict(arrowstyle='->', color='red', lw=2))

        colors = ['C0','C1','C2','C3','C4']
        for i, route in enumerate(ana['vehicle_routes']):
            if route or ana['vehicle_has_drone'][i]:
                if route:
                    seq = [wulong_coord] + [coords[locs.index(c)] for c in route] + [wulong_coord]
                    seq = np.array(seq)
                    ax1.plot(seq[:,1], seq[:,0], linewidth=2, label=f'车辆{i+1}({len(route)}点,{ana["vehicle_times"][i]:.1f}h)')
                    # 为车辆路径添加箭头
                    for j in range(len(seq)-1):
                        ax1.annotate('', xy=(seq[j+1,1], seq[j+1,0]), xytext=(seq[j,1], seq[j,0]),
                                     arrowprops=dict(arrowstyle='->', color=colors[i], lw=1))
                else:
                    # 仅携机：画到最远无人机点
                    max_d=0.0; best=1  # 从五龙镇开始
                    for (c,_,_,_,_,_,_) in ana['drone_rows']:
                        c_idx = locs.index(c)
                        d = self._air_distance(1, c_idx)  # 从五龙镇计算距离
                        if d>max_d: max_d=d; best=c_idx
                    if max_d>0:
                        seg = np.array([wulong_coord, coords[best]])
                        ax1.plot(seg[:,1], seg[:,0], linewidth=2, linestyle='--', label=f'车辆{i+1}(携机)')
                        # 为携机车辆路径添加箭头
                        ax1.annotate('', xy=(seg[1,1], seg[1,0]), xytext=(seg[0,1], seg[0,0]),
                                     arrowprops=dict(arrowstyle='->', color=colors[i], lw=1, linestyle='--'))
        
        # 绘制无人机配送路线
        wulong_idx = list(self.locations.keys()).index("五龙镇")
        customers = list(self.demands.keys())
        customers = [c for c in customers if c not in ["配送中心", "五龙镇"]]
        
        for i, c in enumerate(customers):
            if sol['drone_assignment'][i] == 1:  # 如果该村庄使用无人机配送
                c_idx = list(self.locations.keys()).index(c)
                # 确定起降点（优先该车直送点，否则五龙镇）
                v = int(sol['vehicle_assignment'][i])
                candidates = [wulong_idx]
                for j, other in enumerate(customers):
                    if (sol['drone_assignment'][j] == 0 and int(sol['vehicle_assignment'][j]) == v):
                        candidates.append(list(self.locations.keys()).index(other))
                takeoff_idx = min(candidates, key=lambda x: self._air_distance(x, c_idx))
                
                # 绘制无人机路径
                takeoff_coord = coords[takeoff_idx]
                customer_coord = coords[c_idx]
                
                # 使用虚线表示无人机路径
                ax1.plot([takeoff_coord[1], customer_coord[1]], [takeoff_coord[0], customer_coord[0]], 
                         color='purple', linewidth=2, linestyle=':', alpha=0.8)
                
                # 添加无人机路径箭头
                ax1.annotate('', xy=(customer_coord[1], customer_coord[0]), xytext=(takeoff_coord[1], takeoff_coord[0]),
                             arrowprops=dict(arrowstyle='->', color='purple', lw=2, linestyle=':', alpha=0.8))
        
        # 无人机点
        drone_points = [locs.index(c) for (c, *_) in ana['drone_rows']]
        if drone_points:
            pts = coords[drone_points]
            ax1.scatter(pts[:,1], pts[:,0], s=100, marker='^', color='purple', label=f'无人机配送点({len(drone_points)}个)')

        ax1.set_xlabel('经度'); ax1.set_ylabel('纬度'); ax1.set_title('配送中心→五龙镇→各村庄配送路径图')
        ax1.legend(); ax1.grid(True, alpha=0.3)

        # 右图：成本与时间柱状
        labels = ['车辆燃油','车辆固定','车辆时间','无人机电费','无人机固定','无人机时间']
        vals = [ana['vehicle_fuel_cost'], ana['vehicle_fixed_cost'], ana['vehicle_time_cost'],
                ana['drone_energy_cost'], ana['drone_fixed_cost'], ana['drone_time_cost']]
        bars = ax2.bar(labels, vals)
        #设置每个条形图的颜色
        colors = ['#5ebfc2','#5dcfbd','#72deaf','#97ea9b','#c5f384','#f9f871']
        for b,v,c in zip(bars, vals, colors):
            b.set_color(c)
        ax2.set_ylabel('成本（元）'); ax2.set_title('成本构成（含时间成本）')
        for b,v in zip(bars, vals):
            ax2.text(b.get_x()+b.get_width()/2, b.get_height()+0.5, f"{v:.1f}", ha='center', va='bottom')
        plt.tight_layout()
        plt.savefig('车辆无人机协同配送_含时间成本.png', dpi=300, bbox_inches='tight')
        plt.show()

def main():
    opt = VehicleDroneDeliveryOptimizer()
    best_sol, best_fit, hist = opt.optimize()
    ana = opt.analyze_solution(best_sol)
    
    # 检查时间约束
    if ana['time_constraint_satisfied']==1:
        print(f"\n✅ 方案满足时间约束条件！")
        print(f"时间约束评估值: {ana['time_constraint_value']:.3f} ")
    else:
        print(f"\n❌ 方案不满足时间约束条件！")
        print(f"时间约束评估值: {ana['time_constraint_value']:.3f} ")
        print("建议调整配送策略以改善时间性能")
    
    opt.visualize_solution(best_sol, ana)

    # 汇总导出
    rows=[]
    # 配送中心运输数据
    rows.append({
        '类型':'配送中心运输',
        '编号':'配送中心车辆',
        '直配送村': '五龙镇',
        '距离(km)': ana['depot_to_wulong_distance'],
        '时间(h)': ana['depot_to_wulong_distance'] / opt.vehicle_params['speed'],
        '燃油成本(元)': ana['depot_transport_cost'],
        '时间成本(元)': ana['depot_time_cost'],
        '车辆固定成本(元)': ana['depot_fixed_cost']
    })
    
    # 车辆明细
    for i,route in enumerate(ana['vehicle_routes']):
        used = (len(route)>0) or ana['vehicle_has_drone'][i]
        if not used: continue
        rows.append({
            '类型':'五龙镇车辆',
            '编号':f'五龙镇车辆{i+1}',
            '直配送村': ', '.join(route) if route else '无',
            '距离(km)': ana['vehicle_distances'][i],
            '时间(h)': ana['vehicle_times'][i],
            '燃油成本(元)': ana['vehicle_distances'][i]*opt.vehicle_params['fuel_consumption']*opt.vehicle_params['fuel_price'],
            '时间成本(元)': ana['vehicle_times'][i]*opt.driver_time_price,
            '车辆固定成本(元)': opt.VEHICLE_DEPLOY_FIXED_COST
        })
    # 无人机明细
    for (c, d_km, w, elec, fixc, trips, t_h) in ana['drone_rows']:
        rows.append({
            '类型':'五龙镇无人机',
            '编号':'五龙镇无人机',
            '服务村': c,
            '往返距离(km)': d_km,
            '货重(kg)': w,
            '飞行时间(h)': t_h,
            '电费(元)': elec,
            '无人机固定成本(元)': fixc,
            '架次数': trips,
            '时间成本(元)': t_h*opt.drone_time_price
        })
    df = pd.DataFrame(rows)
    df.to_excel('配送优化结果_含时间成本.xlsx', index=False)
    print("\n结果已保存：配送优化结果_含时间成本.xlsx")

if __name__ == "__main__":
    main()
