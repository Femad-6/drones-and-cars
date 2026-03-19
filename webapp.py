#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
五龙镇配送优化系统 - Web应用界面
基于Streamlit的交互式Web应用
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import time
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import tempfile
import os

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from delivery_optimizer import DeliveryOptimizationSystem
    from config import get_config, get_config_manager
    from data.data_loader import DataLoader
    from utils.geographic_utils import GeographicCalculator
    from utils.map_api import SmartDistanceManager, BaiduMapAPI
except ImportError as e:
    st.error(f"模块导入失败: {e}")
    st.stop()

# 页面配置
st.set_page_config(
    page_title="五龙镇配送优化系统",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "五龙镇配送优化系统 v1.0.0"
    }
)

# 配置文件上传大小限制
try:
    # 设置文件上传大小限制为50MB
    import streamlit.config as st_config
    st_config.set_option('server.maxUploadSize', 50)
except:
    pass

# 自定义CSS样式
st.markdown("""
<style>
    :root {
        --brand-1: #0f766e;
        --brand-2: #14b8a6;
        --brand-3: #f59e0b;
        --ink-1: #0f172a;
        --ink-2: #334155;
        --bg-soft: #f8fafc;
        --card-bg: #ffffff;
        --card-border: #e2e8f0;
    }

    .stApp {
        background:
            radial-gradient(1200px 420px at 50% -80px, #dff7f3 0%, rgba(223, 247, 243, 0) 72%),
            linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }

    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 2rem;
    }

    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        text-align: center;
        letter-spacing: 0.02em;
        background: linear-gradient(95deg, var(--brand-1) 0%, var(--brand-2) 58%, #22c55e 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.6rem;
    }
    
    .sub-header {
        font-size: 1.05rem;
        text-align: center;
        color: var(--ink-2);
        margin-bottom: 1.6rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #0ea5a3 0%, #0f766e 100%);
        padding: 1rem;
        border-radius: 14px;
        color: white;
        text-align: center;
        margin: 0.35rem 0;
        box-shadow: 0 10px 20px rgba(15, 118, 110, 0.16);
        min-height: 112px;
    }
    
    .success-card {
        background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
        padding: 1rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
    }
    
    .info-card {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        padding: 1rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #ef4444 0%, #14b8a6 100%);
        color: white;
        border: none;
        border-radius: 999px;
        padding: 0.55rem 1.7rem;
        font-weight: 700;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 16px rgba(20, 184, 166, 0.22);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 1px solid var(--card-border);
    }

    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 10px 10px 0 0;
        font-weight: 700;
        color: var(--ink-2);
        padding: 0 14px;
    }

    .stTabs [aria-selected="true"] {
        color: var(--ink-1);
        background: #e6fffb;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
        border-right: 1px solid #e2e8f0;
    }

    [data-testid="stSidebar"] .stNumberInput,
    [data-testid="stSidebar"] .stSlider {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 10px;
        padding: 0.2rem 0.4rem;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """初始化会话状态"""
    if 'optimization_results' not in st.session_state:
        st.session_state.optimization_results = None
    if 'config_data' not in st.session_state:
        st.session_state.config_data = None
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = {}
    if 'baidu_api_key' not in st.session_state:
        st.session_state.baidu_api_key = ""
    if 'custom_locations' not in st.session_state:
        st.session_state.custom_locations = {}
    if 'distance_matrices' not in st.session_state:
        st.session_state.distance_matrices = None
    if 'use_smart_distance' not in st.session_state:
        st.session_state.use_smart_distance = False
    if 'custom_demands' not in st.session_state:
        st.session_state.custom_demands = None
    if 'use_custom_demands' not in st.session_state:
        st.session_state.use_custom_demands = False

def safe_get_individual_attr(individual, attr_name, default=None):
    """安全地获取Individual对象的属性"""
    if individual is None:
        return default
    
    try:
        if hasattr(individual, attr_name):
            value = getattr(individual, attr_name)
            return value if value is not None else default
        elif hasattr(individual, '__dict__') and attr_name in individual.__dict__:
            value = individual.__dict__[attr_name]
            return value if value is not None else default
        else:
            return default
    except Exception:
        return default

def safe_format_number(value, format_str=".2f", default_value=0):
    """安全地格式化数字"""
    if value is None:
        value = default_value
    try:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return f"{value:{format_str}}"
        else:
            return f"{float(default_value):{format_str}}"
    except (ValueError, TypeError):
        return f"{float(default_value):{format_str}}"

def safe_join(iterable, separator=", ", default="无数据"):
    """安全地连接可迭代对象"""
    if iterable is None:
        return default
    
    try:
        # 确保是可迭代的
        if isinstance(iterable, (list, tuple, set)):
            # 过滤掉None值和空字符串
            filtered_items = [str(item) for item in iterable if item is not None and str(item).strip()]
            return separator.join(filtered_items) if filtered_items else default
        elif isinstance(iterable, str):
            return iterable if iterable.strip() else default
        else:
            # 尝试转换为列表
            items = list(iterable)
            filtered_items = [str(item) for item in items if item is not None and str(item).strip()]
            return separator.join(filtered_items) if filtered_items else default
    except (TypeError, ValueError):
        return default

def safe_get_chromosome_attr(chromosome, attr_name, default=None):
    """安全地获取chromosome对象的属性"""
    if chromosome is None:
        return default
    
    try:
        if isinstance(chromosome, dict):
            return chromosome.get(attr_name, default)
        elif hasattr(chromosome, attr_name):
            return getattr(chromosome, attr_name, default)
        else:
            return default
    except Exception:
        return default

def display_header():
    """显示页面头部"""
    st.markdown('<h1 class="main-header">🚚 五龙镇配送优化系统</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">车辆-无人机协同配送路径智能优化平台</p>', unsafe_allow_html=True)
    
    # 系统信息卡片
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯 系统版本</h3>
            <p>v1.0.0</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>🚚 支持车辆</h3>
            <p>多车辆协同</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🚁 无人机配送</h3>
            <p>智能调度</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>🧬 优化算法</h3>
            <p>遗传算法</p>
        </div>
        """, unsafe_allow_html=True)

def create_sidebar():
    """创建侧边栏"""
    st.sidebar.title("📋 系统配置")
    st.sidebar.caption("调整关键参数后点击“执行优化”，结果会在“优化结果”标签页展示。")
    
    # 配置选项
    with st.sidebar.expander("🚚 车辆参数", expanded=True):
        num_vehicles = st.number_input("车辆数量", min_value=1, max_value=10, value=3)
        vehicle_capacity = st.number_input("车辆载重 (kg)", min_value=100, max_value=5000, value=1500)
        vehicle_speed = st.number_input("车辆速度 (km/h)", min_value=20, max_value=100, value=50)
        max_hours = st.number_input("最大工时 (小时)", min_value=4, max_value=12, value=8)
    
    with st.sidebar.expander("🚁 无人机参数", expanded=True):
        drone_payload = st.number_input("无人机载重 (kg)", min_value=10, max_value=200, value=80)
        drone_range = st.number_input("无人机航程 (km)", min_value=5, max_value=50, value=12)
        drone_speed = st.number_input("无人机速度 (km/h)", min_value=30, max_value=100, value=60)
    
    with st.sidebar.expander("🧬 算法参数", expanded=False):
        population_size = st.number_input("种群大小", min_value=50, max_value=500, value=150)
        generations = st.number_input("迭代代数", min_value=100, max_value=1000, value=500)
        mutation_rate = st.slider("变异率", min_value=0.1, max_value=0.5, value=0.25, step=0.05)
        crossover_rate = st.slider("交叉率", min_value=0.5, max_value=1.0, value=0.85, step=0.05)

    st.sidebar.markdown("---")
    st.sidebar.markdown("#### ⚡ 当前参数快照")
    snap_col1, snap_col2 = st.sidebar.columns(2)
    with snap_col1:
        st.metric("车辆", f"{num_vehicles} 台")
        st.metric("无人机", f"{drone_payload}kg")
    with snap_col2:
        st.metric("代数", f"{generations}")
        st.metric("变异率", f"{mutation_rate:.2f}")
    
    # 返回配置字典
    return {
        'vehicle_params': {
            'num_vehicles': num_vehicles,
            'capacity': vehicle_capacity,
            'speed': vehicle_speed,
            'max_hours': max_hours
        },
        'drone_params': {
            'max_payload': drone_payload,
            'max_range': drone_range,
            'speed': drone_speed
        },
        'ga_params': {
            'population_size': population_size,
            'generations': generations,
            'mutation_rate': mutation_rate,
            'crossover_rate': crossover_rate
        }
    }

def file_upload_section():
    """文件上传区域"""
    st.markdown("## 📁 数据文件上传")
    
    # 添加提示信息
    st.info("💡 提示：您可以使用默认数据进行测试，或上传自定义文件覆盖默认配置")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 车辆距离矩阵")
        
        # 检查默认文件状态
        default_file = Path("data/物流车配送距离.xlsx")
        if default_file.exists():
            st.success(f"✅ 已有默认距离文件: {default_file.name}")
        else:
            st.warning("⚠️ 未找到默认距离文件，请上传自定义文件")
        
        uploaded_distance = st.file_uploader(
            "上传Excel文件（可选）",
            type=['xlsx', 'xls'],
            key="distance_file",
            help="包含各地点间距离信息的Excel文件，留空则使用默认文件",
            accept_multiple_files=False
        )
        
        if uploaded_distance is not None:
            try:
                # 检查文件大小
                file_size = uploaded_distance.size / (1024 * 1024)  # MB
                if file_size > 10:
                    st.error(f"❌ 文件过大: {file_size:.1f}MB，请上传小于10MB的文件")
                    return
                
                # 读取文件
                bytes_data = uploaded_distance.getvalue()
                df = pd.read_excel(bytes_data)
                
                if df.empty:
                    st.error("❌ 文件为空，请检查文件内容")
                    return
                
                st.success(f"✅ 文件上传成功！数据形状: {df.shape}")
                st.dataframe(df.head(), width="stretch")
                
                # 保存到会话状态
                if 'uploaded_files' not in st.session_state:
                    st.session_state.uploaded_files = {}
                st.session_state.uploaded_files['distance'] = uploaded_distance
                
            except Exception as e:
                st.error(f"❌ 文件读取失败: {str(e)}")
                st.error("请确认文件格式正确且内容有效")
    
    with col2:
        st.markdown("### 📋 配置文件（可选）")
        
        # 显示默认配置状态
        st.info("🔧 系统将使用内置默认配置，上传JSON文件可覆盖部分设置")
        
        uploaded_config = st.file_uploader(
            "上传JSON配置文件（可选）",
            type=['json'],
            key="config_file",
            help="自定义配置参数的JSON文件，用于覆盖默认设置",
            accept_multiple_files=False
        )
        
        if uploaded_config is not None:
            try:
                # 检查文件大小
                file_size = uploaded_config.size / 1024  # KB
                if file_size > 500:  # 500KB限制
                    st.error(f"❌ 配置文件过大: {file_size:.1f}KB，请上传小于500KB的文件")
                    return
                
                # 读取JSON文件
                content = uploaded_config.getvalue().decode('utf-8')
                config_data = json.loads(content)
                
                if not isinstance(config_data, dict):
                    st.error("❌ 配置文件格式错误，应为JSON对象格式")
                    return
                
                st.success("✅ 配置文件上传成功！")
                with st.expander("查看配置内容"):
                    st.json(config_data)
                
                # 保存到会话状态
                if 'uploaded_files' not in st.session_state:
                    st.session_state.uploaded_files = {}
                st.session_state.uploaded_files['config'] = uploaded_config
                st.session_state.config_data = config_data
                
            except json.JSONDecodeError as e:
                st.error(f"❌ JSON格式错误: {str(e)}")
                st.error("请确认文件是有效的JSON格式")
            except UnicodeDecodeError:
                st.error("❌ 文件编码错误，请确保文件使用UTF-8编码")
            except Exception as e:
                st.error(f"❌ 配置文件读取失败: {str(e)}")
    
    # 添加文件清除选项
    if st.session_state.get('uploaded_files'):
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("🗑️ 清除上传文件"):
                st.session_state.uploaded_files = {}
                st.session_state.config_data = None
                st.rerun()
        with col2:
            if st.button("🔄 重置所有设置"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

def smart_distance_section():
    """智能距离配置区域"""
    st.markdown("## 🗺️ 智能距离配置")
    
    # 选择距离计算方式
    distance_mode = st.radio(
        "选择距离计算方式：",
        ["使用默认数据", "智能API距离计算"],
        help="默认数据使用内置的距离矩阵；智能计算通过百度地图API获取真实距离"
    )
    
    if distance_mode == "智能API距离计算":
        st.session_state.use_smart_distance = True
        
        # API密钥配置
        st.markdown("### 🔑 百度地图API配置")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            api_key = st.text_input(
                "百度地图API密钥",
                value=st.session_state.baidu_api_key,
                type="password",
                help="请在百度地图开放平台申请API密钥：https://lbsyun.baidu.com/"
            )
            
            if api_key != st.session_state.baidu_api_key:
                st.session_state.baidu_api_key = api_key
        
        with col2:
            if st.button("🔍 验证API", help="验证API密钥是否有效"):
                if api_key:
                    with st.spinner("验证API密钥..."):
                        try:
                            loader = DataLoader(api_key)
                            if loader.validate_api_key():
                                st.success("✅ API密钥验证成功！")
                            else:
                                st.error("❌ API密钥验证失败，请检查密钥是否正确")
                        except Exception as e:
                            st.error(f"❌ API验证出错: {e}")
                else:
                    st.warning("⚠️ 请先输入API密钥")
        
        # 地点配置
        st.markdown("### 📍 配送地点配置")
        
        # 选择输入方式
        input_mode = st.radio(
            "地点输入方式：",
            ["使用默认地点", "自定义地点列表"],
            horizontal=True
        )
        
        if input_mode == "自定义地点列表":
            st.info("💡 提示：请输入具体的地点名称，系统将通过百度地图API自动获取坐标")
            
            # 城市设置
            city = st.text_input("城市名称", value="济源市", help="地点所在的城市")
            
            # 地点列表输入
            locations_text = st.text_area(
                "配送地点列表",
                value="五龙镇政府\n丰峪村\n上庄村\n泽下村\n文峪村",
                height=200,
                help="请每行输入一个地点名称"
            )
            
            if st.button("🌍 解析地点坐标"):
                if locations_text.strip() and api_key:
                    locations_list = [loc.strip() for loc in locations_text.split('\n') if loc.strip()]
                    
                    with st.spinner(f"正在解析 {len(locations_list)} 个地点的坐标..."):
                        try:
                            loader = DataLoader(api_key)
                            locations_dict = loader.load_locations_from_text(locations_list, city)
                            
                            if locations_dict:
                                st.session_state.custom_locations = locations_dict
                                st.success(f"✅ 成功解析 {len(locations_dict)} 个地点坐标")
                                
                                # 显示解析结果
                                with st.expander("查看解析结果", expanded=True):
                                    df_locations = pd.DataFrame([
                                        {"地点": name, "纬度": f"{coord[0]:.6f}", "经度": f"{coord[1]:.6f}"}
                                        for name, coord in locations_dict.items()
                                    ])
                                    st.dataframe(df_locations, width="stretch")
                            else:
                                st.error("❌ 未能解析任何地点坐标，请检查地点名称和API密钥")
                        except Exception as e:
                            st.error(f"❌ 地点解析失败: {e}")
                else:
                    if not api_key:
                        st.warning("⚠️ 请先配置百度地图API密钥")
                    else:
                        st.warning("⚠️ 请输入地点列表")
        
        # 距离矩阵生成
        if api_key and (input_mode == "使用默认地点" or st.session_state.custom_locations):
            st.markdown("### 🛣️ 距离矩阵生成")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🚗 生成智能距离矩阵", width="stretch"):
                    generate_smart_distance_matrices(api_key, input_mode)
            
            with col2:
                if st.session_state.distance_matrices is not None:
                    if st.button("💾 保存距离矩阵", width="stretch"):
                        save_distance_matrices()
        
        # 显示已生成的距离矩阵信息
        if st.session_state.distance_matrices is not None:
            st.success("✅ 智能距离矩阵已生成！")
            vehicle_matrix, drone_matrix = st.session_state.distance_matrices
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🚗 车辆距离矩阵", f"{vehicle_matrix.shape[0]}×{vehicle_matrix.shape[1]}")
                st.metric("📏 平均车辆距离", f"{np.mean(vehicle_matrix[vehicle_matrix > 0]):.2f} km")
            
            with col2:
                st.metric("🚁 无人机距离矩阵", f"{drone_matrix.shape[0]}×{drone_matrix.shape[1]}")
                st.metric("📏 平均直线距离", f"{np.mean(drone_matrix[drone_matrix > 0]):.2f} km")
    
    else:
        st.session_state.use_smart_distance = False
        st.info("🏠 使用系统内置的默认距离数据进行优化")

def generate_smart_distance_matrices(api_key: str, input_mode: str):
    """生成智能距离矩阵"""
    with st.spinner("🚗 正在通过百度地图API获取车辆真实行驶距离..."):
        try:
            # 创建进度条
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 获取地点数据
            if input_mode == "使用默认地点":
                locations = get_config('locations', {})
                status_text.text("📍 使用默认地点数据...")
            else:
                locations = st.session_state.custom_locations
                status_text.text("📍 使用自定义地点数据...")
            
            progress_bar.progress(20)
            
            # 生成距离矩阵
            loader = DataLoader(api_key)
            status_text.text("🛣️ 正在计算距离矩阵...")
            
            vehicle_matrix, drone_matrix = loader.generate_smart_distance_matrices(
                locations, use_baidu_api=True
            )
            
            progress_bar.progress(80)
            status_text.text("💾 保存结果...")
            
            # 保存到session state
            st.session_state.distance_matrices = (vehicle_matrix, drone_matrix)
            
            progress_bar.progress(100)
            status_text.text("✅ 完成！")
            
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            
            # 显示统计信息
            st.success("🎉 智能距离矩阵生成成功！")
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"🚗 车辆距离：通过百度地图API获取\n"
                       f"📊 矩阵大小：{vehicle_matrix.shape[0]}×{vehicle_matrix.shape[1]}\n"
                       f"📏 最大距离：{np.max(vehicle_matrix):.2f} km")
            
            with col2:
                st.info(f"🚁 无人机距离：坐标直线距离\n"
                       f"📊 矩阵大小：{drone_matrix.shape[0]}×{drone_matrix.shape[1]}\n"
                       f"📏 最大距离：{np.max(drone_matrix):.2f} km")
                
        except Exception as e:
            st.error(f"❌ 距离矩阵生成失败: {e}")
            st.error("建议检查API密钥配置和网络连接")

def save_distance_matrices():
    """保存距离矩阵到文件"""
    if st.session_state.distance_matrices is None:
        st.warning("⚠️ 没有可保存的距离矩阵")
        return
    
    try:
        vehicle_matrix, drone_matrix = st.session_state.distance_matrices
        
        # 获取地点名称
        if st.session_state.custom_locations:
            location_names = list(st.session_state.custom_locations.keys())
        else:
            location_names = list(get_config('locations', {}).keys())
        
        # 保存矩阵
        loader = DataLoader(st.session_state.baidu_api_key)
        loader.save_smart_distance_matrices(
            vehicle_matrix, drone_matrix, location_names, "data"
        )
        
        st.success("✅ 距离矩阵已保存到 data/ 目录")
        st.info("📁 生成的文件：\n- 车辆距离矩阵_API.xlsx\n- 无人机距离矩阵.xlsx")
        
    except Exception as e:
        st.error(f"❌ 保存失败: {e}")

def demand_editing_section():
    """包裹需求编辑区域"""
    st.markdown("## 📦 包裹需求配置")
    
    # 选择需求配置方式
    demand_mode = st.radio(
        "选择需求配置方式：",
        ["使用默认需求", "自定义包裹需求"],
        help="默认需求使用系统内置数据；自定义需求允许修改各村庄的包裹需求量"
    )
    
    if demand_mode == "自定义包裹需求":
        st.session_state.use_custom_demands = True
        
        # 获取默认需求数据作为基础
        default_demands = get_config('demands_piece', {})
        
        # 如果还没有自定义需求，则使用默认需求初始化
        if st.session_state.custom_demands is None:
            st.session_state.custom_demands = default_demands.copy()
        
        st.markdown("### 📊 需求数据编辑")
        st.info("💡 提示：您可以修改各村庄的包裹需求量，系统将根据新的需求量进行优化计算")
        
        # 创建可编辑的数据表格
        display_demand_editor()
        
        # 需求分析和统计
        display_demand_statistics()
        
    else:
        st.session_state.use_custom_demands = False
        st.info("🏠 使用系统内置的默认需求数据进行优化")
        
        # 显示默认需求统计
        display_default_demand_info()

def display_demand_editor():
    """显示需求编辑器"""
    demands = st.session_state.custom_demands
    
    if not demands:
        st.warning("⚠️ 无法获取需求数据")
        return
    
    # 转换为DataFrame便于编辑
    df_demands = pd.DataFrame([
        {"村庄名称": village, "包裹需求(件)": demand}
        for village, demand in demands.items()
    ])
    
    # 分列显示编辑器
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("#### 📝 编辑需求数据")
        
        # 使用data_editor进行表格编辑
        edited_df = st.data_editor(
            df_demands,
            column_config={
                "村庄名称": st.column_config.TextColumn(
                    "村庄名称",
                    help="村庄名称（不可修改）",
                    disabled=True,
                    width="medium"
                ),
                "包裹需求(件)": st.column_config.NumberColumn(
                    "包裹需求(件)",
                    help="该村庄的包裹需求量",
                    min_value=0,
                    max_value=10000,
                    step=1,
                    format="%d",
                    width="medium"
                )
            },
            num_rows="fixed",
            width="stretch",
            key="demand_editor"
        )
        
        # 批量操作区域
        st.markdown("#### ⚡ 批量操作")
        
        batch_col1, batch_col2, batch_col3 = st.columns(3)
        
        with batch_col1:
            if st.button("📈 按比例调整", width="stretch"):
                show_batch_adjustment()
        
        with batch_col2:
            if st.button("📥 导入Excel", width="stretch"):
                show_import_demands()
        
        with batch_col3:
            if st.button("💾 导出Excel", width="stretch"):
                export_demands_to_excel(edited_df)
    
    with col2:
        st.markdown("#### 🔧 操作面板")
        
        # 应用更改按钮
        if st.button("✅ 应用更改", width="stretch", type="primary"):
            # 将编辑后的数据保存到session state
            new_demands = {}
            for _, row in edited_df.iterrows():
                village = row["村庄名称"]
                demand = max(0, int(row["包裹需求(件)"]))  # 确保非负整数
                new_demands[village] = demand
            
            st.session_state.custom_demands = new_demands
            st.success("✅ 需求数据已更新！")
            st.rerun()
        
        # 重置按钮
        if st.button("🔄 重置为默认", width="stretch"):
            default_demands = get_config('demands_piece', {})
            st.session_state.custom_demands = default_demands.copy()
            st.success("🔄 已重置为默认需求数据")
            st.rerun()
        
        # 验证数据按钮
        if st.button("🔍 验证数据", width="stretch"):
            validate_demand_data(edited_df)

def show_batch_adjustment():
    """显示批量调整界面"""
    with st.expander("📈 批量按比例调整", expanded=True):
        adjustment_type = st.selectbox(
            "调整方式",
            ["全部村庄", "选定村庄", "需求范围"]
        )
        
        if adjustment_type == "全部村庄":
            ratio = st.slider("调整比例", 0.1, 3.0, 1.0, 0.1, format="%.1f倍")
            
            if st.button("应用到全部村庄"):
                for village in st.session_state.custom_demands:
                    current_demand = st.session_state.custom_demands[village]
                    new_demand = max(1, int(current_demand * ratio))
                    st.session_state.custom_demands[village] = new_demand
                st.success(f"✅ 已将所有村庄需求调整为 {ratio:.1f} 倍")
                st.rerun()
        
        elif adjustment_type == "选定村庄":
            selected_villages = st.multiselect(
                "选择村庄",
                options=list(st.session_state.custom_demands.keys())
            )
            ratio = st.slider("调整比例", 0.1, 3.0, 1.0, 0.1, format="%.1f倍", key="selected_ratio")
            
            if st.button("应用到选定村庄") and selected_villages:
                for village in selected_villages:
                    current_demand = st.session_state.custom_demands[village]
                    new_demand = max(1, int(current_demand * ratio))
                    st.session_state.custom_demands[village] = new_demand
                st.success(f"✅ 已将选定村庄需求调整为 {ratio:.1f} 倍")
                st.rerun()

def show_import_demands():
    """显示导入需求界面"""
    with st.expander("📥 从Excel导入需求数据", expanded=True):
        uploaded_file = st.file_uploader(
            "选择Excel文件",
            type=['xlsx', 'xls'],
            help="Excel文件应包含'村庄名称'和'包裹需求'两列"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file)
                
                # 检查必要的列
                required_cols = ['村庄名称', '包裹需求']
                missing_cols = [col for col in required_cols if col not in df.columns]
                
                if missing_cols:
                    st.error(f"❌ 缺少必要的列: {', '.join(missing_cols)}")
                    return
                
                # 预览数据
                st.dataframe(df.head())
                
                if st.button("💾 导入数据"):
                    # 更新需求数据
                    for _, row in df.iterrows():
                        village = str(row['村庄名称']).strip()
                        demand = max(0, int(row['包裹需求']))
                        
                        if village in st.session_state.custom_demands:
                            st.session_state.custom_demands[village] = demand
                    
                    st.success("✅ 需求数据导入成功！")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ 文件读取失败: {e}")

def export_demands_to_excel(df_demands):
    """导出需求数据到Excel"""
    try:
        import io
        
        # 创建Excel文件
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_demands.to_excel(writer, index=False, sheet_name='包裹需求')
        
        excel_data = output.getvalue()
        
        # 创建下载按钮
        st.download_button(
            label="📥 下载Excel文件",
            data=excel_data,
            file_name=f"包裹需求数据_{time.strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        st.error(f"❌ 导出失败: {e}")

def validate_demand_data(df_demands):
    """验证需求数据"""
    errors = []
    warnings = []
    
    # 检查数据完整性
    if df_demands.empty:
        errors.append("需求数据为空")
    
    # 检查数值有效性
    for _, row in df_demands.iterrows():
        village = row["村庄名称"]
        demand = row["包裹需求(件)"]
        
        if pd.isna(demand):
            errors.append(f"{village}: 需求量不能为空")
        elif demand < 0:
            errors.append(f"{village}: 需求量不能为负数")
        elif demand == 0:
            warnings.append(f"{village}: 需求量为0，该村庄将不会被配送")
        elif demand > 5000:
            warnings.append(f"{village}: 需求量过大({demand}件)，请确认是否正确")
    
    # 显示验证结果
    if errors:
        st.error("❌ 数据验证失败：")
        for error in errors:
            st.error(f"  • {error}")
    else:
        st.success("✅ 数据验证通过！")
    
    if warnings:
        st.warning("⚠️ 注意事项：")
        for warning in warnings:
            st.warning(f"  • {warning}")

def display_demand_statistics():
    """显示需求统计"""
    demands = st.session_state.custom_demands
    
    if not demands:
        return
    
    st.markdown("### 📊 需求统计分析")
    
    # 计算统计数据
    demand_values = list(demands.values())
    total_demand = sum(demand_values)
    avg_demand = np.mean(demand_values)
    max_demand = max(demand_values)
    min_demand = min(demand_values)
    
    # 显示统计卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 总需求量", f"{total_demand:,} 件")
    
    with col2:
        st.metric("📊 平均需求", f"{avg_demand:.0f} 件")
    
    with col3:
        st.metric("📈 最大需求", f"{max_demand:,} 件")
    
    with col4:
        st.metric("📉 最小需求", f"{min_demand:,} 件")
    
    # 需求分布图表
    col1, col2 = st.columns(2)
    
    with col1:
        # 需求分布直方图
        fig_hist = px.histogram(
            x=demand_values,
            nbins=10,
            title="需求量分布",
            labels={'x': '需求量(件)', 'y': '村庄数量'}
        )
        st.plotly_chart(fig_hist, width="stretch")
    
    with col2:
        # 村庄需求排序图
        df_sorted = pd.DataFrame([
            {"村庄": village, "需求量": demand}
            for village, demand in demands.items()
        ]).sort_values("需求量", ascending=False).head(10)
        
        fig_bar = px.bar(
            df_sorted,
            x="需求量",
            y="村庄",
            orientation="h",
            title="需求量Top10村庄",
            labels={'需求量': '需求量(件)', '村庄': '村庄名称'}
        )
        st.plotly_chart(fig_bar, width="stretch")

def display_default_demand_info():
    """显示默认需求信息"""
    default_demands = get_config('demands_piece', {})
    transfer_station = get_config('wulong_transfer_station', {})
    
    if not default_demands:
        st.warning("⚠️ 无法获取默认需求数据")
        return
    
    # 五龙镇中转站信息
    st.markdown("### 🏢 五龙镇中转站")
    if transfer_station:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_packages = transfer_station.get('total_downstream_packages', 0)
            st.metric("📦 中转总量", f"{total_packages:,} 件")
        
        with col2:
            service_areas = len(transfer_station.get('service_areas', []))
            st.metric("🏘️ 服务村庄", f"{service_areas} 个")
        
        with col3:
            peak_throughput = transfer_station.get('operational_metrics', {}).get('daily_throughput', {}).get('peak_days', 0)
            st.metric("📈 峰值吞吐", f"{peak_throughput} 件/日")
        
        with col4:
            storage_capacity = transfer_station.get('operational_metrics', {}).get('storage_capacity', {}).get('downstream_storage', 0)
            st.metric("🏪 仓储容量", f"{storage_capacity} 件")
        
        # 中转站详细信息
        with st.expander("🔍 中转站详细信息", expanded=False):
            display_transfer_station_details(transfer_station)
    
    st.markdown("### 📊 村庄需求统计")
    
    # 统计信息
    total_demand = sum(default_demands.values())
    village_count = len(default_demands)
    avg_demand = total_demand / village_count if village_count > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📦 总需求量", f"{total_demand:,} 件")
    
    with col2:
        st.metric("🏘️ 服务村庄", f"{village_count} 个")
    
    with col3:
        st.metric("📊 平均需求", f"{avg_demand:.0f} 件/村")
    
    # 显示默认需求数据表格
    with st.expander("📋 查看村庄需求数据", expanded=False):
        df_default = pd.DataFrame([
            {"村庄名称": village, "包裹需求(件)": demand}
            for village, demand in default_demands.items()
        ]).sort_values("包裹需求(件)", ascending=False)
        
        st.dataframe(df_default, width="stretch")
    
    # 详细货物分类显示
    display_cargo_details_section()
    
    # 上行包裹详细显示
    display_upstream_packages_section()

def optimization_section():
    """优化执行区域"""
    st.markdown("## 🚀 开始优化")
    
    # 获取侧边栏配置
    sidebar_config = create_sidebar()
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        if st.button("🎯 执行优化", width="stretch"):
            run_optimization(sidebar_config)
    
    # 显示当前配置摘要
    with st.expander("📋 当前配置摘要", expanded=False):
        display_config_summary(sidebar_config)
        
def display_config_summary(config: Dict[str, Any]):
    """显示配置摘要"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🚚 系统配置")
        st.json(config)
    
    with col2:
        st.markdown("#### 📦 需求配置")
        if st.session_state.use_custom_demands and st.session_state.custom_demands:
            demand_summary = {
                "配置类型": "自定义需求",
                "村庄数量": len(st.session_state.custom_demands),
                "总需求量": sum(st.session_state.custom_demands.values()),
                "平均需求": round(sum(st.session_state.custom_demands.values()) / len(st.session_state.custom_demands), 1),
                "最高需求村庄": max(st.session_state.custom_demands.items(), key=lambda x: x[1])[0],
                "最高需求量": max(st.session_state.custom_demands.values())
            }
        else:
            default_demands = get_config('demands_piece', {})
            demand_summary = {
                "配置类型": "默认需求",
                "村庄数量": len(default_demands),
                "总需求量": sum(default_demands.values()),
                "平均需求": round(sum(default_demands.values()) / len(default_demands), 1) if default_demands else 0
            }
        st.json(demand_summary)

def run_optimization(config: Dict[str, Any]):
    """运行优化算法"""
    try:
        with st.spinner("🔄 正在执行优化算法，请稍候..."):
            # 创建进度条
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 更新配置
            config_manager = get_config_manager()
            for section, params in config.items():
                for key, value in params.items():
                    config_manager.set(f"{section}.{key}", value)
            
            # 如果用户设置了自定义需求，则更新配置
            if st.session_state.use_custom_demands and st.session_state.custom_demands:
                status_text.text("📦 应用自定义需求数据...")
                config_manager.set("demands_piece", st.session_state.custom_demands)
                st.info(f"✅ 使用自定义需求数据：共{len(st.session_state.custom_demands)}个村庄，总需求{sum(st.session_state.custom_demands.values())}件")
            
            progress_bar.progress(20)
            status_text.text("⚙️ 初始化优化系统...")
            
            # 创建优化系统，传递百度API密钥
            optimizer = DeliveryOptimizationSystem(baidu_api_key=st.session_state.baidu_api_key)
            
            progress_bar.progress(40)
            status_text.text("📊 加载数据...")
            
            # 加载数据（如果有智能距离矩阵则使用）
            distance_matrices = None
            if st.session_state.distance_matrices is not None:
                distance_matrices = st.session_state.distance_matrices
                status_text.text("📊 使用智能API距离矩阵加载数据...")
            else:
                status_text.text("📊 使用默认距离矩阵加载数据...")
            
            load_success = optimizer.load_data(distance_matrices)
            if not load_success:
                st.error("❌ 数据加载失败")
                progress_bar.empty()
                status_text.empty()
                return
            
            progress_bar.progress(50)
            status_text.text("⚙️ 初始化优化器...")
            
            # 初始化优化器
            init_success = optimizer.initialize_optimizer()
            if not init_success:
                st.error("❌ 优化器初始化失败")
                progress_bar.empty()
                status_text.empty()
                return
            
            progress_bar.progress(60)
            status_text.text("🧬 运行遗传算法...")
            
            # 运行优化
            opt_success = optimizer.run_optimization()
            if not opt_success:
                st.error("❌ 优化算法执行失败")
                progress_bar.empty()
                status_text.empty()
                return
            
            progress_bar.progress(80)
            status_text.text("📈 生成分析报告...")
            
            # 生成详细分析
            analysis_success = optimizer.analyze_solution()
            if not analysis_success:
                st.warning("⚠️ 分析报告生成失败，但优化结果可用")
            
            # 获取结果
            results = optimizer.results
            detailed_results = results.get('analysis', {})
            
            progress_bar.progress(100)
            status_text.text("✅ 优化完成！")
            
            # 保存结果到会话状态
            st.session_state.optimization_results = {
                'basic': results,
                'detailed': detailed_results,
                'config': config,
                'optimizer': optimizer  # 保存优化器实例以便获取更多数据
            }
            
            time.sleep(1)  # 让用户看到完成状态
            progress_bar.empty()
            status_text.empty()
            
            st.success("🎉 优化算法执行成功！请查看下方结果。")
            
    except Exception as e:
        st.error(f"❌ 优化执行失败: {e}")
        st.exception(e)

def display_results():
    """显示优化结果"""
    if st.session_state.optimization_results is None:
        st.info("👆 请先执行优化算法以查看结果")
        return
    
    try:
        results = st.session_state.optimization_results
        basic_results = results['basic']
        detailed_results = results['detailed']
    except Exception as e:
        st.error(f"❌ 获取优化结果时出错: {e}")
        st.error("请重新运行优化算法")
        return
    
    st.markdown("## 📊 优化结果")
    
    # 关键指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_cost = detailed_results.get('total_cost', basic_results.get('total_cost', 0))
        st.metric(
            "💰 总成本",
            f"{safe_format_number(total_cost, '.2f', 0)} 元",
            delta=None
        )
    
    with col2:
        opt_time = basic_results.get('optimization_time', 0)
        st.metric(
            "⏱️ 优化耗时",
            f"{safe_format_number(opt_time, '.2f', 0)} 秒",
            delta=None
        )
    
    with col3:
        best_solution = basic_results.get('best_solution')
        best_fitness = safe_get_individual_attr(best_solution, 'fitness', 0)
        st.metric(
            "🎯 最优适应度",
            safe_format_number(best_fitness, '.2f', 0),
            delta=None
        )
    
    with col4:
        # 从详细结果中计算准时率
        time_eval = detailed_results.get('time_constraint_evaluation', 0.5)
        delivery_ratio = time_eval * 100 if time_eval is not None else 50.0
        st.metric(
            "⏰ 时间评估",
            f"{safe_format_number(delivery_ratio, '.1f', 50.0)}%",
            delta=None
        )
    
    # 详细结果选项卡
    tab1, tab2, tab3, tab4 = st.tabs(["🚚 配送方案", "📈 成本分析", "🗺️ 路径地图", "📋 详细报告"])
    
    with tab1:
        display_delivery_plan(detailed_results)
    
    with tab2:
        display_cost_analysis(detailed_results)
    
    with tab3:
        display_route_map(detailed_results)
    
    with tab4:
        display_detailed_report(detailed_results)

def display_delivery_plan(results: Dict[str, Any]):
    """显示配送方案"""
    st.markdown("### 🚚 车辆配送方案")
    
    # 从优化器获取位置名称映射
    optimizer = st.session_state.optimization_results.get('optimizer')
    if optimizer and hasattr(optimizer, 'locations'):
        location_names = list(optimizer.locations.keys())
        
        # 从最优解中获取车辆路径
        best_solution = st.session_state.optimization_results['basic'].get('best_solution')
        chromosome = safe_get_individual_attr(best_solution, 'chromosome')
        vehicle_assignments = safe_get_chromosome_attr(chromosome, 'vehicle_assignment', [])
        
        if isinstance(vehicle_assignments, np.ndarray):
            vehicle_assignments = vehicle_assignments.tolist()
        
        # 按车辆分组显示
        if vehicle_assignments:
            vehicle_routes = {}
            for i, vehicle_id in enumerate(vehicle_assignments):
                if vehicle_id not in vehicle_routes:
                    vehicle_routes[vehicle_id] = []
                if i < len(location_names):
                    village_name = location_names[i]
                    if village_name not in ['配送中心', '五龙镇']:  # 排除配送中心和五龙镇
                        vehicle_routes[vehicle_id].append(village_name)
            
            for vehicle_id, villages in vehicle_routes.items():
                if villages:  # 只显示有分配村庄的车辆
                    with st.expander(f"车辆 {vehicle_id + 1} - {len(villages)} 个村庄", expanded=True):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write("**配送村庄:**")
                            village_list = safe_join(villages, ", ", "暂无村庄")
                            st.write(village_list)
                        
                        with col2:
                            st.metric("村庄数量", len(villages))
                            # 这里可以添加更多统计信息
        else:
            st.info("暂无车辆路径数据")
    
    st.markdown("### 🚁 无人机配送方案")
    # 简化的无人机显示逻辑
    st.info("无人机配送方案将根据实际优化结果显示")

def display_cost_analysis(results: Dict[str, Any]):
    """显示成本分析"""
    st.markdown("### 💰 成本构成分析")
    
    # 创建成本构成饼图
    cost_data = results.get('cost_breakdown', {})
    if cost_data:
        fig = px.pie(
            values=list(cost_data.values()),
            names=list(cost_data.keys()),
            title="成本构成分布",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, width="stretch")
    
    # 成本明细表
    if cost_data:
        try:
            total_cost = sum(cost_data.values())
            df_cost = pd.DataFrame([
                {
                    "成本项目": k, 
                    "金额 (元)": safe_format_number(v, '.2f', 0),
                    "占比": f"{safe_format_number(v/total_cost*100 if total_cost > 0 else 0, '.1f', 0)}%"
                }
                for k, v in cost_data.items() if v is not None
            ])
            st.dataframe(df_cost, width="stretch")
        except Exception as e:
            st.error(f"成本数据显示出错: {e}")
            st.info("成本数据格式不正确，请重新运行优化")

def display_route_map(results: Dict[str, Any]):
    """显示路径地图"""
    st.markdown("### 🗺️ 配送路径地图")
    
    try:
        # 获取位置数据
        locations = get_config('locations', {})
        
        if not locations:
            st.warning("⚠️ 缺少位置数据，无法显示地图")
            return
        
        # 创建地图数据
        map_data = []
        for name, (lat, lon) in locations.items():
            map_data.append({
                'name': name,
                'lat': lat,
                'lon': lon,
                'type': '配送中心' if name == '配送中心' else ('五龙镇' if name == '五龙镇' else '村庄')
            })
        
        df_map = pd.DataFrame(map_data)
        
        # 创建散点地图
        fig = px.scatter_map(
            df_map,
            lat="lat",
            lon="lon",
            hover_name="name",
            color="type",
            size_max=15,
            zoom=11,
            map_style="open-street-map",
            title="五龙镇配送网络地图",
            color_discrete_map={
                '配送中心': '#FF6B6B',
                '五龙镇': '#4ECDC4',
                '村庄': '#45B7D1'
            }
        )

        fig.update_layout(height=600)
        
        st.plotly_chart(fig, width="stretch")
        
        # 添加图例说明
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("🔴 **配送中心** - 物流起点")
        with col2:
            st.markdown("🟡 **五龙镇** - 中转站点")
        with col3:
            st.markdown("🔵 **村庄** - 配送目的地")
        
    except Exception as e:
        st.error(f"地图显示失败: {e}")

def display_detailed_report(results: Dict[str, Any]):
    """显示详细报告"""
    st.markdown("### 📋 详细优化报告")
    
    # 生成报告文本
    report_text = generate_report_text(results)
    
    # 显示报告
    st.text_area("优化报告内容", report_text, height=400)
    
    # 下载按钮
    col1, col2 = st.columns([1, 4])
    with col1:
        st.download_button(
            label="📥 下载报告",
            data=report_text,
            file_name=f"五龙镇配送优化报告_{time.strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    
    # JSON格式结果下载
    with col2:
        json_data = json.dumps(results, ensure_ascii=False, indent=2)
        st.download_button(
            label="📥 下载JSON数据",
            data=json_data,
            file_name=f"优化结果_{time.strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

def generate_report_text(results: Dict[str, Any]) -> str:
    """生成报告文本"""
    report = []
    report.append("=" * 60)
    report.append("五龙镇配送优化系统 - 优化报告")
    report.append("=" * 60)
    report.append(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # 基本信息
    report.append("📊 优化结果摘要:")
    if 'total_cost' in results:
        total_cost = results['total_cost']
        report.append(f"  总成本: {safe_format_number(total_cost, '.2f', 0)} 元")
    if 'optimization_time' in results:
        opt_time = results['optimization_time']
        report.append(f"  优化耗时: {safe_format_number(opt_time, '.2f', 0)} 秒")
    if 'objective_value' in results:
        obj_value = results['objective_value']
        report.append(f"  目标函数值: {safe_format_number(obj_value, '.2f', 0)}")
    
    report.append("")
    
    # 车辆方案
    if 'vehicle_routes' in results:
        report.append("🚚 车辆配送方案:")
        vehicle_routes = results['vehicle_routes']
        if vehicle_routes:
            for i, route in enumerate(vehicle_routes, 1):
                village_list = safe_join(route, ", ", "暂无配送村庄")
                report.append(f"  车辆{i}: {village_list}")
        else:
            report.append("  暂无车辆配送方案")
        report.append("")
    
    # 无人机方案
    if 'drone_deliveries' in results:
        drone_villages = results['drone_deliveries']
        if drone_villages:
            report.append("🚁 无人机配送:")
            village_list = safe_join(drone_villages, ", ", "暂无配送村庄")
            report.append(f"  配送村庄: {village_list}")
        else:
            report.append("🚁 无人机配送: 暂无")
        report.append("")
    
    # 成本分析
    if 'cost_breakdown' in results:
        report.append("💰 成本构成:")
        for item, cost in results['cost_breakdown'].items():
            if cost is not None:
                report.append(f"  {item}: {safe_format_number(cost, '.2f', 0)} 元")
        report.append("")
    
    report.append("=" * 60)
    
    return "\n".join(report)

def main():
    """主函数"""
    # 初始化会话状态
    init_session_state()
    
    # 显示头部
    display_header()
    
    # 将流程拆分为标签页，减少单页纵向滚动
    setup_tab, optimize_tab, result_tab = st.tabs([
        "⚙️ 数据与配置",
        "🚀 执行优化",
        "📊 优化结果"
    ])

    with setup_tab:
        file_upload_section()
        st.markdown("---")
        smart_distance_section()
        st.markdown("---")
        demand_editing_section()

    with optimize_tab:
        optimization_section()

    with result_tab:
        display_results()
    
    # 页脚
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>© 2025 五龙镇配送优化系统 | 版本 1.0.0 | 基于遗传算法的智能优化平台</p>
    </div>
    """, unsafe_allow_html=True)

def display_transfer_station_details(transfer_station: Dict[str, Any]):
    """显示中转站详细信息"""
    if not transfer_station:
        st.warning("⚠️ 无法获取中转站数据")
        return
    
    # 汇总数据
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 货物汇总")
        cargo_summary = transfer_station.get('cargo_summary', {})
        if cargo_summary:
            st.write(f"- 💼 轻包裹：{cargo_summary.get('light_packages', 0):,} 件")
            st.write(f"- 📦 重包裹：{cargo_summary.get('heavy_packages', 0):,} 件")
            st.write(f"- 🔧 易碎物品：{cargo_summary.get('fragile_items', 0):,} 件")
    
    with col2:
        st.markdown("#### 📈 运营指标")
        operational = transfer_station.get('operational_metrics', {})
        if operational:
            daily_throughput = operational.get('daily_throughput', {})
            st.write(f"- 🌟 峰值日吞吐：{daily_throughput.get('peak_days', 0)} 件")
            st.write(f"- 📊 正常日吞吐：{daily_throughput.get('normal_days', 0)} 件")
            st.write(f"- 🔽 低峰日吞吐：{daily_throughput.get('low_days', 0)} 件")
    
    # 上行数据汇总
    st.markdown("#### 📤 上行包裹汇总")
    upstream_summary = transfer_station.get('upstream_summary', {})
    if upstream_summary:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            recyclables = upstream_summary.get('total_recyclables', {})
            if recyclables:
                st.write("**♻️ 回收品**")
                st.write(f"- 📄 纸类：{recyclables.get('paper', 0):,} 件")
                st.write(f"- 🥤 塑料：{recyclables.get('plastic', 0):,} 件")
                st.write(f"- 📱 电子产品：{recyclables.get('electronics', 0):,} 件")
        
        with col2:
            agricultural = upstream_summary.get('total_agricultural_products', {})
            if agricultural:
                st.write("**🌾 农产品**")
                st.write(f"- 🍎 水果：{agricultural.get('fruits', 0):,} 件")
                st.write(f"- 🥬 蔬菜：{agricultural.get('vegetables', 0):,} 件")
                st.write(f"- 🌾 粮食：{agricultural.get('grains', 0):,} 件")
        
        with col3:
            crafts = upstream_summary.get('total_handmade_crafts', {})
            returns = upstream_summary.get('total_return_packages', {})
            if crafts or returns:
                st.write("**🎨 手工艺品**")
                st.write(f"- 🧵 纺织品：{crafts.get('textiles', 0):,} 件")
                st.write(f"- 🪵 木工制品：{crafts.get('woodwork', 0):,} 件")
                st.write(f"- 🏺 陶器：{crafts.get('pottery', 0):,} 件")
                
                st.write("**↩️ 退货包裹**")
                st.write(f"- 💥 损坏：{returns.get('damaged', 0):,} 件")
                st.write(f"- 📮 错配：{returns.get('wrong_delivery', 0):,} 件")

def display_cargo_details_section():
    """显示货物详细分类数据"""
    st.markdown("### 📦 详细货物分类")
    
    cargo_details = get_config('cargo_details', {})
    if not cargo_details:
        st.info("ℹ️ 暂无详细货物分类数据")
        return
    
    # 计算总计
    total_light = sum(details.get('light_packages', 0) for details in cargo_details.values())
    total_heavy = sum(details.get('heavy_packages', 0) for details in cargo_details.values())
    total_fragile = sum(details.get('fragile_items', 0) for details in cargo_details.values())
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💼 轻包裹总计", f"{total_light:,} 件")
    
    with col2:
        st.metric("📦 重包裹总计", f"{total_heavy:,} 件")
    
    with col3:
        st.metric("🔧 易碎物品总计", f"{total_fragile:,} 件")
    
    # 详细表格
    with st.expander("📋 查看详细货物分类数据", expanded=False):
        cargo_data = []
        for village, details in cargo_details.items():
            cargo_data.append({
                "村庄名称": village,
                "轻包裹(件)": details.get('light_packages', 0),
                "重包裹(件)": details.get('heavy_packages', 0),
                "易碎物品(件)": details.get('fragile_items', 0),
                "总计(件)": sum(details.values())
            })
        
        df_cargo = pd.DataFrame(cargo_data)
        df_cargo = df_cargo.sort_values("总计(件)", ascending=False)
        st.dataframe(df_cargo, width="stretch")
        
        # 货物分类分布图
        if len(cargo_data) > 0:
            fig_cargo = px.bar(
                df_cargo.head(10),
                x="村庄名称",
                y=["轻包裹(件)", "重包裹(件)", "易碎物品(件)"],
                title="Top10村庄货物分类分布",
                labels={'value': '数量(件)', 'variable': '货物类型'}
            )
            fig_cargo.update_xaxes(tickangle=45)
            st.plotly_chart(fig_cargo, width="stretch")

def display_upstream_packages_section():
    """显示上行包裹详细数据"""
    st.markdown("### 📤 详细上行包裹")

    # 仅用于界面展示的中英文映射，不改变底层数据键名
    category_labels = {
        'recyclables': '回收品',
        'agricultural_products': '农产品',
        'handmade_crafts': '手工艺品',
        'return_packages': '退货包裹'
    }
    item_labels = {
        'paper': '纸类',
        'plastic': '塑料',
        'electronics': '电子产品',
        'fruits': '水果',
        'vegetables': '蔬菜',
        'grains': '粮食',
        'textiles': '纺织品',
        'woodwork': '木工制品',
        'pottery': '陶器',
        'damaged': '损坏',
        'wrong_delivery': '错配'
    }
    
    upstream_packages = get_config('upstream_packages', {})
    if not upstream_packages:
        st.info("ℹ️ 暂无详细上行包裹数据")
        return
    
    # 计算各类总计
    totals = {
        'recyclables': {'paper': 0, 'plastic': 0, 'electronics': 0},
        'agricultural_products': {'fruits': 0, 'vegetables': 0, 'grains': 0},
        'handmade_crafts': {'textiles': 0, 'woodwork': 0, 'pottery': 0},
        'return_packages': {'damaged': 0, 'wrong_delivery': 0}
    }
    
    for village_data in upstream_packages.values():
        for category, items in village_data.items():
            if category in totals:
                for item, count in items.items():
                    if item in totals[category]:
                        totals[category][item] += count
    
    # 显示汇总数据
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**♻️ 回收品总计**")
        total_recyclables = sum(totals['recyclables'].values())
        st.metric("总回收品", f"{total_recyclables:,} 件")
        for item, count in totals['recyclables'].items():
            st.write(f"- {item_labels.get(item, item)}: {count:,} 件")
    
    with col2:
        st.markdown("**🌾 农产品总计**")
        total_agricultural = sum(totals['agricultural_products'].values())
        st.metric("总农产品", f"{total_agricultural:,} 件")
        for item, count in totals['agricultural_products'].items():
            st.write(f"- {item_labels.get(item, item)}: {count:,} 件")
    
    with col3:
        st.markdown("**🎨 手工艺品总计**")
        total_crafts = sum(totals['handmade_crafts'].values())
        st.metric("总手工艺品", f"{total_crafts:,} 件")
        for item, count in totals['handmade_crafts'].items():
            st.write(f"- {item_labels.get(item, item)}: {count:,} 件")
    
    with col4:
        st.markdown("**↩️ 退货包裹总计**")
        total_returns = sum(totals['return_packages'].values())
        st.metric("总退货包裹", f"{total_returns:,} 件")
        for item, count in totals['return_packages'].items():
            st.write(f"- {item_labels.get(item, item)}: {count:,} 件")
    
    # 详细表格
    with st.expander("📋 查看详细上行包裹数据", expanded=False):
        upstream_data = []
        for village, categories in upstream_packages.items():
            row = {"村庄名称": village}
            village_total = 0
            
            for category, items in categories.items():
                for item, count in items.items():
                    category_name = category_labels.get(category, category)
                    item_name = item_labels.get(item, item)
                    col_name = f"{category_name}_{item_name}"
                    row[col_name] = count
                    village_total += count
            
            row["总计(件)"] = village_total
            upstream_data.append(row)
        
        df_upstream = pd.DataFrame(upstream_data)
        df_upstream = df_upstream.sort_values("总计(件)", ascending=False)
        st.dataframe(df_upstream, width="stretch")

if __name__ == "__main__":
    main()
