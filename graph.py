import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('data/legacy/nyr20.csv')

# Split date column
df[['Month', 'Day', 'Year']] = df['Date'].str.split('/', expand=True)
df['Month'] = df['Month'].astype(int)
df['Day'] = df['Day'].astype(int)
df['Year'] = df['Year'].astype(int)

# Replace falsy values with 0's, otherwise the boolean conversion will return True for "0" and "0.0"
df.fillna(0, inplace=True)
df = df.replace('0', 0)
df = df.replace('0.0', 0)

# Create new column that sums up total resolutions met per day
resolution_bools = df.iloc[:, 1:6].astype(bool)
df['Resolutions Met'] = resolution_bools.sum(axis=1)
print(df)

# Generate heatmap
df_map = df.pivot("Month", "Day", "Resolutions Met")
nyr_map = sns.heatmap(df_map, vmin=0, vmax=5, cmap="inferno", square=True, cbar_kws={'orientation': 'horizontal'})

# Create rectangular outlines for notable days
notable_days = {
    "start_adderall": [14, 4],  # date in [day, month] format
}
for event, day in notable_days.items():
    day_coords = [x - 1 for x in day]
    rect = plt.Rectangle(day_coords, 1, 1, color="gold", linewidth=2.5, fill=False)
    nyr_map.add_patch(rect)

plt.show()
