# 五龙镇配送优化系统

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

面向县域农村场景的“车辆 + 无人机”协同配送优化项目，支持命令行批处理与 Web 交互式分析。

## 项目概览

本项目围绕五龙镇及周边村庄配送网络，提供以下能力：

- 多车辆协同路径优化（遗传算法）
- 车辆与无人机混合配送建模
- 时间约束与成本约束综合评估
- 上下行包裹与中转站数据展示
- 结果可视化与报告导出
- 支持默认数据、Excel 上传与（可选）百度地图 API 智能距离

## 核心特性

- 双入口运行方式
  - CLI：适合批量运行与复现实验
  - Web：适合参数调优、交互分析与演示
- 参数可配置
  - 车辆参数、无人机参数、算法参数
  - 自定义需求数据与配置文件覆盖
- 数据与结果完整闭环
  - 输入：Excel/JSON/默认配置
  - 输出：优化结果 JSON、图表、日志

## 快速开始

### 1. 环境要求

- Python 3.8+
- pip

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行方式

#### 方式 A：Web 界面（推荐）

```bash
python start_webapp.py
```

说明：

- 启动脚本会自动检测可用端口（默认优先 8501）
- 可直接在浏览器中完成参数配置、数据上传与结果查看

#### 方式 B：命令行优化

```bash
# 默认配置运行
python main.py

# 指定输出目录
python main.py -o output

# 指定自定义配置
python main.py -c config/example_config.json

# 设置日志级别
python main.py -v DEBUG
```

## 项目结构

```text
五龙镇配送优化系统/
├── main.py                      # CLI 入口
├── webapp.py                    # Streamlit Web 界面
├── start_webapp.py              # Web 启动脚本（自动端口）
├── start_webapp.bat             # Windows 一键启动
├── requirements.txt             # 依赖清单
├── setup.py                     # 打包脚本
├── README.md                    # 项目说明
├── WEB_GUIDE.md                 # Web 使用指南
├── config/                      # 示例配置
├── data/                        # 默认数据文件
├── output/                      # 输出目录
├── docs/                        # 文档目录
└── src/
    ├── __main__.py              # python -m src 入口
    ├── delivery_optimizer.py    # 业务流程编排
    ├── algorithms/              # 遗传算法实现
    ├── config/                  # 配置管理与默认配置
    ├── data/                    # 数据加载与预处理
    ├── utils/                   # 地理、API、模糊评估工具
    └── visualization/           # 可视化报告生成
```

## 数据与配置

### 默认数据

默认读取 `data/` 目录中的距离矩阵等数据文件，例如：

- `data/物流车配送距离.xlsx`
- `data/无人机距离矩阵.xlsx`

### 配置来源

- 默认配置：`src/config/default_config.py`
- 运行时管理：`src/config/config_manager.py`
- 可选覆盖：`config/*.json`

## 输出结果

运行完成后，通常会在 `output/` 目录生成：

- `optimization_results.json`：优化结果与关键指标
- 图表文件：路径图、成本分析图、收敛曲线等
- `system.log`：日志（按运行参数决定）

## Web 功能说明

Web 页面主要分为三部分：

- 数据与配置
  - 距离矩阵上传
  - 配置文件上传
  - 智能距离配置（可选）
  - 包裹需求编辑
- 执行优化
  - 一键执行优化
  - 当前参数摘要
- 优化结果
  - 指标卡片
  - 配送路径地图
  - 成本拆解与详细报告

## 常见问题

### 1) 提示文件不存在：`data/物流车配送距离.xlsx`

通常是启动目录不正确导致相对路径解析错误。建议始终通过以下方式启动：

```bash
python start_webapp.py
```

该脚本会在项目目录下启动 Streamlit，避免路径偏移问题。

### 2) 端口被占用

`start_webapp.py` 会自动切换到可用端口并打印访问地址。

### 3) 库接口弃用警告

项目已适配近期 Streamlit/Plotly 的主要弃用项；若仍出现，多数为环境缓存或旧进程未关闭，重启应用即可。

## 开发说明

- 主要算法：`src/algorithms/genetic_algorithm.py`
- 主流程编排：`src/delivery_optimizer.py`
- 若要扩展新策略，建议从 `src/algorithms/` 增加实现并在 `src/algorithms/__init__.py` 注册

## 许可证

本项目采用 MIT 协议，详见 `LICENSE`。

---

本项目用于教学、科研与建模分析场景，业务参数与成本模型可按实际地区数据进行二次校准。
