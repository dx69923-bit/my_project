import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np

# ======================
# M1 数据加载
# ======================
def load_data():
    print("Loading data...")

    df = pd.read_parquet(
        r"D:\Cource\专选\人工智能编程语言\Homework\期末大作业\yellow_tripdata_2023-01.parquet"
    )

    return df.head(500000)


# ======================
# M1 数据清洗 + 特征工程
# ======================
def clean_data(df):

    print(df[['trip_distance', 'fare_amount']].describe())
    print("Cleaning data...")

    # 时间
    df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
    df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])

    df['hour'] = df['tpep_pickup_datetime'].dt.hour
    df['weekday'] = df['tpep_pickup_datetime'].dt.weekday

    df['is_peak'] = df['hour'].isin([7, 8, 9, 17, 18, 19])
    df['is_weekend'] = df['weekday'].isin([5, 6])

    # 行程时间
    df['trip_duration'] = (
        df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']
    ).dt.total_seconds() / 60

    # 每英里费用
    df['fare_per_mile'] = df['fare_amount'] / df['trip_distance']

    # ======================
    # ⭐ 99%统一过滤（核心）
    # ======================
    q = 0.99
    df = df[
        (df['trip_distance'] < df['trip_distance'].quantile(q)) &
        (df['fare_amount'] < df['fare_amount'].quantile(q)) &
        (df['trip_duration'] < df['trip_duration'].quantile(q))
    ]

    return df


# ======================
# M2 统一绘图函数
# ======================
def plot_scatter(x, y, xlabel, ylabel, title, filename):
    plt.figure(figsize=(8, 6))

    plt.scatter(x, y, alpha=0.05, s=5)
    plt.grid(True, alpha=0.2, color='gray')
    plt.xlim(left=0)
    plt.ylim(bottom=0)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title, fontweight='bold')

    plt.grid(alpha=0.3)

    plt.savefig(f"outputs/{filename}", dpi=300, bbox_inches='tight')
    plt.close()


def plot_bar(x, y, xlabel, ylabel, title, filename):
    plt.figure(figsize=(8, 6))

    plt.bar(x, y)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title, fontsize=14, fontweight='bold')

    plt.xticks(rotation=30)

    plt.grid(alpha=0.3)

    plt.savefig(f"outputs/{filename}", dpi=300, bbox_inches='tight')
    plt.close()


def plot_line(x, y, xlabel, ylabel, title, filename):
    plt.figure(figsize=(8, 6))

    plt.plot(x, y, marker='o')

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title, fontsize=14, fontweight='bold')

    plt.grid(alpha=0.3)

    plt.savefig(f"outputs/{filename}", dpi=300, bbox_inches='tight')
    plt.close()


# ======================
# M2 分析
# ======================
def analyze(df):

    print("Analyzing...")

    os.makedirs("outputs", exist_ok=True)

    plt.style.use('ggplot')
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['figure.figsize'] = (8, 6)

    # ======================
    # 1. 小时趋势
    # ======================
    hourly = df.groupby('hour').size()

    plot_line(
        hourly.index,
        hourly.values,
        "Hour",
        "Orders",
        "Hourly Demand",
        "hourly.png"
    )

    # ======================
    # 2. 热门区域
    # ======================
    top10 = df['PULocationID'].value_counts().head(10)

    plot_bar(
        top10.index.astype(str),
        top10.values,
        "Location",
        "Orders",
        "Top 10 Pickup Areas",
        "top10_areas.png"
    )

    # ======================
    # 3. 距离 vs 费用（99%过滤版）
    # ======================
    plot_scatter(
        df['trip_distance'],
        df['fare_amount'],
        "Distance (mile)",
        "Fare ($)",
        "Distance vs Fare",
        "distance_fare.png"
    )

    # ======================
    # 4. 工作日 vs 周末
    # ======================
    week = df.groupby('is_weekend').size()

    plot_bar(
        ["Weekday", "Weekend"],
        week.values,
        "Day Type",
        "Orders",
        "Week Pattern",
        "weekday_vs_weekend.png"
    )

    # ======================
    # 5. 高峰 vs 非高峰
    # ======================
    peak = df.groupby('is_peak')['fare_amount'].mean()

    plot_bar(
        ["Non-Peak", "Peak"],
        peak.values,
        "Period",
        "Avg Fare",
        "Peak Fare Comparison",
        "peak_fare.png"
    )

    # ======================
    # 6. 行程时间 vs 费用（修复！）
    # ======================
    plot_scatter(
        df['trip_duration'],
        df['fare_amount'],
        "Duration (min)",
        "Fare ($)",
        "Duration vs Fare",
        "duration_vs_fare.png"
    )


# ======================
# M3 模型
# ======================

from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

# ======================
# 1. 特征工程
# ======================
def build_features(df):

    demand = df.groupby(
        ['PULocationID', 'hour', 'weekday', 'is_peak']
    ).size().reset_index(name='demand')

    return demand


# ======================
# 2. 评估函数
# ======================
def evaluate(name, y_true, y_pred):

    print(f"\n=== {name} ===")
    print("MAE:", mean_absolute_error(y_true, y_pred))
    print("RMSE:", np.sqrt(mean_squared_error(y_true, y_pred)))
    print("R2:", r2_score(y_true, y_pred))


# ======================
# 3. 主训练流程
# ======================
def train_model(df):

    print("Training model...")

    # ===== 数据构造 =====
    demand = build_features(df)

    X = demand[['PULocationID', 'hour', 'weekday', 'is_peak']]
    y = demand['demand']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # ======================
    # 4. baseline模型
    # ======================
    baseline = DummyRegressor(strategy="mean")
    baseline.fit(X_train, y_train)
    base_pred = baseline.predict(X_test)

    # ======================
    # 5. RF模型
    # ======================
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=15,
        random_state=42
    )

    model.fit(X_train, y_train)
    pred = model.predict(X_test)

    # ======================
    # 6. 对比评估
    # ======================
    evaluate("Baseline", y_test, base_pred)
    evaluate("RandomForest", y_test, pred)

    # ======================
    # 7. 误差分析
    # ======================
    error = abs(y_test - pred)

    print("\nError Analysis:")
    print("Mean Error:", error.mean())
    print("Max Error:", error.max())

    return model

# ======================
# M4 QA
# ======================
def parse_hour(q):
    import re
    match = re.search(r"(\d{1,2})", q)
    if match:
        h = int(match.group(1))
        return min(max(h, 0), 23)
    return 12

def get_intent(q):

    q = q.lower()

    keywords = {
        "top_area": ["热门", "区域", "哪里"],
        "prediction": ["预测", "需求", "多少"],
        "peak": ["高峰", "拥堵", "忙"]
    }

    for intent, words in keywords.items():
        if any(w in q for w in words):
            return intent

    return "unknown"

def qa_system(df, model):

    print("\nmart Taxi QA System Started")
    print("可输入：热门区域 / 预测 + 时间 / 高峰\n")

    while True:
        q = input("请输入问题(q退出): ")

        if q == "q":
            print("系统已退出")
            break

        intent = get_intent(q)

        # ======================
        # 1. 热门区域（优化输出）
        # ======================
        if intent == "top_area":

            top = df['PULocationID'].value_counts().head(5)

            print("\n最热门5个上车区域：")
            for i, (loc, cnt) in enumerate(top.items(), 1):
                print(f"{i}. 区域 {loc} - {cnt} 单")

        # ======================
        # 2. 需求预测（增强解释）
        # ======================
        elif intent == "prediction":

            hour = parse_hour(q)

            loc = 1
            weekday = 2
            is_peak = 1 if hour in [7,8,9,17,18,19] else 0

            X = [[loc, hour, weekday, is_peak]]

            pred = model.predict(X)[0]

            print(f"\n预测结果：")
            print(f"- 时间：{hour} 点")
            print(f"- 预测需求量：{pred:.2f}")

            if pred > df['demand'].mean() if 'demand' in df.columns else 50:
                print("⚠当前时段需求较高，建议增加运力")
            else:
                print("✔ 当前时段需求正常")

        # ======================
        # 3. 高峰解释（增强版）
        # ======================
        elif intent == "peak":

            print("\n高峰时段分析：")
            print("- 上午高峰：7-9点")
            print("- 晚高峰：17-19点")
            print("- 原因：通勤需求集中")

        # ======================
        # 4. fallback
        # ======================
        else:
            print("\n❓无法识别问题")
            print("可尝试：")
            print("- 热门区域")
            print("- 预测18点需求")
            print("- 高峰时间")

def main():
    df = load_data()
    df = clean_data(df)
    analyze(df)
    model = train_model(df)
    qa_system(df, model)


if __name__ == "__main__":
    main()