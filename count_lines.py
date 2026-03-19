#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统计五龙镇配送优化系统的代码行数
"""

import os
from pathlib import Path

def count_lines():
    """统计所有Python文件的代码行数"""
    total_lines = 0
    file_info = []
    
    # 遍历所有Python文件
    for root, dirs, files in os.walk('.'):
        # 跳过缓存目录
        if '__pycache__' in root or '.git' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                        total_lines += lines
                        file_info.append((file, lines, file_path))
                except Exception as e:
                    print(f"读取文件 {file_path} 失败: {e}")
    
    # 按行数排序
    file_info.sort(key=lambda x: x[1], reverse=True)
    
    # 打印结果
    print("=" * 60)
    print("五龙镇配送优化系统 - 代码行数统计")
    print("=" * 60)
    
    print(f"\n📊 总体统计:")
    print(f"   总文件数: {len(file_info)}")
    print(f"   总代码行数: {total_lines:,}")
    
    print(f"\n📁 文件详细统计 (按行数排序):")
    print("-" * 60)
    print(f"{'文件名':<25} {'行数':<8} {'路径'}")
    print("-" * 60)
    
    for filename, lines, filepath in file_info:
        print(f"{filename:<25} {lines:<8} {filepath}")
    
    print("-" * 60)
    print(f"总计: {total_lines:,} 行代码")
    
    # 分析
    print(f"\n📈 分析结果:")
    if total_lines >= 3000:
        print(f"   ✅ 代码行数({total_lines:,})已达到版权中心3000行要求")
    else:
        print(f"   ⚠️  代码行数({total_lines:,})未达到版权中心3000行要求")
        print(f"   建议补充到至少3000行")
    
    # 计算前30页和后30页
    lines_per_page = 50
    total_pages = total_lines // lines_per_page + (1 if total_lines % lines_per_page > 0 else 0)
    
    print(f"\n📄 页面分析:")
    print(f"   总页数: {total_pages} 页")
    print(f"   前30页行数: 1-{min(30 * lines_per_page, total_lines):,}")
    print(f"   后30页行数: {max(1, (total_pages - 30) * lines_per_page + 1):,}-{total_lines:,}")
    
    return total_lines, file_info

if __name__ == '__main__':
    count_lines()


