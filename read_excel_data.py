import pandas as pd
import numpy as np

print("正在读取Excel文件...")

# 读取物流车配送距离Excel文件
try:
    df = pd.read_excel('物流车配送距离.xlsx')
    print("物流车配送距离.xlsx 文件内容:")
    print("=" * 50)
    print("数据形状:", df.shape)
    print("列名:", df.columns.tolist())
    print("\n前5行数据:")
    print(df.head())
    
    # 保存数据到文本文件以便查看
    with open('物流车配送距离_数据.txt', 'w', encoding='utf-8') as f:
        f.write("物流车配送距离.xlsx 数据内容:\n")
        f.write("=" * 50 + "\n")
        f.write(f"数据形状: {df.shape}\n")
        f.write(f"列名: {df.columns.tolist()}\n\n")
        f.write("完整数据:\n")
        f.write(df.to_string())
    
    print("数据已保存到 '物流车配送距离_数据.txt'")
    
except Exception as e:
    print(f"读取物流车配送距离.xlsx时出错: {e}")

print("\n" + "="*50 + "\n")

# 读取五龙镇各村距离矩阵
try:
    df2 = pd.read_excel('五龙镇各村距离矩阵.xlsx')
    print("五龙镇各村距离矩阵.xlsx 文件内容:")
    print("=" * 50)
    print("数据形状:", df2.shape)
    print("列名:", df2.columns.tolist())
    print("\n前5行数据:")
    print(df2.head())
    
    # 保存数据到文本文件以便查看
    with open('五龙镇各村距离矩阵_数据.txt', 'w', encoding='utf-8') as f:
        f.write("五龙镇各村距离矩阵.xlsx 数据内容:\n")
        f.write("=" * 50 + "\n")
        f.write(f"数据形状: {df2.shape}\n")
        f.write(f"列名: {df2.columns.tolist()}\n\n")
        f.write("完整数据:\n")
        f.write(df2.to_string())
    
    print("数据已保存到 '五龙镇各村距离矩阵_数据.txt'")
    
except Exception as e:
    print(f"读取五龙镇各村距离矩阵.xlsx时出错: {e}")
