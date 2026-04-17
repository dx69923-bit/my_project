# 张涵茗-24301064-第三次人工智能编程作业

## 1. 任务拆解与 AI 协作策略

本次作业采用分模块逐步实现的方式，而不是一次性生成完整代码。具体拆解如下：

1. 任务1：数据读取与清洗（pandas）
2. 任务2：时间分布分析（numpy + matplotlib）
3. 任务3：线路统计函数封装（pandas + seaborn）
4. 任务4：PHF 高峰小时分析（numpy + pandas）
5. 任务5：文件导出（pandas）
6. 任务6：热力图分析（seaborn）

每一步完成后，我均对 AI 输出进行人工检查，确保符合课程要求的函数签名、库使用规范和可视化标准。


## 2. 核心 Prompt 迭代记录

初代 Prompt：  
> “一次性生成完整公交数据分析代码”

AI 生成的问题：  
- 未严格使用 numpy 完成条件统计（混用 pandas 原生方法）  
- 使用 seaborn 替代 matplotlib 绘制任务2柱状图，违反要求  
- PHF 公式实现错误（直接平均流量除以最大5分钟流量，未乘以12）  
- 函数签名不规范（参数名与给定模板不一致）  
- resample 使用了 `'T'` 而非 `'min'`

优化后的 Prompt：  
> 请严格按以下规则生成代码：  
> 1. 按任务逐步完成（任务1→任务2→任务3→任务4→任务5→任务6），不要一次性生成完整代码  
> 2. 严格使用指定库：numpy 必须用于条件统计；pandas 数据处理；matplotlib 任务2柱状图；seaborn 任务3和任务6可视化  
> 3. 不得修改任何函数签名、参数名或返回格式  
> 4. 每个任务必须单独给出代码，并保证可运行  
> 5. 时间处理必须使用 pandas datetime  
> 6. resample 时间粒度必须使用 `'min'`，不能使用 `'T'`  
> 7. 图表必须包含中文标题、中文坐标轴、图例（如适用）  
> 8. 所有可视化必须保存为图片文件（dpi=150）  
> 9. 代码必须符合课程评分规范，而不是追求简化


## 3. Debug 记录

报错现象：  
执行 `df.resample('5T').size()` 时，pandas 抛出 `ValueError: <class 'pandas.core.indexes.datetimes.DatetimeIndex'> is not supported with period='5T'`。

解决过程：  
查阅 pandas 文档发现，`'T'` 是旧版别名，在新版中已弃用或导致歧义。将 `'5T'` 和 `'15T'` 全部替换为 `'5min'` 和 `'15min'`，同时将 PHF 分析中的 `resample('5min')` 保持一致。修改后代码正常运行。


## 4. 人工代码审查（逐行中文注释）

以下为任务4 PHF 高峰小时系数计算的核心代码，已添加逐行中文注释：

```python
# 假设 df_up 已按上车站点筛选，且包含 'hour' 列和 '交易时间' 列
# 计算每个小时的上车总人数
hourly = df_up.groupby('hour').size()   # 按小时分组，统计每小时的记录数（上车人数）

# 找到上车人数最多的小时（高峰小时）
peak_hour = hourly.idxmax()             # idxmax() 返回最大值的索引（即小时数）

# 从原始数据中筛选出高峰小时的所有记录
peak_df = df_up[df_up['hour'] == peak_hour].copy()

# 将交易时间设为时间索引，便于重采样
peak_df = peak_df.set_index('交易时间')

# 按5分钟间隔统计该小时内的上车人数（.size() 统计每段内的记录数）
count_5min = peak_df.resample('5min').size()

# 找出这12个5分钟段中的最大值（最大5分钟流量）
max_5 = count_5min.max()

# 计算该小时的总上车人数
peak_total = hourly.loc[peak_hour]

# 计算高峰小时系数 PHF = 小时总流量 / (12 × 最大5分钟流量)
phf5 = peak_total / (12 * max_5)

# 输出结果
print(f"高峰小时: {peak_hour}:00 - {peak_hour+1}:00")
print(f"高峰小时总上车人数: {peak_total}")
print(f"最大5分钟上车人数: {max_5}")
print(f"PHF (5分钟间隔): {phf5:.3f}")
