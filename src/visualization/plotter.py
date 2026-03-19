# -*- coding: utf-8 -*-
"""
五龙镇配送优化系统 - 可视化模块
提供配送方案的可视化功能
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
import logging
from pathlib import Path
import seaborn as sns

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


class DeliveryVisualizer:
    """配送可视化器类"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

        # 获取配置
        viz_config = get_config('visualization_params', {})
        self.figsize_main = viz_config.get('figsize_main', (20, 10))
        self.figsize_single = viz_config.get('figsize_single', (12, 8))
        self.dpi = viz_config.get('dpi', 300)
        self.color_palette = viz_config.get('color_palette',
                                          ['#5ebfc2','#5dcfbd','#72deaf','#97ea9b','#c5f384','#f9f871'])
        self.vehicle_colors = viz_config.get('vehicle_colors',
                                           ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])

    def plot_delivery_network(self, locations: Dict[str, Tuple[float, float]],
                            routes: Dict[int, List[str]],
                            drone_assignments: Dict[str, int],
                            save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制配送网络图

        Args:
            locations: 位置坐标字典
            routes: 车辆路径字典 {车辆ID: [村庄列表]}
            drone_assignments: 无人机分配 {村庄: 车辆ID}
            save_path: 保存路径

        Returns:
            matplotlib Figure对象
        """
        fig, ax = plt.subplots(figsize=self.figsize_main)

        # 绘制所有位置点
        depot_coords = []
        wulong_coords = []
        village_coords = []
        village_names = []

        for name, (lat, lon) in locations.items():
            if name == "配送中心":
                ax.scatter(lon, lat, s=200, c='red', marker='s',
                          label='配送中心', zorder=5)
                depot_coords = [lon, lat]
            elif name == "五龙镇":
                ax.scatter(lon, lat, s=150, c='blue', marker='^',
                          label='五龙镇中转站', zorder=5)
                wulong_coords = [lon, lat]
            else:
                ax.scatter(lon, lat, s=50, c='black', alpha=0.7, zorder=3)
                village_coords.append((lon, lat))
                village_names.append(name)

        # 绘制配送中心到五龙镇中转站的路径
        if depot_coords and wulong_coords:
            ax.plot([depot_coords[0], wulong_coords[0]],
                   [depot_coords[1], wulong_coords[1]],
                   color='red', linewidth=4, linestyle='-',
                   label='配送中心→中转站', zorder=4)
            # 添加箭头
            ax.annotate('', xy=(wulong_coords[0], wulong_coords[1]),
                       xytext=(depot_coords[0], depot_coords[1]),
                       arrowprops=dict(arrowstyle='->', color='red', lw=2))
            
            # 在五龙镇附近添加中转站说明
            ax.annotate('中转站\n(汇总{total_packages}件)'.format(
                total_packages=get_config('wulong_transfer_station', {}).get('total_downstream_packages', 3012)
            ), xy=(wulong_coords[0], wulong_coords[1]), 
                       xytext=(10, 10), textcoords='offset points',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7),
                       fontsize=9, ha='left')

        # 绘制车辆路径
        colors = plt.get_cmap('tab10', len(routes))
        for vehicle_id, route in routes.items():
            if not route:
                continue

            # 构建路径坐标
            path_coords = [wulong_coords]  # 从五龙镇出发
            for village in route:
                if village in locations:
                    lat, lon = locations[village]
                    path_coords.append([lon, lat])
            path_coords.append(wulong_coords)  # 返回五龙镇

            path_coords = np.array(path_coords)

            # 绘制路径
            ax.plot(path_coords[:, 0], path_coords[:, 1],
                   linewidth=3, marker='o', markersize=6,
                   color=colors(vehicle_id),
                   label=f'车辆{vehicle_id+1}路径')

            # 添加方向箭头
            for i in range(len(path_coords) - 1):
                start = path_coords[i]
                end = path_coords[i + 1]
                ax.annotate('', xy=(end[0], end[1]), xytext=(start[0], start[1]),
                           arrowprops=dict(arrowstyle='->',
                                         color=colors(vehicle_id), lw=1.5))

        # 绘制无人机路径
        drone_plotted = False
        for village, vehicle_id in drone_assignments.items():
            if village not in locations:
                continue

            village_lat, village_lon = locations[village]

            # 选择起降点（简化为五龙镇）
            takeoff_lat, takeoff_lon = wulong_coords

            # 绘制无人机路径
            ax.plot([takeoff_lon, village_lon], [takeoff_lat, village_lat],
                   linewidth=2, linestyle=':', color='purple',
                   alpha=0.8, label='无人机路径' if not drone_plotted else "")
            drone_plotted = True

            # 添加箭头
            ax.annotate('', xy=(village_lon, village_lat),
                       xytext=(takeoff_lon, takeoff_lat),
                       arrowprops=dict(arrowstyle='->', color='purple',
                                     lw=2, linestyle=':', alpha=0.8))

        # 设置图例和标签
        ax.set_xlabel('经度')
        ax.set_ylabel('纬度')
        ax.set_title('五龙镇配送优化网络图\n（含中转站协同配送方案）', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
        ax.grid(True, alpha=0.3)
        
        # 添加说明文本
        info_text = (f"📦 服务村庄: {len([v for v in locations.keys() if v not in ['配送中心', '五龙镇']])}个\n"
                    f"🚚 车辆数量: {len(routes)}辆\n"
                    f"🚁 无人机任务: {len(drone_assignments)}个\n"
                    f"🏢 中转站: 五龙镇")
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        # 保存图片
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            self.logger.info(f"配送网络图已保存到: {save_path}")

        return fig

    def plot_cost_breakdown(self, cost_data: Dict[str, float],
                           save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制成本构成图

        Args:
            cost_data: 成本数据字典
            save_path: 保存路径

        Returns:
            matplotlib Figure对象
        """
        fig, ax = plt.subplots(figsize=self.figsize_single)

        labels = list(cost_data.keys())
        values = list(cost_data.values())

        bars = ax.bar(labels, values, color=self.color_palette[:len(labels)])

        # 添加数值标签
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(values) * 0.01,
                   f'{value:.1f}', ha='center', va='bottom')

        ax.set_ylabel('成本 (元)')
        ax.set_title('配送成本构成分析')
        ax.grid(True, alpha=0.3)

        plt.xticks(rotation=45, ha='right')

        # 保存图片
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            self.logger.info(f"成本构成图已保存到: {save_path}")

        return fig

    def plot_delivery_times(self, delivery_times: Dict[str, float],
                          time_threshold: float = 2.0,
                          save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制配送时间分布图

        Args:
            delivery_times: 配送时间字典
            time_threshold: 时间阈值
            save_path: 保存路径

        Returns:
            matplotlib Figure对象
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.figsize_main)

        # 按时间排序
        sorted_times = sorted(delivery_times.items(), key=lambda x: x[1])
        villages = [item[0] for item in sorted_times]
        times = [item[1] for item in sorted_times]

        # 配送时间柱状图
        colors = ['green' if t <= time_threshold else 'red' for t in times]
        bars = ax1.bar(range(len(villages)), times, color=colors, alpha=0.7)

        ax1.axhline(y=time_threshold, color='orange', linestyle='--',
                   linewidth=2, label=f'时间阈值 ({time_threshold}h)')

        ax1.set_xlabel('村庄')
        ax1.set_ylabel('配送时间 (小时)')
        ax1.set_title('各村庄配送时间')
        ax1.set_xticks(range(len(villages)))
        ax1.set_xticklabels(villages, rotation=45, ha='right')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 配送时间分布直方图
        on_time = [t for t in times if t <= time_threshold]
        late = [t for t in times if t > time_threshold]

        ax2.hist([on_time, late], bins=10, label=['准时', '超时'],
                color=['green', 'red'], alpha=0.7)

        ax2.axvline(x=time_threshold, color='orange', linestyle='--',
                   linewidth=2, label=f'时间阈值 ({time_threshold}h)')

        ax2.set_xlabel('配送时间 (小时)')
        ax2.set_ylabel('村庄数量')
        ax2.set_title('配送时间分布')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        # 保存图片
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            self.logger.info(f"配送时间图已保存到: {save_path}")

        return fig

    def plot_optimization_history(self, history: List[float],
                                save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制优化历史图

        Args:
            history: 优化历史数据
            save_path: 保存路径

        Returns:
            matplotlib Figure对象
        """
        fig, ax = plt.subplots(figsize=self.figsize_single)

        ax.plot(history, linewidth=2, marker='o', markersize=3,
               color=self.color_palette[0])

        ax.set_xlabel('迭代代数')
        ax.set_ylabel('最优目标值')
        ax.set_title('遗传算法优化过程')
        ax.grid(True, alpha=0.3)

        # 添加统计信息
        final_value = history[-1]
        best_value = min(history)
        improvement = (history[0] - best_value) / history[0] * 100 if history[0] > 0 else 0

        ax.text(0.02, 0.98, '.2f'f'最终值: {final_value:.2f}\n'
                            f'最优值: {best_value:.2f}\n'
                            f'改进率: {improvement:.1f}%',
               transform=ax.transAxes, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        # 保存图片
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            self.logger.info(f"优化历史图已保存到: {save_path}")

        return fig

    def plot_demand_distribution(self, demands: Dict[str, float],
                               locations: Dict[str, Tuple[float, float]],
                               save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制需求分布图

        Args:
            demands: 需求量字典
            locations: 位置字典
            save_path: 保存路径

        Returns:
            matplotlib Figure对象
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.figsize_main)

        # 需求 vs 距离散点图
        depot_lat, depot_lon = locations.get("配送中心", (0, 0))
        distances = []
        demand_values = []

        for village, demand in demands.items():
            if village in locations and village != "配送中心":
                lat, lon = locations[village]
                distance = np.sqrt((lat - depot_lat)**2 + (lon - depot_lon)**2) * 111  # 近似km
                distances.append(distance)
                demand_values.append(demand)

        scatter = ax1.scatter(distances, demand_values,
                             s=np.array(demand_values) * 2,
                             alpha=0.6, c=distances, cmap='viridis')

        ax1.set_xlabel('距离配送中心 (km)')
        ax1.set_ylabel('需求量 (件)')
        ax1.set_title('村庄需求 vs 距离分布')
        ax1.grid(True, alpha=0.3)

        # 为每个点添加标签
        for village, distance, demand in zip(demands.keys(), distances, demand_values):
            if village != "配送中心":
                ax1.annotate(village, (distance, demand),
                           xytext=(5, 5), textcoords='offset points', fontsize=8)

        # 需求分布直方图
        ax2.hist(demand_values, bins=15, alpha=0.7, color=self.color_palette[0],
                edgecolor='black')
        ax2.set_xlabel('需求量 (件)')
        ax2.set_ylabel('村庄数量')
        ax2.set_title('需求量分布')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        # 保存图片
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            self.logger.info(f"需求分布图已保存到: {save_path}")

        return fig

    def create_comprehensive_report(self, analysis_results: Dict[str, Any],
                                  save_dir: str = "output") -> None:
        """
        创建综合可视化报告

        Args:
            analysis_results: 分析结果字典
            save_dir: 保存目录
        """
        Path(save_dir).mkdir(exist_ok=True)

        # 1. 配送网络图
        if 'routes' in analysis_results:
            network_fig = self.plot_delivery_network(
                analysis_results.get('locations', {}),
                analysis_results.get('routes', {}),
                analysis_results.get('drone_assignments', {}),
                save_path=f"{save_dir}/配送网络图.png"
            )
            plt.close(network_fig)

        # 2. 成本构成图
        if 'cost_breakdown' in analysis_results:
            cost_fig = self.plot_cost_breakdown(
                analysis_results['cost_breakdown'],
                save_path=f"{save_dir}/成本构成图.png"
            )
            plt.close(cost_fig)

        # 3. 配送时间分析
        if 'delivery_times' in analysis_results:
            time_fig = self.plot_delivery_times(
                analysis_results['delivery_times'],
                analysis_results.get('time_threshold', 2.0),
                save_path=f"{save_dir}/配送时间分析.png"
            )
            plt.close(time_fig)

        # 4. 优化历史
        if 'optimization_history' in analysis_results:
            history_fig = self.plot_optimization_history(
                analysis_results['optimization_history'],
                save_path=f"{save_dir}/优化历史.png"
            )
            plt.close(history_fig)

        # 5. 需求分布
        if 'demands' in analysis_results and 'locations' in analysis_results:
            demand_fig = self.plot_demand_distribution(
                analysis_results['demands'],
                analysis_results['locations'],
                save_path=f"{save_dir}/需求分布图.png"
            )
            plt.close(demand_fig)

        self.logger.info(f"综合可视化报告已生成，保存在: {save_dir}")


# 便捷函数
def plot_delivery_solution(locations: Dict[str, Tuple[float, float]],
                         routes: Dict[int, List[str]],
                         drone_assignments: Dict[str, int],
                         save_path: Optional[str] = None) -> plt.Figure:
    """便捷的配送方案可视化函数"""
    visualizer = DeliveryVisualizer()
    return visualizer.plot_delivery_network(locations, routes, drone_assignments, save_path)

def create_visualization_report(analysis_results: Dict[str, Any],
                              save_dir: str = "output") -> None:
    """创建完整的可视化报告"""
    visualizer = DeliveryVisualizer()
    visualizer.create_comprehensive_report(analysis_results, save_dir)
