# 五龙镇各村包裹分配计算
# 基于人口比例分配3123件包裹

# 各村人口数据（按图片中的顺序）
villages_population = {
    "石官村": 5600,
    "中石阵村": 5201,
    "阳和村": 4676,
    "碾上村": 3868,
    "泽下村": 3600,
    "七峪村": 3100,
    "渔村": 3000,
    "合脉掌村": 3000,
    "桑峪村": 2972,
    "荷花村": 2781,
    "西蒋村": 2652,
    "岭后村": 2600,
    "河头村": 2350,
    "上庄村": 2300,
    "罗圈村": 2100,
    "南沃村": 1800,
    "丰峪村": 1778,
    "岭南村": 1750,
    "马兰村": 1725,
    "城峪村": 1696,
    "牛家岗村": 1386,
    "陈家岗村": 1380,
    "薛家岗村": 1380,
    "长坡村": 1306,
    "文峪村": 1000,
    "栗家洼村": 1000
}

# 总包裹数
total_packages = 3123

# 计算总人口
total_population = sum(villages_population.values())
print(f"总人口: {total_population}人")
print(f"总包裹数: {total_packages}件")
print(f"平均每人的包裹数: {total_packages/total_population:.4f}件/人")
print()

# 按人口比例分配包裹
package_distribution = {}
for village, population in villages_population.items():
    # 按比例计算包裹数
    packages = (population / total_population) * total_packages
    # 四舍五入到整数
    packages_rounded = round(packages)
    package_distribution[village] = packages_rounded

# 显示分配结果
print("各村包裹分配结果:")
print("-" * 50)
print(f"{'村庄名称':<12} {'人口数':<8} {'分配包裹数':<10} {'比例(%)':<8}")
print("-" * 50)

total_assigned = 0
for village, population in villages_population.items():
    packages = package_distribution[village]
    percentage = (population / total_population) * 100
    print(f"{village:<12} {population:<8} {packages:<10} {percentage:.2f}%")
    total_assigned += packages

print("-" * 50)
print(f"{'总计':<12} {total_population:<8} {total_assigned:<10} 100.00%")

# 检查是否有分配误差
difference = total_packages - total_assigned
if difference != 0:
    print(f"\n注意: 由于四舍五入，总分配包裹数与目标包裹数相差 {difference} 件")
    print("建议调整:")
    
    # 找出人口最多的村庄来调整差额
    max_population_village = max(villages_population.items(), key=lambda x: x[1])[0]
    package_distribution[max_population_village] += difference
    print(f"将 {max_population_village} 的包裹数调整为 {package_distribution[max_population_village]} 件")

print("\n最终分配结果:")
for village, packages in package_distribution.items():
    print(f"{village}: {packages}件")
