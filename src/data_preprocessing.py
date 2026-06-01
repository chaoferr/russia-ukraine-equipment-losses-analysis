import os
import pandas as pd
import numpy as np

# 数据文件夹路径
DATA_DIR = "data"

# 类型映射表：将 WarSpotting 的类别映射到官方的对应名称 (处理过空格和减号的形式)
TYPE_MAPPING = {
    "Tanks": "tank",
    "Airplanes": "aircraft",
    "Helicopters": "helicopter",
    "Infantry fighting vehicles": "APC",
    "Infantry mobility vehicles": "APC",
    "Self-propelled artillery": "field_artillery",
    "Towed artillery": "field_artillery",
    "Rocket and missile artillery": "MRL",
    "Anti-aircraft systems": "anti_aircraft_warfare",
    "Drones": "drone",
    "Vessels": "naval_ship"
}

def load_official_data():
    """读取官方数据并转成每日损失量 (差分)"""
    df = pd.read_csv(os.path.join(DATA_DIR, "russia_losses_equipment.csv"))
    # 日期排序保证差分正确
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    # 获取累积数据的列 (排除 date 和 day 等非计数类)
    skip_cols = ['date', 'day', 'greatest losses direction', 'military auto', 'fuel tank']
    
    # 格式化一下列名
    df.columns = [c.replace(' ', '_').replace('-', '_') for c in df.columns]
    
    cum_cols = [c for c in df.columns if c not in ['date', 'day', 'greatest_losses_direction']]
    
    # 转换为每日新增量
    df_daily = df.copy()
    df_daily[cum_cols] = df[cum_cols].diff().fillna(df[cum_cols].iloc[0])
    
    # 强制修正负值（因官方修正历史数据可能导致diff为负）
    df_daily[cum_cols] = df_daily[cum_cols].clip(lower=0)
    
    return df_daily[['date'] + cum_cols]

def load_warspotting_data():
    """读取 WarSpotting 数据并聚合到每天"""
    file_path = os.path.join(DATA_DIR, "warspotting_losses.csv")
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    
    # 映射类型
    df['mapped_type'] = df['type'].map(TYPE_MAPPING)
    df = df.dropna(subset=['mapped_type'])
    
    # 按天和类型汇总
    daily_counts = df.groupby(['date', 'mapped_type']).size().reset_index(name='count')
    
    # 行转列
    df_pivot = daily_counts.pivot(index='date', columns='mapped_type', values='count').fillna(0)
    df_pivot = df_pivot.reset_index()
    return df_pivot

def main():
    print("正在处理数据...")
    df_official = load_official_data()
    df_ws = load_warspotting_data()
    
    # 添加后缀进行区分
    df_official = df_official.set_index('date').add_suffix('_official').reset_index()
    df_ws = df_ws.set_index('date').add_suffix('_ws').reset_index()
    
    # 按日期合并，缺失用 0 填充
    df_merged = pd.merge(df_official, df_ws, on='date', how='outer').fillna(0)
    
    # 排序日期
    df_merged = df_merged.sort_values('date').reset_index(drop=True)
    
    out_path = os.path.join(DATA_DIR, "daily_losses_matched.csv")
    df_merged.to_csv(out_path, index=False)
    
    print(f"合并完成！数据已保存至 {out_path}")
    print(df_merged.head())

if __name__ == "__main__":
    main()
