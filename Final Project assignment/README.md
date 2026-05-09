# 人机协作报告（AI + Python 数据分析项目）

## 一、AI交互日志

本次项目采用人机协作方式完成出租车数据分析与建模任务。

### 1. 数据处理阶段
AI建议进行：
- trip_distance / fare_amount异常值清洗
- 时间字段转换
- 构造hour、weekday、is_peak等特征

我采纳了大部分建议，并额外加入：
- 500000行数据截断（防止内存溢出）
- 99%分位数过滤（提升稳定性）

---

### 2. 可视化阶段问题

在绘制distance_fare图时出现问题：数据集中所有点集中在0附近。

AI建议：
使用分位数过滤异常值。

我修改为：
- 统一对 distance / fare / duration 做99%截断
- 封装plot_scatter函数统一风格

---

### 3. M4 QA系统报错

报错1：
NameError: get_intent not defined

原因：函数未定义

解决：
补充 get_intent()

---

报错2：
NameError: parse_hour not defined

解决：
增加正则时间解析函数 parse_hour()

---

## 二、三阶段对比

### 1. Native版本
仅包含：
- RandomForest模型
- 无评估指标

缺点：
结构混乱，可解释性差

---

### 2. Prompt版本（AI辅助）

加入：
- train/test split
- MAE / RMSE / R2

优点：
开始具有机器学习规范结构

---

### 3. Vibe版本（最终版）

加入：
- baseline模型对比
- error analysis
- 统一评估函数

优点：
接近科研级结构，逻辑完整


## 三、反思

通过本次人机协作项目，我对AI工具的能力边界有了更清晰的认识。

AI在代码生成、结构设计和调试建议方面具有很高效率，可以快速帮助我搭建完整的数据分析流程，包括数据清洗、可视化和机器学习建模。

但AI并不是完全可靠的执行者，它仍然会出现函数缺失、逻辑不完整或上下文理解错误的问题，例如本项目中出现的get_intent和parse_hour未定义错误。

因此，最有效的方式是“人类负责结构判断，AI负责生成与优化”。人机协作可以显著提高开发效率，但最终代码质量仍依赖人的调试与整合能力。
