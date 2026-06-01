# russia-ukraine-equipment-losses-analysis

## 项目简介
本项目基于大作业要求，通过数理统计方法比较并对齐俄乌冲突中“官方时序战报”与“开源影像验证（WarSpotting）”两类数据集的装备损失率差异。核心解决原始观测中的记录偏误与置信区间估计问题。

## 目录结构
- `data/` : 存放官方记录、检验记录以及交叉结果数据集 (`stratified_estimation_results.csv`)
- `src/data_preprocessing.py` : 数据清洗与匹配脚本（负责种类对齐及日度差分）
- `src/step1_mle_and_ci.py` : 点估计与基础泊松置信区间（Wald / Score / Exact）
- `src/step2_bootstrap.py` : 基于 Block Bootstrap BCa 的偏误校正计算代码
- `src/step3_poisson_test.py` : 两独立 Poisson 条件检验计算模块
- `src/step4_stratified_analysis.py` : 按“装备/时间段”双向分层的顶层汇总执行脚本
- `log.txt` : 团队进展与数据表单的简明摘要
- `要求.txt` : 大作业任务指标

## 环境配置
```bash
pip install -r requirements.txt
```

## 运行方式
1. 数据清洗合并：
```bash
python src/data_preprocessing.py
```
2. 运行分层估计与检验，生成统计分析表单：
```bash
python src/step4_stratified_analysis.py
```
