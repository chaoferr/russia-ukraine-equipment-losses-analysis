import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ast

# -----------------
# 绘图风格设置（论文要求）
# -----------------
def set_paper_style():
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman"],
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "legend.fontsize": 11,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight"
    })

def parse_ci(ci_str):
    """把 CSV 里的字符串 CI 转为 tuple，兼容 np.float64 格式"""
    try:
        if isinstance(ci_str, str):
            # 去除 numpy 的壳子
            clean_str = ci_str.replace("np.float64(", "").replace(")", "")
            return ast.literal_eval(clean_str)
        return ci_str
    except:
        return (0, 0)

def plot_mle_comparison(df_results, output_dir):
    """绘制整体阶段各装备类型的 MLE 及 BCa CI 对比图"""
    # 取全阶段数据
    df_tot = df_results[df_results['Time_Period'] == '1_Total_Conflict'].copy()
    
    if len(df_tot) == 0:
        return
        
    labels = df_tot['Equipment'].str.replace('_', ' ').str.title()
    mle_off = df_tot['mle_official'].values
    mle_ws = df_tot['mle_warspotting'].values
    
    # 提取 CI 用于绘制 Error bars (yerr需要提供 lower bound error 和 upper bound error)
    # yerr 形状: (2, N)
    ci_off = np.array([parse_ci(x) for x in df_tot['bootstrap_bca_official']])
    err_off = np.vstack([mle_off - ci_off[:, 0], ci_off[:, 1] - mle_off])
    
    ci_ws = np.array([parse_ci(x) for x in df_tot['bootstrap_bca_warspotting']])
    err_ws = np.vstack([mle_ws - ci_ws[:, 0], ci_ws[:, 1] - mle_ws])

    x = np.arange(len(labels))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 使用对数刻度因为 drone 和 artillery 的数值大得夸张
    ax.bar(x - width/2, mle_off, width, yerr=err_off, label='Official Claims', 
           color='indianred', capsize=5, alpha=0.9, edgecolor='black')
    ax.bar(x + width/2, mle_ws, width, yerr=err_ws, label='WarSpotting (Verified)', 
           color='steelblue', capsize=5, alpha=0.9, edgecolor='black')
    
    ax.set_ylabel('Loss Rate (units/day) - Log Scale')
    ax.set_title('Estimated Equipment Loss Rates (MLE with BCa 95% CI)')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha='right')
    ax.set_yscale('log')
    ax.legend(loc='upper right')
    
    # 添加网格
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    plt.savefig(os.path.join(output_dir, 'fig1_mle_comparison_log.png'))
    plt.close()

def plot_stratified_evolution(df_results, output_dir, eq_type='tank'):
    """绘制特定装备在不同时间段的损失率差异演化"""
    df_eq = df_results[(df_results['Equipment'] == eq_type) & (df_results['Time_Period'] != '1_Total_Conflict')].copy()
    
    if len(df_eq) == 0:
        return
        
    # 清洗 x 轴 label，使得其美观
    time_labels = [p.replace('_', ' ')[2:] for p in df_eq['Time_Period']]
    mle_off = df_eq['mle_official'].values
    mle_ws = df_eq['mle_warspotting'].values
    
    x = np.arange(len(time_labels))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    ax.bar(x - width/2, mle_off, width, label='Official Claims', color='indianred', alpha=0.85, edgecolor='black')
    ax.bar(x + width/2, mle_ws, width, label='WarSpotting (Verified)', color='steelblue', alpha=0.85, edgecolor='black')
    
    ax.set_ylabel('Loss Rate (units/day)')
    ax.set_title(f'Stratified Loss Rate Evolution: {eq_type.title()}')
    ax.set_xticks(x)
    ax.set_xticklabels(time_labels)
    ax.legend()
    
    plt.savefig(os.path.join(output_dir, f'fig2_stratified_{eq_type}.png'))
    plt.close()

def plot_time_series_smoothing(data_path, output_dir, eq_type='tank'):
    """绘制日记录的时间序列平滑曲线(7天均线)对比"""
    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    col_off = f'{eq_type}_official'
    col_ws = f'{eq_type}_ws'
    
    if col_off not in df.columns or col_ws not in df.columns:
        return
        
    df['off_smooth'] = df[col_off].rolling(window=14, center=True).mean()
    df['ws_smooth'] = df[col_ws].rolling(window=14, center=True).mean()
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # 画原始散点 (浅色)
    ax.scatter(df['date'], df[col_off], color='indianred', alpha=0.1, s=10)
    ax.scatter(df['date'], df[col_ws], color='steelblue', alpha=0.1, s=10)
    
    # 画平滑线
    ax.plot(df['date'], df['off_smooth'], label='Official (14-day MA)', color='darkred', linewidth=2)
    ax.plot(df['date'], df['ws_smooth'], label='WarSpotting (14-day MA)', color='midnightblue', linewidth=2)
    
    ax.set_ylabel('Daily Losses')
    ax.set_xlabel('Date')
    ax.set_title(f'Temporal Dynamics of {eq_type.title()} Losses')
    ax.legend()
    
    # 标签旋转
    plt.xticks(rotation=30)
    
    plt.savefig(os.path.join(output_dir, f'fig3_timeseries_{eq_type}.png'))
    plt.close()

def main():
    set_paper_style()
    base_dir = os.path.dirname(os.path.dirname(__file__))
    out_dir = os.path.join(base_dir, 'figures')
    
    res_path = os.path.join(base_dir, "data", "stratified_estimation_results.csv")
    ts_path = os.path.join(base_dir, "data", "daily_losses_matched.csv")
    
    if os.path.exists(res_path):
        df_res = pd.read_csv(res_path)
        plot_mle_comparison(df_res, out_dir)
        plot_stratified_evolution(df_res, out_dir, 'tank')
        plot_stratified_evolution(df_res, out_dir, 'APC')
        plot_stratified_evolution(df_res, out_dir, 'helicopter')
        print("Bar plots finished.")
        
    if os.path.exists(ts_path):
        plot_time_series_smoothing(ts_path, out_dir, 'tank')
        plot_time_series_smoothing(ts_path, out_dir, 'APC')
        print("Time series plots finished.")

    print(f"所有论文可视化图片已成功保存至：{out_dir}")

if __name__ == "__main__":
    main()
