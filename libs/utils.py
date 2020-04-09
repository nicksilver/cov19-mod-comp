import pandas as pd

def calc_stats(df):
    df_dop = df.idxmax().to_frame()
    df_max = df.max().to_frame()
    df_stats = df_dop.merge(df_max, right_index=True, left_index=True)
    df_stats.columns = ['Day of Peak', 'Peak Value']
    return df_stats