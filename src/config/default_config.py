# -*- coding: utf-8 -*-
"""
五龙镇配送优化系统 - 默认配置文件
包含系统所有参数的默认设置
"""

# 系统基本信息
SYSTEM_INFO = {
    'name': '五龙镇配送优化系统',
    'version': '1.0.0',
    'author': '配送优化研究团队',
    'description': '基于车辆-无人机协同配送的县域农村电商物流优化系统'
}

# 地理位置数据
LOCATIONS = {
    "配送中心": (35.8236, 113.9715),  # 配送中心
    "五龙镇": (35.7828, 113.9398),  # 五龙镇中转站（村庄数据汇总点）
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

# 各村快递需求量（下行配送包裹数）
DEMANDS_PIECE = {
    "石官村": 266, "中石阵村": 246, "阳和村": 221, "碾上村": 183, "泽下村": 170,
    "七峪村": 147, "渔村": 142, "合脉掌村": 142, "桑峪村": 141, "荷花村": 132,
    "西蒋村": 125, "岭后村": 123, "上庄村": 109, "罗圈村": 99,
    "南沃村": 85, "丰峪村": 84, "岭南村": 83, "马兰村": 82, "城峪村": 80,
    "牛家岗村": 66, "陈家岗村": 65, "薛家岗村": 65, "长坡村": 62, "文峪村": 47, "栗家洼村": 47
}

# 配送货物详细分类（按类型和重量）
CARGO_DETAILS = {
    "石官村": {"light_packages": 160, "heavy_packages": 80, "fragile_items": 26},
    "中石阵村": {"light_packages": 148, "heavy_packages": 74, "fragile_items": 24},
    "阳和村": {"light_packages": 133, "heavy_packages": 66, "fragile_items": 22},
    "碾上村": {"light_packages": 110, "heavy_packages": 55, "fragile_items": 18},
    "泽下村": {"light_packages": 102, "heavy_packages": 51, "fragile_items": 17},
    "七峪村": {"light_packages": 88, "heavy_packages": 44, "fragile_items": 15},
    "渔村": {"light_packages": 85, "heavy_packages": 43, "fragile_items": 14},
    "合脉掌村": {"light_packages": 85, "heavy_packages": 43, "fragile_items": 14},
    "桑峪村": {"light_packages": 85, "heavy_packages": 42, "fragile_items": 14},
    "荷花村": {"light_packages": 79, "heavy_packages": 40, "fragile_items": 13},
    "西蒋村": {"light_packages": 75, "heavy_packages": 38, "fragile_items": 12},
    "岭后村": {"light_packages": 74, "heavy_packages": 37, "fragile_items": 12},
    "上庄村": {"light_packages": 65, "heavy_packages": 33, "fragile_items": 11},
    "罗圈村": {"light_packages": 59, "heavy_packages": 30, "fragile_items": 10},
    "南沃村": {"light_packages": 51, "heavy_packages": 26, "fragile_items": 8},
    "丰峪村": {"light_packages": 50, "heavy_packages": 25, "fragile_items": 9},
    "岭南村": {"light_packages": 50, "heavy_packages": 25, "fragile_items": 8},
    "马兰村": {"light_packages": 49, "heavy_packages": 25, "fragile_items": 8},
    "城峪村": {"light_packages": 48, "heavy_packages": 24, "fragile_items": 8},
    "牛家岗村": {"light_packages": 40, "heavy_packages": 20, "fragile_items": 6},
    "陈家岗村": {"light_packages": 39, "heavy_packages": 20, "fragile_items": 6},
    "薛家岗村": {"light_packages": 39, "heavy_packages": 20, "fragile_items": 6},
    "长坡村": {"light_packages": 37, "heavy_packages": 19, "fragile_items": 6},
    "文峪村": {"light_packages": 28, "heavy_packages": 14, "fragile_items": 5},
    "栗家洼村": {"light_packages": 28, "heavy_packages": 14, "fragile_items": 5}
}

# 上行包裹数据（详细分类）
UPSTREAM_PACKAGES = {
    "石官村": {
        "recyclables": {"paper": 32, "plastic": 21, "electronics": 5},
        "agricultural_products": {"fruits": 15, "vegetables": 28, "grains": 12},
        "handmade_crafts": {"textiles": 8, "woodwork": 3, "pottery": 2},
        "return_packages": {"damaged": 4, "wrong_delivery": 2}
    },
    "中石阵村": {
        "recyclables": {"paper": 29, "plastic": 20, "electronics": 5},
        "agricultural_products": {"fruits": 14, "vegetables": 26, "grains": 11},
        "handmade_crafts": {"textiles": 7, "woodwork": 3, "pottery": 2},
        "return_packages": {"damaged": 3, "wrong_delivery": 2}
    },
    "阳和村": {
        "recyclables": {"paper": 26, "plastic": 18, "electronics": 4},
        "agricultural_products": {"fruits": 13, "vegetables": 23, "grains": 10},
        "handmade_crafts": {"textiles": 7, "woodwork": 2, "pottery": 2},
        "return_packages": {"damaged": 3, "wrong_delivery": 1}
    },
    "碾上村": {
        "recyclables": {"paper": 22, "plastic": 15, "electronics": 4},
        "agricultural_products": {"fruits": 11, "vegetables": 19, "grains": 8},
        "handmade_crafts": {"textiles": 6, "woodwork": 2, "pottery": 1},
        "return_packages": {"damaged": 3, "wrong_delivery": 1}
    },
    "泽下村": {
        "recyclables": {"paper": 20, "plastic": 14, "electronics": 3},
        "agricultural_products": {"fruits": 10, "vegetables": 18, "grains": 8},
        "handmade_crafts": {"textiles": 5, "woodwork": 2, "pottery": 1},
        "return_packages": {"damaged": 2, "wrong_delivery": 1}
    },
    "七峪村": {
        "recyclables": {"paper": 18, "plastic": 12, "electronics": 3},
        "agricultural_products": {"fruits": 9, "vegetables": 15, "grains": 7},
        "handmade_crafts": {"textiles": 5, "woodwork": 2, "pottery": 1},
        "return_packages": {"damaged": 2, "wrong_delivery": 1}
    },
    "渔村": {
        "recyclables": {"paper": 17, "plastic": 11, "electronics": 3},
        "agricultural_products": {"fruits": 8, "vegetables": 14, "grains": 6},
        "handmade_crafts": {"textiles": 4, "woodwork": 1, "pottery": 1},
        "return_packages": {"damaged": 2, "wrong_delivery": 1}
    },
    "合脉掌村": {
        "recyclables": {"paper": 17, "plastic": 11, "electronics": 3},
        "agricultural_products": {"fruits": 8, "vegetables": 14, "grains": 6},
        "handmade_crafts": {"textiles": 4, "woodwork": 1, "pottery": 1},
        "return_packages": {"damaged": 2, "wrong_delivery": 1}
    },
    "桑峪村": {
        "recyclables": {"paper": 17, "plastic": 11, "electronics": 3},
        "agricultural_products": {"fruits": 8, "vegetables": 14, "grains": 6},
        "handmade_crafts": {"textiles": 4, "woodwork": 1, "pottery": 1},
        "return_packages": {"damaged": 2, "wrong_delivery": 1}
    },
    "荷花村": {
        "recyclables": {"paper": 16, "plastic": 10, "electronics": 2},
        "agricultural_products": {"fruits": 7, "vegetables": 13, "grains": 6},
        "handmade_crafts": {"textiles": 4, "woodwork": 1, "pottery": 1},
        "return_packages": {"damaged": 2, "wrong_delivery": 1}
    },
    "西蒋村": {
        "recyclables": {"paper": 15, "plastic": 10, "electronics": 2},
        "agricultural_products": {"fruits": 7, "vegetables": 12, "grains": 5},
        "handmade_crafts": {"textiles": 3, "woodwork": 1, "pottery": 1},
        "return_packages": {"damaged": 2, "wrong_delivery": 1}
    },
    "岭后村": {
        "recyclables": {"paper": 15, "plastic": 10, "electronics": 2},
        "agricultural_products": {"fruits": 7, "vegetables": 12, "grains": 5},
        "handmade_crafts": {"textiles": 3, "woodwork": 1, "pottery": 1},
        "return_packages": {"damaged": 2, "wrong_delivery": 1}
    },
    "上庄村": {
        "recyclables": {"paper": 13, "plastic": 9, "electronics": 2},
        "agricultural_products": {"fruits": 6, "vegetables": 11, "grains": 5},
        "handmade_crafts": {"textiles": 3, "woodwork": 1, "pottery": 1},
        "return_packages": {"damaged": 1, "wrong_delivery": 1}
    },
    "罗圈村": {
        "recyclables": {"paper": 12, "plastic": 8, "electronics": 2},
        "agricultural_products": {"fruits": 5, "vegetables": 9, "grains": 4},
        "handmade_crafts": {"textiles": 3, "woodwork": 1, "pottery": 0},
        "return_packages": {"damaged": 1, "wrong_delivery": 1}
    },
    "南沃村": {
        "recyclables": {"paper": 13, "plastic": 9, "electronics": 2},
        "agricultural_products": {"fruits": 5, "vegetables": 8, "grains": 4},
        "handmade_crafts": {"textiles": 2, "woodwork": 1, "pottery": 0},
        "return_packages": {"damaged": 1, "wrong_delivery": 1}
    },
    "丰峪村": {
        "recyclables": {"paper": 13, "plastic": 8, "electronics": 2},
        "agricultural_products": {"fruits": 5, "vegetables": 8, "grains": 4},
        "handmade_crafts": {"textiles": 2, "woodwork": 1, "pottery": 0},
        "return_packages": {"damaged": 1, "wrong_delivery": 1}
    },
    "岭南村": {
        "recyclables": {"paper": 13, "plastic": 8, "electronics": 2},
        "agricultural_products": {"fruits": 5, "vegetables": 8, "grains": 4},
        "handmade_crafts": {"textiles": 2, "woodwork": 1, "pottery": 0},
        "return_packages": {"damaged": 1, "wrong_delivery": 1}
    },
    "马兰村": {
        "recyclables": {"paper": 12, "plastic": 8, "electronics": 2},
        "agricultural_products": {"fruits": 5, "vegetables": 8, "grains": 3},
        "handmade_crafts": {"textiles": 2, "woodwork": 1, "pottery": 0},
        "return_packages": {"damaged": 1, "wrong_delivery": 1}
    },
    "城峪村": {
        "recyclables": {"paper": 12, "plastic": 8, "electronics": 2},
        "agricultural_products": {"fruits": 5, "vegetables": 8, "grains": 3},
        "handmade_crafts": {"textiles": 2, "woodwork": 1, "pottery": 0},
        "return_packages": {"damaged": 1, "wrong_delivery": 1}
    },
    "牛家岗村": {
        "recyclables": {"paper": 10, "plastic": 7, "electronics": 1},
        "agricultural_products": {"fruits": 4, "vegetables": 7, "grains": 3},
        "handmade_crafts": {"textiles": 2, "woodwork": 0, "pottery": 0},
        "return_packages": {"damaged": 1, "wrong_delivery": 0}
    },
    "陈家岗村": {
        "recyclables": {"paper": 10, "plastic": 6, "electronics": 1},
        "agricultural_products": {"fruits": 4, "vegetables": 6, "grains": 3},
        "handmade_crafts": {"textiles": 2, "woodwork": 0, "pottery": 0},
        "return_packages": {"damaged": 1, "wrong_delivery": 0}
    },
    "薛家岗村": {
        "recyclables": {"paper": 10, "plastic": 6, "electronics": 1},
        "agricultural_products": {"fruits": 4, "vegetables": 6, "grains": 3},
        "handmade_crafts": {"textiles": 2, "woodwork": 0, "pottery": 0},
        "return_packages": {"damaged": 1, "wrong_delivery": 0}
    },
    "长坡村": {
        "recyclables": {"paper": 10, "plastic": 6, "electronics": 1},
        "agricultural_products": {"fruits": 4, "vegetables": 6, "grains": 2},
        "handmade_crafts": {"textiles": 1, "woodwork": 0, "pottery": 0},
        "return_packages": {"damaged": 1, "wrong_delivery": 0}
    },
    "文峪村": {
        "recyclables": {"paper": 7, "plastic": 5, "electronics": 1},
        "agricultural_products": {"fruits": 3, "vegetables": 5, "grains": 2},
        "handmade_crafts": {"textiles": 1, "woodwork": 0, "pottery": 0},
        "return_packages": {"damaged": 1, "wrong_delivery": 0}
    },
    "栗家洼村": {
        "recyclables": {"paper": 7, "plastic": 5, "electronics": 1},
        "agricultural_products": {"fruits": 3, "vegetables": 5, "grains": 2},
        "handmade_crafts": {"textiles": 1, "woodwork": 0, "pottery": 0},
        "return_packages": {"damaged": 1, "wrong_delivery": 0}
    }
}

# 保持向后兼容的回收品数据（简化版本）
RECYCLABLES = {
    "石官村": {"short": 53, "long": 21},
    "中石阵村": {"short": 49, "long": 19},
    "阳和村": {"short": 44, "long": 18},
    "碾上村": {"short": 37, "long": 14},
    "泽下村": {"short": 34, "long": 14},
    "七峪村": {"short": 30, "long": 12},
    "渔村": {"short": 28, "long": 11},
    "合脉掌村": {"short": 28, "long": 11},
    "桑峪村": {"short": 28, "long": 11},
    "荷花村": {"short": 26, "long": 10},
    "西蒋村": {"short": 25, "long": 10},
    "岭后村": {"short": 25, "long": 10},
    "上庄村": {"short": 22, "long": 9},
    "罗圈村": {"short": 20, "long": 8},
    "南沃村": {"short": 21, "long": 9},
    "丰峪村": {"short": 21, "long": 8},
    "岭南村": {"short": 21, "long": 8},
    "马兰村": {"short": 20, "long": 8},
    "城峪村": {"short": 20, "long": 8},
    "牛家岗村": {"short": 17, "long": 7},
    "陈家岗村": {"short": 16, "long": 7},
    "薛家岗村": {"short": 16, "long": 7},
    "长坡村": {"short": 16, "long": 6},
    "文峪村": {"short": 12, "long": 5},
    "栗家洼村": {"short": 12, "long": 5},
}

# 五龙镇中转站汇总数据（所有村庄数据的总和）
WULONG_TRANSFER_STATION = {
    "total_downstream_packages": 3012,  # 下行包裹总数（等于所有村庄需求总和）
    "cargo_summary": {
        "light_packages": 1810,  # 轻包裹总数
        "heavy_packages": 905,   # 重包裹总数  
        "fragile_items": 297     # 易碎物品总数
    },
    "upstream_summary": {
        "total_recyclables": {
            "paper": 427,        # 纸类回收品总数
            "plastic": 282,      # 塑料回收品总数
            "electronics": 58    # 电子产品回收品总数
        },
        "total_agricultural_products": {
            "fruits": 182,       # 水果总数
            "vegetables": 313,   # 蔬菜总数
            "grains": 140        # 粮食总数
        },
        "total_handmade_crafts": {
            "textiles": 92,      # 纺织品总数
            "woodwork": 30,      # 木工制品总数
            "pottery": 18        # 陶器总数
        },
        "total_return_packages": {
            "damaged": 50,       # 损坏退货总数
            "wrong_delivery": 25 # 错配退货总数
        }
    },
    "operational_metrics": {
        "daily_throughput": {
            "peak_days": 150,    # 高峰期日吞吐量（包裹数）
            "normal_days": 120,  # 平常日吞吐量（包裹数）
            "low_days": 80       # 低峰期日吞吐量（包裹数）
        },
        "storage_capacity": {
            "downstream_storage": 500,  # 下行仓储容量（包裹数）
            "upstream_storage": 300,    # 上行仓储容量（包裹数）
            "temp_storage": 100         # 临时存储容量（包裹数）
        },
        "processing_time": {
            "sorting_time_per_package": 0.5,   # 每包裹分拣时间（分钟）
            "loading_time_per_vehicle": 20,    # 每车装载时间（分钟）
            "quality_check_time": 15           # 质量检查时间（分钟）
        }
    },
    "service_areas": [
        "石官村", "中石阵村", "阳和村", "碾上村", "泽下村", "七峪村", "渔村", 
        "合脉掌村", "桑峪村", "荷花村", "西蒋村", "岭后村", "上庄村", "罗圈村",
        "南沃村", "丰峪村", "岭南村", "马兰村", "城峪村", "牛家岗村", "陈家岗村",
        "薛家岗村", "长坡村", "文峪村", "栗家洼村"
    ]
}

# 车辆参数配置
VEHICLE_PARAMS = {
    'fuel_consumption': 0.252,  # L/km
    'fuel_price': 6.89,         # 元/L
    'speed': 50.0,              # km/h
    'capacity': 1500.0,         # kg
    'num_vehicles': 3,
    'max_hours': 8.0,           # 每辆车最大工时
    'driver_time_price': 60.0,  # 元/小时
    'deploy_fixed_cost': 20.0   # 元/车次
}

# 无人机参数配置
DRONE_PARAMS = {
    'max_payload': 80.0,        # kg（货物）
    'max_range': 12.0,          # km（去程满载）
    'empty_range': 26.0,        # km（回程空载）
    'speed': 60.0,              # km/h
    'battery_capacity': 2.132,  # kWh
    'electricity_price': 0.6,   # 元/kWh
    'weight': 10.0,             # kg（机体）
    'time_price': 20.0,         # 元/小时
    'max_hours': 8.0,           # 无人机总作业上限
    'trip_fixed_cost': 5.0,     # 元/架次
    'power_kwh_per_km_base': 0.164,    # kWh/km 基础能耗
    'power_kwh_per_km_slope': 0.191    # kWh/km 载重相关能耗
}

# 时间约束参数
TIME_CONSTRAINTS = {
    'time_tag': 2.0,                    # 时间阈值（小时）
    'penalty_time': 200.0,              # 超时惩罚权重（元/小时）
    'use_hard_constraint': False,       # True则超时直接判为不可行
    'fuzzy_threshold': 0.56             # 模糊评估阈值
}

# 补贴政策参数
SUBSIDY_POLICY = {
    'down_base': {"fast": 1.0, "slow": 0.5},     # 下行补贴基准（元/件）
    'up_base': {"fast": 0.8, "slow": 0.4},       # 上行补贴基准（元/kg）
    'alpha_down': 0.2,                           # 下行补贴退坡系数
    'alpha_up': 0.2,                             # 上行补贴退坡系数
    'subsidy_stage': 1,                          # 补贴阶段
    'subsidy_budget': 5000.0,                    # 补贴预算（元）
    'over_budget_penalty': 5.0                   # 超预算惩罚系数
}

# 上下行一体化参数
INTEGRATED_PARAMS = {
    'package_weight': 0.5,        # 下行件重（kg/件）
    'recyclable_weight': 2.0,     # 上行件重（kg/件）
    'purchase_price': 6.2,        # 收购价格（元/kg）
    'sale_price': 7.6,            # 销售价格（元/kg）
    'fast_threshold': 0.8,        # 快时效阈值
    'slow_threshold': 0.7,        # 慢时效阈值
    'time_soft_threshold': 0.9    # 时间软约束阈值
}

# GA算法参数
GA_PARAMS = {
    'population_size': 150,
    'generations': 500,
    'mutation_rate': 0.25,
    'crossover_rate': 0.85,
    'elite_size': 0.1
}

# 定向采购参数（产业扶持）
TARGET_PROCUREMENT = {
    'target_min_ratio': {v: 0.3 for v in ["七峪村", "渔村", "合脉掌村", "栗家洼村", "阳和村"]},
    'procure_ratio_bounds': (0, 1)
}

# 模糊评估函数权重
FUZZY_WEIGHTS = {
    'T_avg_weight': 0.444,
    'T_max_weight': 0.084,
    'R_high_weight': 0.472
}

# 文件路径配置
FILE_PATHS = {
    'vehicle_distance_file': 'data/物流车配送距离.xlsx',
    'village_distance_file': 'data/五龙镇各村距离矩阵.xlsx',
    'output_dir': 'output/',
    'config_dir': 'config/',
    'log_file': 'logs/system.log'
}

# 可视化参数
VISUALIZATION_PARAMS = {
    'figsize_main': (20, 10),
    'figsize_single': (12, 8),
    'dpi': 300,
    'font_family': ['SimHei', 'Microsoft YaHei'],
    'color_palette': ['#5ebfc2','#5dcfbd','#72deaf','#97ea9b','#c5f384','#f9f871'],
    'vehicle_colors': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'],
    'drone_color': '#9B59B6'
}
