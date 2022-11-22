import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def convert_legacy_resolutions(filename):
    df = pd.read_csv(f"data/legacy/{filename}")
    pd.set_option('display.max_columns', None)
    print(f"Preview of uploaded dataset:\n{df.head()}\n")

    data_start = int(input("index of first column containing resolution data: "))
    data_end = int(input("index of last column containing resolution data: "))

    # Split a column called "Date" or "date"
    try:
        df[['Month', 'Day', 'Year']] = df['Date'].str.split('/', expand=True)
    except KeyError as e:
        print(f"No column called={e}: trying 'date' instead")
        df[['Month', 'Day', 'Year']] = df['date'].str.split('/', expand=True)
    # Convert 2-digit year to 4-digit year
    df['Year'] = ["20" + year if len(year) == 2 else year for year in df['Year']]
    df['Month'] = df['Month'].astype(int)
    df['Day'] = df['Day'].astype(int)
    df['Year'] = df['Year'].astype(int)

    # Replace falsy values with 0's, otherwise the boolean conversion will return True for "0" and "0.0"
    df.fillna(0, inplace=True)
    df = df.replace('0', 0)
    df = df.replace('0.0', 0)

    # Create new column that sums up total resolutions met per day
    resolution_bools = df.iloc[:, data_start:data_end + 1].astype(bool)
    df['Resolutions Met'] = resolution_bools.sum(axis=1)

    # Save cleaned df as CSV
    df.to_csv(f"data/converted/{filename}", index=False)


def generate_heatmap(filename, notable_month=None, notable_day=None):
    df = pd.read_csv(f"data/converted/{filename}")

    df_map = df.pivot("Month", "Day", "Resolutions Met")
    nyr_map = sns.heatmap(
        df_map,
        vmin=0,
        vmax=5,
        cmap="inferno",
        square=True,
        cbar_kws={'orientation': 'horizontal'}
    ).set(
        title=f"{df['Year'][0]}"
    )

    # TODO: use kwargs and allow for multiple notable dates
    if notable_month and notable_day:
        day_coords = [notable_day - 1, notable_month - 1]
        rect = plt.Rectangle(day_coords, 1, 1, color="gold", linewidth=2.5, fill=False)
        nyr_map.add_patch(rect)

    plt.show()


# generate_heatmap("nyr19.csv")
# generate_heatmap("nyr20.csv")
# generate_heatmap("nyr21.csv")
