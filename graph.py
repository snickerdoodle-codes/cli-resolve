import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

DAYS = 365
ROWS = 20
COLS = 20

curr_row = 1
curr_col = 1
row_nums = []
col_nums = []
for day in range(1, DAYS + 1):
    if day % ROWS == 0:
        row_nums.append(curr_row)
        curr_row += 1
        col_nums.append(curr_col)
        curr_col = 1  # reset col num
    else:
        row_nums.append(curr_row)
        col_nums.append(curr_col)
        curr_col += 1

# print(f"rows: {row_nums} ***** {len(row_nums)}")
# print(f"cols: {col_nums} ***** {len(col_nums)}")

# Data cleaning
df = pd.read_csv('data/nyr_2022_sample.csv')
df.fillna(0, inplace=True)
df = df.replace('0', 0)
df = df.replace('0.0', 0)

df['Row Num'] = row_nums
df['Col Num'] = col_nums
df['Resolutions Met'] = sum(
    [
        df['Exercise'].astype(bool),
        df['Floss'].astype(bool),
        df['Writing'].astype(bool),
        df['Coding'].astype(bool),
        df['Skincare'].astype(bool)
    ]
)
# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
# print(df)

# df_melted = pd.melt(df, id_vars='Row Num', value_vars=['Exercise', 'Floss', 'Writing', 'Coding', 'Skincare'],
#                     var_name='Resolution', value_name='Value')
#
# print(df_melted)
# df_map = df_melted.pivot("Row Num", "Resolution", "Value")
df_map = df.pivot("Row Num", "Col Num", "Resolutions Met")

# glue = sns.load_dataset("glue").pivot("Model", "Task", "Score")
nyr_map = sns.heatmap(df_map, vmin=0, vmax=5, cmap="inferno", xticklabels=False, yticklabels=False)

# outline day I started Adderall
rect = plt.Rectangle([3, 5], 1, 1, color="gold",
                     linewidth=2.5, fill=False)
nyr_map.add_patch(rect)
nyr_map.set(xlabel=None, ylabel=None)
plt.show()
