import math
import pandas as pd

def haversine(lat1, lon1, lat2, lon2):
    """
    使用Haversine公式计算两点之间的直线距离（单位：公里）。
    """
    R = 6371.0  # 地球平均半径，单位公里
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

if __name__ == "__main__":
    # 定义所有地点的名称及其经纬度坐标（纬度, 经度）
    locations = {
        "五龙镇": (35.7828, 113.9398),
        "丰峪村": (35.8015, 113.9395),
        "上庄村": (35.7951, 113.9582),
        "泽下村": (35.7912, 113.9786),
        "文峪村": (35.8153, 113.9841),
        "河头村": (35.8236, 113.9715),
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

    # 获取一个有序的地点名称列表，用于构建矩阵
    location_names = list(locations.keys())
    
    # 初始化一个空的距离矩阵
    distance_matrix = []

    # 遍历每一个起点
    for origin_name in location_names:
        row = []
        origin_lat, origin_lon = locations[origin_name]
        
        # 遍历每一个终点
        for dest_name in location_names:
            dest_lat, dest_lon = locations[dest_name]
            
            # 计算距离并添加到行中
            distance = haversine(origin_lat, origin_lon, dest_lat, dest_lon)
            row.append(distance)
        
        # 将完整的一行添加到距离矩阵中
        distance_matrix.append(row)

    # --- 打印结果 ---
    print("=========================================================================================================")
    print("                                各村庄及配送中心之间的直线距离矩阵 (单位：公里)                               ")
    print("=========================================================================================================")

    # 打印列标题 (为了对齐，我们截取部分名称)
    header = "             " + " ".join([f"{name[:3]:<6}" for name in location_names])
    print(header)
    print("-" * len(header))

    # 打印每一行的数据
    for i, origin_name in enumerate(location_names):
        # 打印行标题
        row_str = f"{origin_name[:5]:<12}"
        # 打印该行对应的所有距离
        for distance in distance_matrix[i]:
            row_str += f"{distance:<6.2f}"
        print(row_str)

    print("\n提示：该矩阵为对称矩阵，即从A到B的距离等于从B到A的距离。")
    print("      在建模时，您可以使用上三角或下三角部分的数据。")
    
    # --- 导出到Excel ---
    # 创建DataFrame
    df = pd.DataFrame(distance_matrix, 
                     index=location_names, 
                     columns=location_names)
    
    # 添加距离单位说明
    df.index.name = '起点'
    df.columns.name = '终点'
    
    # 导出到Excel文件
    excel_filename = "五龙镇各村距离矩阵.xlsx"
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        # 主距离矩阵表
        df.to_excel(writer, sheet_name='距离矩阵', index=True)
        
        # 创建距离统计表
        stats_data = []
        for i, origin in enumerate(location_names):
            for j, dest in enumerate(location_names):
                if i != j:  # 排除自己到自己的距离
                    stats_data.append({
                        '起点': origin,
                        '终点': dest,
                        '距离(公里)': round(distance_matrix[i][j], 2)
                    })
        
        stats_df = pd.DataFrame(stats_data)
        stats_df.to_excel(writer, sheet_name='距离明细', index=False)
        
        # 创建距离统计摘要
        summary_data = []
        for origin in location_names:
            distances = [distance_matrix[location_names.index(origin)][location_names.index(dest)] 
                        for dest in location_names if dest != origin]
            summary_data.append({
                '村庄名称': origin,
                '到其他村庄平均距离(公里)': round(sum(distances) / len(distances), 2),
                '到其他村庄最短距离(公里)': round(min(distances), 2),
                '到其他村庄最长距离(公里)': round(max(distances), 2)
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='距离统计', index=False)
    
    print(f"\n结果已成功导出到Excel文件：{excel_filename}")
    print("文件包含三个工作表：")
    print("1. 距离矩阵 - 完整的距离矩阵")
    print("2. 距离明细 - 所有村庄间的距离列表")
    print("3. 距离统计 - 每个村庄的距离统计信息")