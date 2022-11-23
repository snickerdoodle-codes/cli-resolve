import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import math
from time import sleep
import os


def go_home():
    """
    Takes the user back to the main menu after a showy message
    :return:
    """
    print("*** Taking you back to main menu in 3, 2, 1...")
    sleep(2)
    os.system('clear')


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
    # Create new boolean columns from categorical resolutions
    start = data_start
    while start < data_end + 1:
        end = start + 1
        col_name = df.iloc[:, start:end].columns.values[0]
        df[f"{col_name}_bool"] = df.iloc[:, start:end].astype(bool)
        df[f"{col_name}_bool"] = df[f"{col_name}_bool"].astype(int)
        start += 1

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


def generate_minimap(filename):
    df = pd.read_csv(f"data/converted/{filename}")
    pd.set_option('display.max_columns', None)
    print(f"Preview of uploaded dataset:\n{df.head()}\n")

    cols = input("Enter a comma-separated list of columns to create minimaps from (e.g. exercise,skincare): ")
    col_list = cols.split(",")

    # Calculate the smallest squarish grid that will hold all plots
    num_maps = len(col_list)
    num_cols = math.ceil(math.sqrt(num_maps))
    num_rows = num_cols
    while (num_rows * num_cols) >= num_maps:
        if ((num_rows - 1) * num_cols) >= num_maps:
            num_rows -= 1
        else:
            break

    fig, axes = plt.subplots(nrows=num_rows, ncols=num_cols)
    i = 0
    j = 0
    for res in col_list:
        try:
            df_map = df.pivot("Month", "Day", res)
            nyr_map = sns.heatmap(
                df_map,
                vmin=0,
                vmax=1,
                cmap="binary",
                square=True,
                cbar=False,
                ax=axes[i][j] if num_maps > 2 else axes[j]
            ).set(
                title=f"{res}"
            )
            sns.despine(
                top=False,
                right=False,
                left=False,
                bottom=False,
            )
            # Fill across columns first, then move down to next row
            if num_maps > 2:
                if j < num_cols - 1:
                    j += 1
                else:
                    j = 0
                    i += 1
            else:
                j += 1
        except Exception as e:
            print(f"Something went wrong: {e}\n"
                  f"Spelling matters -- perhaps `{res}` is not the name of the column?")

    # Remove empty plots from grid by continuing to read through cols, then rows, until out of rows
    if num_maps > 2:
        while i < num_rows:
            fig.delaxes(axes[i][j])
            if j < num_cols - 1:
                j += 1
            else:
                j = 0
                i += 1

    fig.subplots_adjust(hspace=0)
    plt.show()


# generate_heatmap("nyr19.csv")
# generate_heatmap("nyr20.csv")
# generate_heatmap("nyr21.csv")
# generate_minimap("nyr21.csv")
# generate_minimap("nyr_2022_sample_b.csv")
