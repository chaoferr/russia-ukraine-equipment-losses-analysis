warspotting_losses.csv 
离散数据，被照片或视频独立证实、带有唯一编号的武器损失
局限性：观测偏差

russia_losses_equipment.csv（装备损失主表）
宏观、连续的“时间序列”数据。各大类装备的累计损失总数。

russia_losses_equipment_correction.csv（官方回溯修正表）
统计误差调整记录。

russia_losses_personnel.csv（人员伤亡时序表）
士兵伤亡累计数字。

github仓库：https://github.com/chaoferr/russia-ukraine-equipment-losses-analysis

src/data_preprocessing.py
数据清洗与序列对齐：读取官方战报与 WarSpotting 开源数据，完成武器类型映射对齐，转每日新增。
【输出】合并后的对齐日数据表：`data/daily_losses_matched.csv`

src/step1_mle_and_ci.py
单点估计(MLE)：进行最基础的估计模型；计算 Wald、Score、Exact 三种不同假定下的泊松区间。
【输出】提供函数接口、打印输出各武器类型总天数和损失总量与泊松区间信息。

src/step2_bootstrap.py
Block Bootstrap (BCa)：偏误校正模块，使用滑动窗口减弱序列自相关性和减小方差。
【输出】提供函数接口、对样本数据重采样并计算用于修正置信区间的界限信息。

src/step3_poisson_test.py
两独立 Poisson 条件检验：判定对标中差异 P-value 的严格数学流程。
【输出】提供函数接口、打印各个武器在检验下的p-value结果判断是否具有显著性差异。

src/step4_stratified_analysis.py
分层估计（核心输出）：引入 1-3 步底层算法；按“不同装备类型 x 不同战役阶段(包含整体/2022/2023/2024-2026)”深度下钻分层测量。
【输出】在经过分层处理并计算MLE、置信区间以验证假设结果集已生成至核心结果文件：`data/stratified_estimation_results.csv`。

src/step5_visualization.py
可视化模块：生成满足学术论文要求的点估计条形图（含误差棒）、截面演化对比以及时间序列平滑折线图，以直观呈现验证偏误的严重性。
【输出】将在 `figures/` 目录下生成以下图片：
- `fig1_mle_comparison_log.png`：对数坐标下展示所有武器整体宏观阶段下官方与WarSpotting的损失率点估计 (MLE) 与95% BCa置信区间的对标图。
- `fig2_stratified_tank.png`：坦克 (Tank) 分阶段下钻的损失率随时间段推移演化的柱状分布对比图。
- `fig2_stratified_APC.png`：装甲运兵车 (APC) 分阶段损失率演化对比图。
- `fig3_timeseries_tank.png`：坦克 (Tank) 整个战事周期下每日损失散点及 14 天平滑均线的动态对比折线图。
- `fig3_timeseries_APC.png`：装甲运兵车 (APC) 周期下散点及 14 天平滑均线的动态对比折线图。

analysis_report.md
总结性统计学报告：包含了背景、模型阐释、数字偏误（Tank/Drone差异讨论）和对于战役分层验证的深度归纳（如不同阶段直升机战线损失验证等）。
