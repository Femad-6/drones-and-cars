# -*- coding: utf-8 -*-
"""
五龙镇配送优化系统 - 安装脚本
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README文件
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# 读取版本信息
version_info = {}
exec((this_directory / "src" / "__init__.py").read_text(), version_info)

setup(
    name="wulong_delivery_optimizer",
    version=version_info.get("__version__", "1.0.0"),
    author=version_info.get("__author__", "配送优化研究团队"),
    author_email="",
    description=version_info.get("__description__", "五龙镇配送优化系统"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    project_urls={
        "Bug Tracker": "",
        "Source Code": "",
    },

    # 包信息
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "": ["*.json", "*.txt", "*.md"],
    },

    # 依赖
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "openpyxl>=3.0.0",
        "scipy>=1.7.0",
    ],

    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "sphinx>=4.0.0",
        ],
        "all": [
            "pytest>=6.0.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "sphinx>=4.0.0",
        ]
    },

    # 分类器
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Visualization",
    ],

    # 关键词
    keywords=[
        "delivery",
        "optimization",
        "genetic-algorithm",
        "vehicle-routing",
        "drone-delivery",
        "logistics",
        "rural-ecommerce"
    ],

    # 入口点
    entry_points={
        "console_scripts": [
            "wulong-optimizer=main:main",
        ],
    },

    # 其他元数据
    zip_safe=False,
    include_package_data=True,
)
