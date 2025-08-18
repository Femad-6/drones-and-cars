# -*- coding: utf-8 -*-
"""
五龙镇车-机协同配送方案可视化
基于优化模型结果生成直观的图表展示
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 五龙镇下辖村庄数据
village_data = {
    '村庄名称': [
        '丰峪村', '上庄村', '泽下村', '文峪村', '河头村', '罗圈村', 
        '城峪村', '岭后村', '荷花村', '渔村', '合脉掌村', '碾上村', 
        '长坡村', '南沃村', '西蒋村', '岭南村', '桑峪村', '马兰村', 
        '中石阵村', '栗家洼村', '牛家岗村', '陈家岗村', '薛家岗村', 
        '石官村', '阳和村', '七峪村'
    ],
    '距离配送中心(km)': [
        8, 12, 15, 10, 18, 14, 9, 16, 11, 13, 20, 7, 17, 19, 6, 21, 
        12, 15, 8, 22, 14, 16, 13, 11, 9, 18
    ],
    '需求件数': [
        25, 18, 15, 22, 12, 20, 28, 14, 24, 19, 8, 32, 16, 10, 35, 6, 
        21, 17, 26, 5, 23, 18, 20, 22, 27, 13
    ]
}

df_villages = pd.DataFrame(village_data)

def create_delivery_visualization():
    """创建配送方案可视化图表"""
    
    fig = plt.figure(figsize=(20, 16))
    
    # 1. 村庄分布与距离关系图
    ax1 = plt.subplot(3, 3, 1)
    scatter = ax1.scatter(df_villages['距离配送中心(km)'], df_villages['需求件数'], 
                         s=df_villages['需求件数']*3, alpha=0.7, 
                         c=df_villages['距离配送中心(km)'], cmap='viridis')
    ax1.set_xlabel('距离配送中心 (公里)')
    ax1.set_ylabel('需求件数')
    ax1.set_title('村庄分布：距离 vs 需求')
    ax1.grid(True, alpha=0.3)
    
    # 添加村庄标签
    for i, village in enumerate(df_villages['村庄名称']):
        ax1.annotate(village, (df_villages['距离配送中心(km)'].iloc[i], 
                              df_villages['需求件数'].iloc[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    # 2. 需求分布柱状图
    ax2 = plt.subplot(3, 3, 2)
    bars = ax2.bar(range(len(df_villages)), df_villages['需求件数'], 
                   color='skyblue', alpha=0.8)
    ax2.set_xlabel('村庄编号')
    ax2.set_ylabel('需求件数')
    ax2.set_title('各村庄需求分布')
    ax2.set_xticks(range(len(df_villages)))
    ax2.set_xticklabels(range(1, len(df_villages)+1), rotation=45)
    ax2.grid(True, alpha=0.3)
    
    # 3. 距离分布饼图
    ax3 = plt.subplot(3, 3, 3)
    distance_ranges = pd.cut(df_villages['距离配送中心(km)'], 
                            bins=[0, 10, 15, 25], 
                            labels=['近程(0-10km)', '中程(10-15km)', '远程(15-25km)'])
    distance_counts = distance_ranges.value_counts()
    
    colors = ['lightgreen', 'orange', 'red']
    wedges, texts, autotexts = ax3.pie(distance_counts.values, labels=distance_counts.index, 
                                       autopct='%1.1f%%', colors=colors, startangle=90)
    ax3.set_title('村庄距离分布')
    
    # 4. 成本结构分析（模拟数据）
    ax4 = plt.subplot(3, 3, 4)
    cost_components = ['固定成本', '车辆运输', '无人机运输', '补贴收入']
    cost_values = [600, 1200, 800, -900]  # 模拟数据
    colors_cost = ['lightcoral', 'lightblue', 'lightgreen', 'gold']
    
    bars = ax4.bar(cost_components, cost_values, color=colors_cost, alpha=0.8)
    ax4.set_ylabel('成本 (元)')
    ax4.set_title('成本结构分析')
    ax4.grid(True, alpha=0.3)
    
    # 添加数值标签
    for bar, value in zip(bars, cost_values):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.0f}', ha='center', va='bottom' if value > 0 else 'top')
    
    # 5. 配送方式选择逻辑
    ax5 = plt.subplot(3, 3, 5)
    # 基于距离和需求的配送方式决策
    delivery_method = []
    for i in range(len(df_villages)):
        distance = df_villages['距离配送中心(km)'].iloc[i]
        demand = df_villages['需求件数'].iloc[i]
        
        # 简单的决策逻辑：距离远且需求少的用无人机
        if distance > 15 and demand < 20:
            delivery_method.append('无人机')
        else:
            delivery_method.append('车辆')
    
    df_villages['配送方式'] = delivery_method
    
    # 统计配送方式
    method_counts = df_villages['配送方式'].value_counts()
    colors_method = ['lightblue', 'lightgreen']
    wedges, texts, autotexts = ax5.pie(method_counts.values, labels=method_counts.index, 
                                       autopct='%1.1f%%', colors=colors_method, startangle=90)
    ax5.set_title('配送方式分布')
    
    # 6. 距离-需求-配送方式三维关系
    ax6 = plt.subplot(3, 3, 6)
    truck_mask = df_villages['配送方式'] == '车辆'
    drone_mask = df_villages['配送方式'] == '无人机'
    
    ax6.scatter(df_villages[truck_mask]['距离配送中心(km)'], 
               df_villages[truck_mask]['需求件数'], 
               s=100, c='blue', alpha=0.7, label='车辆配送', marker='o')
    ax6.scatter(df_villages[drone_mask]['距离配送中心(km)'], 
               df_villages[drone_mask]['需求件数'], 
               s=100, c='red', alpha=0.7, label='无人机配送', marker='^')
    
    ax6.set_xlabel('距离配送中心 (公里)')
    ax6.set_ylabel('需求件数')
    ax6.set_title('配送方式选择逻辑')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    # 7. 阶梯补贴效果分析
    ax7 = plt.subplot(3, 3, 7)
    subsidy_tiers = ['第一档\n(3.0元/件)', '第二档\n(2.0元/件)', '第三档\n(1.0元/件)', '第四档\n(0.5元/件)']
    tier_capacity = [30, 60, 120, 1000]
    tier_usage = [25, 45, 80, 50]  # 模拟使用量
    
    x = np.arange(len(subsidy_tiers))
    width = 0.35
    
    bars1 = ax7.bar(x - width/2, tier_capacity, width, label='容量限制', 
                    color='lightgray', alpha=0.8)
    bars2 = ax7.bar(x + width/2, tier_usage, width, label='实际使用', 
                    color='lightblue', alpha=0.8)
    
    ax7.set_xlabel('补贴档位')
    ax7.set_ylabel('件数')
    ax7.set_title('阶梯补贴使用情况')
    ax7.set_xticks(x)
    ax7.set_xticklabels(subsidy_tiers)
    ax7.legend()
    ax7.grid(True, alpha=0.3)
    
    # 8. 时效分析
    ax8 = plt.subplot(3, 3, 8)
    # 模拟各村庄的配送时间
    delivery_times = []
    for i in range(len(df_villages)):
        distance = df_villages['距离配送中心(km)'].iloc[i]
        method = df_villages['配送方式'].iloc[i]
        
        if method == '车辆':
            # 车辆速度40km/h，加上装卸时间
            time = distance / 40 + 0.5
        else:
            # 无人机速度60km/h，直线距离
            time = distance * 1.2 / 60 + 0.2
        
        delivery_times.append(time)
    
    df_villages['配送时间(小时)'] = delivery_times
    
    # 时效分布
    time_ranges = pd.cut(df_villages['配送时间(小时)'], 
                        bins=[0, 0.5, 1, 2], 
                        labels=['0.5h内', '0.5-1h', '1-2h'])
    time_counts = time_ranges.value_counts()
    
    colors_time = ['green', 'orange', 'red']
    wedges, texts, autotexts = ax8.pie(time_counts.values, labels=time_counts.index, 
                                       autopct='%1.1f%%', colors=colors_time, startangle=90)
    ax8.set_title('配送时效分布')
    
    # 9. 综合效益分析
    ax9 = plt.subplot(3, 3, 9)
    # 计算综合效益指标
    efficiency_scores = []
    for i in range(len(df_villages)):
        distance = df_villages['距离配送中心(km)'].iloc[i]
        demand = df_villages['需求件数'].iloc[i]
        method = df_villages['配送方式'].iloc[i]
        
        # 简单的效益评分：需求/距离 * 方式系数
        if method == '无人机':
            efficiency = (demand / distance) * 1.2  # 无人机效率更高
        else:
            efficiency = demand / distance
        
        efficiency_scores.append(efficiency)
    
    df_villages['效益评分'] = efficiency_scores
    
    # 效益分布直方图
    ax9.hist(efficiency_scores, bins=8, color='lightblue', alpha=0.8, edgecolor='black')
    ax9.set_xlabel('效益评分')
    ax9.set_ylabel('村庄数量')
    ax9.set_title('配送效益分布')
    ax9.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('wulong_delivery_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_route_visualization():
    """创建车辆路径可视化"""
    
    # 模拟车辆路径数据
    vehicle_routes = {
        '车辆1': ['五龙镇', '西蒋村', '碾上村', '城峪村', '阳和村', '中石阵村', '五龙镇'],
        '车辆2': ['五龙镇', '丰峪村', '文峪村', '荷花村', '渔村', '石官村', '薛家岗村', '五龙镇'],
        '车辆3': ['五龙镇', '上庄村', '罗圈村', '桑峪村', '牛家岗村', '陈家岗村', '五龙镇']
    }
    
    # 无人机配送村庄
    drone_villages = ['泽下村', '河头村', '岭后村', '合脉掌村', '长坡村', '南沃村', 
                     '岭南村', '马兰村', '栗家洼村', '七峪村']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # 1. 车辆路径图
    colors = ['red', 'blue', 'green']
    for i, (vehicle, route) in enumerate(vehicle_routes.items()):
        # 简化的路径可视化
        x_coords = np.linspace(0, 10, len(route))
        y_coords = np.sin(x_coords + i) + i * 0.5
        
        ax1.plot(x_coords, y_coords, 'o-', color=colors[i], label=vehicle, linewidth=2, markersize=8)
        
        # 添加村庄标签
        for j, village in enumerate(route):
            if village != '五龙镇':
                ax1.annotate(village, (x_coords[j], y_coords[j]), 
                           xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    ax1.set_title('车辆配送路径')
    ax1.set_xlabel('路径节点')
    ax1.set_ylabel('路径坐标')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. 无人机配送覆盖图
    # 模拟无人机配送的覆盖范围
    center_x, center_y = 5, 5
    coverage_radius = 3
    
    # 绘制配送中心
    ax2.scatter(center_x, center_y, s=200, c='red', marker='s', label='五龙镇配送中心')
    
    # 绘制无人机配送村庄
    drone_x = np.random.uniform(center_x - coverage_radius, center_x + coverage_radius, len(drone_villages))
    drone_y = np.random.uniform(center_y - coverage_radius, center_y + coverage_radius, len(drone_villages))
    
    ax2.scatter(drone_x, drone_y, s=100, c='blue', marker='^', alpha=0.7, label='无人机配送村庄')
    
    # 添加村庄标签
    for i, village in enumerate(drone_villages):
        ax2.annotate(village, (drone_x[i], drone_y[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    # 绘制覆盖范围
    circle = plt.Circle((center_x, center_y), coverage_radius, fill=False, 
                       color='red', linestyle='--', alpha=0.5, label='无人机覆盖范围')
    ax2.add_patch(circle)
    
    ax2.set_xlim(center_x - coverage_radius - 1, center_x + coverage_radius + 1)
    ax2.set_ylim(center_y - coverage_radius - 1, center_y + coverage_radius + 1)
    ax2.set_title('无人机配送覆盖')
    ax2.set_xlabel('X坐标')
    ax2.set_ylabel('Y坐标')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig('wulong_route_visualization.png', dpi=300, bbox_inches='tight')
    plt.show()

def print_delivery_summary():
    """打印配送方案摘要"""
    print("="*60)
    print("五龙镇车-机协同配送方案摘要")
    print("="*60)
    
    print(f"\n1. 基础信息:")
    print(f"   配送中心: 五龙镇")
    print(f"   服务村庄数: {len(df_villages)} 个")
    print(f"   总需求: {df_villages['需求件数'].sum()} 件")
    print(f"   平均距离: {df_villages['距离配送中心(km)'].mean():.1f} 公里")
    
    print(f"\n2. 配送方式分析:")
    method_counts = df_villages['配送方式'].value_counts()
    for method, count in method_counts.items():
        percentage = count / len(df_villages) * 100
        print(f"   {method}配送: {count} 个村庄 ({percentage:.1f}%)")
    
    print(f"\n3. 距离分布:")
    distance_stats = df_villages['距离配送中心(km)'].describe()
    print(f"   最近村庄: {distance_stats['min']:.1f} 公里")
    print(f"   最远村庄: {distance_stats['max']:.1f} 公里")
    print(f"   平均距离: {distance_stats['mean']:.1f} 公里")
    
    print(f"\n4. 需求分布:")
    demand_stats = df_villages['需求件数'].describe()
    print(f"   最小需求: {demand_stats['min']:.0f} 件")
    print(f"   最大需求: {demand_stats['max']:.0f} 件")
    print(f"   平均需求: {demand_stats['mean']:.1f} 件")
    
    print(f"\n5. 时效分析:")
    delivery_times = []
    for i in range(len(df_villages)):
        distance = df_villages['距离配送中心(km)'].iloc[i]
        method = df_villages['配送方式'].iloc[i]
        
        if method == '车辆':
            time = distance / 40 + 0.5
        else:
            time = distance * 1.2 / 60 + 0.2
        
        delivery_times.append(time)
    
    df_villages['配送时间(小时)'] = delivery_times
    time_stats = df_villages['配送时间(小时)'].describe()
    print(f"   最短时间: {time_stats['min']:.2f} 小时")
    print(f"   最长时间: {time_stats['max']:.2f} 小时")
    print(f"   平均时间: {time_stats['mean']:.2f} 小时")
    
    print("="*60)

if __name__ == "__main__":
    print("正在生成五龙镇配送方案可视化...")
    
    # 创建综合分析图表
    create_delivery_visualization()
    
    # 创建路径可视化
    create_route_visualization()
    
    # 打印摘要
    print_delivery_summary()
    
    print("\n可视化完成！已生成以下文件：")
    print("- wulong_delivery_analysis.png (综合分析)")
    print("- wulong_route_visualization.png (路径可视化)")

