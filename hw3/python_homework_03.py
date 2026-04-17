import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


# =========================
# 任务 1：
# =========================
print("---------- 任务 1 开始 ----------")

# 读取数据
try:
    df = pd.read_csv("ICData.csv", sep='\t')
    if df.shape[1] == 1:
        raise Exception("分隔符错误")
except:
    df = pd.read_csv("ICData.csv")

print("前5行：")
print(df.head())

print("\n基本信息：")
print(df.info())

# 时间解析（字符串 → datetime）
df['交易时间'] = pd.to_datetime(df['交易时间'])

# 提取小时
df['hour'] = df['交易时间'].dt.hour

# 构造搭乘站点数（绝对值）
df['ride_stops'] = (df['下车站点'] - df['上车站点']).abs()

# 删除异常（ride_stops = 0）
before = len(df)
df = df[df['ride_stops'] != 0]
after = len(df)

print(f"删除异常记录数：{before - after}")

# 缺失值检查
print("\n缺失值情况：")
print(df.isnull().sum())

# 处理策略：直接删除
df = df.dropna()

print("---------- 任务 1 完成 ----------")


# =========================
# 任务 2：
# =========================
print("---------- 任务 2 开始 ----------")

df_up = df[df['刷卡类型'] == 0]

hours = df_up['hour'].values

early_count = np.sum(hours < 7)
night_count = np.sum(hours >= 22)
total = len(hours)

print(f"早峰前刷卡量: {early_count} ({early_count/total:.2%})")
print(f"深夜刷卡量: {night_count} ({night_count/total:.2%})")

hour_counts = df_up.groupby('hour').size().reindex(range(24), fill_value=0)

plt.figure(figsize=(10,6))

colors = []
for i in range(24):
    if i < 7:
        colors.append('orange')
    elif i >= 22:
        colors.append('red')
    else:
        colors.append('blue')

plt.bar(hour_counts.index, hour_counts.values, color=colors)

# 添加图例
from matplotlib.patches import Patch

legend_elements = [
    Patch(facecolor='orange', label='早峰前（<7）'),
    Patch(facecolor='blue', label='正常时段（7-21）'),
    Patch(facecolor='red', label='深夜（≥22）')
]

plt.legend(handles=legend_elements)

plt.xlabel("小时")
plt.ylabel("刷卡量")
plt.title("24小时刷卡量分布")
plt.xticks(range(0,24,2))
plt.grid(axis='y')

plt.savefig("hour_distribution.png", dpi=150)
plt.close()

print("---------- 任务 2 完成 ----------")

# =========================
# 任务 3：
# =========================
print("---------- 任务 3 开始 ----------")

def analyze_route_stops(df, route_col='线路号', stops_col='ride_stops'):
    """
    计算各线路乘客的平均搭乘站点数及其标准差。

    Parameters
    ----------
    df : pd.DataFrame
        预处理后的数据集
    route_col : str, default='线路号'
        线路号列名
    stops_col : str, default='ride_stops'
        搭乘站点数列名

    Returns
    -------
    pd.DataFrame
        包含列：线路号、mean_stops、std_stops，按 mean_stops 降序排列
    """
    result = df.groupby(route_col)[stops_col].agg(
        mean_stops='mean',
        std_stops='std'
    ).reset_index()
    return result.sort_values(by='mean_stops', ascending=False)


route_stats = analyze_route_stops(df)

print(route_stats.head(10))

# 可视化
top15_routes = route_stats.head(15)['线路号']

df_top15 = df[df['线路号'].isin(top15_routes)].copy()

# 转为字符串
df_top15['线路号'] = df_top15['线路号'].astype(str)

plt.figure(figsize=(10, 6))

sns.barplot(
    data=df_top15,
    y='线路号',
    x='ride_stops',
    order=top15_routes.astype(str),
    palette="Blues_d",
    errorbar='sd',
    capsize=0.3
)

plt.xlabel("平均搭乘站点数")
plt.ylabel("线路号")
plt.title("线路搭乘站点分析")

plt.xlim(left=0)

plt.savefig("route_stops.png", dpi=150)
plt.close()

print("---------- 任务 3 完成 ----------")

# =========================
# 任务 4：
# =========================
print("---------- 任务 4 开始 ----------")

# 统计每小时刷卡量
hourly = df_up.groupby('hour').size()

# 找到高峰小时
peak_hour = hourly.idxmax()
peak_total = hourly.max()

print(f"高峰小时：{peak_hour:02d}:00 ~ {peak_hour+1:02d}:00，刷卡量：{peak_total} 次")

# 筛选该小时数据
peak_df = df_up[df_up['hour'] == peak_hour].copy()

# 设置时间索引（用于时间重采样）
peak_df = peak_df.set_index('交易时间')

# ---------- 5分钟粒度 ----------
# 按5分钟窗口统计刷卡量
count_5min = peak_df.resample('5min').size()

# 找最大5分钟流量
max_5 = count_5min.max()
max_5_time = count_5min.idxmax()

# PHF5公式
phf5 = peak_total / (12 * max_5)

# ---------- 15分钟粒度 ----------
count_15min = peak_df.resample('15min').size()

max_15 = count_15min.max()
max_15_time = count_15min.idxmax()

phf15 = peak_total / (4 * max_15)

print(f"最大5分钟刷卡量（{max_5_time.time()}）：{max_5}")
print(f"PHF5 = {peak_total} / (12 × {max_5}) = {phf5:.4f}")

print(f"最大15分钟刷卡量（{max_15_time.time()}）：{max_15}")
print(f"PHF15 = {peak_total} / (4 × {max_15}) = {phf15:.4f}")

print("---------- 任务 4 完成 ----------")


# =========================
# 任务 5：
# =========================
print("---------- 任务 5 开始 ----------")

folder = "线路驾驶员信息"
os.makedirs(folder, exist_ok=True)

df_range = df[(df['线路号'] >= 1101) & (df['线路号'] <= 1120)]

paths = []

for route in range(1101, 1121):
    sub = df_range[df_range['线路号'] == route]

    pairs = sub[['车辆编号', '驾驶员编号']].drop_duplicates()

    path = os.path.join(folder, f"{route}.txt")
    paths.append(path)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"线路号: {route}\n")
        f.write("车辆编号\t驾驶员编号\n")
        for _, row in pairs.iterrows():
            f.write(f"{row['车辆编号']}\t{row['驾驶员编号']}\n")

print("生成文件路径：")
for p in paths:
    print(p)

print("---------- 任务 5 完成 ----------")


# =========================
# 任务 6：
# =========================
print("---------- 任务 6 开始 ----------")

def top10(col):
    return df[col].value_counts().head(10)

top_driver = top10('驾驶员编号')
top_route = top10('线路号')
top_stop = top10('上车站点')
top_vehicle = top10('车辆编号')

print("\nTop10司机：\n", top_driver)
print("\nTop10线路：\n", top_route)
print("\nTop10站点：\n", top_stop)
print("\nTop10车辆：\n", top_vehicle)

heatmap_data = pd.DataFrame([
    top_driver.values,
    top_route.values,
    top_stop.values,
    top_vehicle.values
])

plt.figure(figsize=(10,4))

sns.heatmap(
    heatmap_data,
    annot=True,
    cmap="YlOrRd",
    xticklabels=[f"Top{i}" for i in range(1,11)],
    yticklabels=["司机","线路","站点","车辆"]
)

plt.title("服务绩效热力图\n（基于乘客人次）")

plt.savefig("performance_heatmap.png", dpi=150, bbox_inches='tight')
plt.close()

print("\n结论：从热力图可以观察到，不同维度存在明显的客流集中现象，部分线路和司机服务人次显著高于其他，说明城市公交运行具有明显的主干线路依赖结构，同时部分站点可能为核心换乘枢纽，承担更高客流压力。")

print("---------- 任务 6 完成 ----------")