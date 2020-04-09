import pandas as pd
from datetime import datetime

def calc_stats(df):
    df_dop = df.idxmax().to_frame()
    df_max = df.max().to_frame()
    df_stats = df_dop.merge(df_max, right_index=True, left_index=True)
    df_stats.columns = ['Day of Peak', 'Peak Value']
    df_stats = df_stats.astype({'Peak Value': 'int'})
    df_stats['Day of Peak'] = df_stats['Day of Peak'].dt.strftime("%m/%d/%Y")
    return df_stats