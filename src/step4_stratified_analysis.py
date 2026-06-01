import os
import sys
import pandas as pd
import numpy as np

# 确保可引入同级目录下的模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from step1_mle_and_ci import poisson_mle, poisson_intervals
from step2_bootstrap import bootstrap_bca_interval
from step3_poisson_test import two_poisson_conditional_test

# 按照时间段进行分层 (战役阶段粗略划分)
TIME_PERIODS = {
    "1_Total_Conflict": ("2022-02-24", "2026-12-31"),
    "2_2022_Initial_Phases": ("2022-02-24", "2022-12-31"),
    "3_2023_Attrition_War": ("2023-01-01", "2023-12-31"),
    "4_2024_2026_Stalemate": ("2024-01-01", "2026-12-31")
}

EQUIPMENT_TYPES = ['tank', 'APC', 'aircraft', 'helicopter', 'field_artillery', 'drone']

def evaluate_strata(df, eq_type, start_date, end_date):
    """
    截取特定时间段和特定装备，分别调用 1-3 步的核心估计算法
    """
    mask = (df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))
    df_slice = df[mask]
    
    col_off = f"{eq_type}_official"
    col_ws = f"{eq_type}_ws"
    
    if len(df_slice) == 0 or col_off not in df.columns or col_ws not in df.columns:
        return None
        
    data_off = df_slice[col_off].values
    data_ws = df_slice[col_ws].values
    
    # 步骤1：MLE 和 泊松 CI
    mle_off = poisson_mle(data_off)
    mle_ws = poisson_mle(data_ws)
    
    _, _, exact_off = poisson_intervals(data_off)
    _, _, exact_ws = poisson_intervals(data_ws)
    
    # 步骤2：Block Bootstrap (使用7天周期)
    bb_ci_off = bootstrap_bca_interval(data_off, block_size=7)
    bb_ci_ws = bootstrap_bca_interval(data_ws, block_size=7)
    
    # 步骤3：假设检验
    pval = two_poisson_conditional_test(data_off, data_ws)
    
    return {
        "mle_official": round(mle_off, 2),
        "mle_warspotting": round(mle_ws, 2),
        "exact_ci_official": [round(x, 2) for x in exact_off],
        "exact_ci_warspotting": [round(x, 2) for x in exact_ws],
        "bootstrap_bca_official": [round(x, 2) for x in bb_ci_off],
        "bootstrap_bca_warspotting": [round(x, 2) for x in bb_ci_ws],
        "p_value": pval,
        "is_significant_diff": pval < 0.05
    }

def main():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "daily_losses_matched.csv")
    if not os.path.exists(data_path):
        print("缺少数据文件，请先运行数据预处理脚本。")
        return
        
    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])
    
    results = []
    
    print("="*60)
    print(" 按照时间段 & 装备类型 的分层交叉估计分析启动 ")
    print("="*60)
    
    for period_name, (start_d, end_d) in TIME_PERIODS.items():
        for eq in EQUIPMENT_TYPES:
            metrics = evaluate_strata(df, eq, start_d, end_d)
            if metrics:
                row = {
                    "Time_Period": period_name,
                    "Equipment": eq,
                    **metrics
                }
                results.append(row)
                
    result_df = pd.DataFrame(results)
    
    # 保存该分层结果
    out_path = os.path.join(os.path.dirname(__file__), "..", "data", "stratified_estimation_results.csv")
    result_df.to_csv(out_path, index=False)
    
    # 终端预览核心交叉结果
    # 剔除过于冗长的CI列以方便预览
    preview_df = result_df[['Time_Period', 'Equipment', 'mle_official', 'mle_warspotting', 'is_significant_diff']]
    print(preview_df.to_string())
    print("\n[✓] 分层估计结果已详细保存至：", os.path.relpath(out_path))

if __name__ == "__main__":
    main()
