from datetime import datetime, timedelta
import csv
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import math


def get_res_fieldnames(res_dict, start_date_str, end_date):
    res_fields = []
    for res_id, entry in res_dict.items():
        log_data = entry["data"]
        has_data = check_data_against_range(log_data, start_date_str, end_date)
        if has_data:
            res_fields.append(res_id)
    return res_fields


def check_data_against_range(data, start_date_str, end_date):
    curr_date = datetime.strptime(start_date_str, "%m/%d/%Y")
    while curr_date <= end_date:
        curr_date_str = datetime.strftime(curr_date, "%-m/%-d/%Y")
        if curr_date_str in data:
            # We're happy as long as there's a single date with data
            return True
        curr_date += timedelta(days=1)
    return False


def write_res_row(fieldnames, curr_data, fname_start, fname_end):
    date_str = curr_data["date"]
    with open(f"data/exports/res_{fname_start}_{fname_end}.csv", "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if f.tell() == 0:  # write header only if blank file
            w.writeheader()
        w.writerow(curr_data)


def convert_resolutions(filepath):
    filename = filepath.split("data/exports/")[1]
    df = pd.read_csv(filepath)
    data_start = 1
    data_end = len(df.columns) - 1

    # TODO: make this DRY (compare with convert_legacy_resolutions)
    df[['Month', 'Day', 'Year']] = df['date'].str.split('/', expand=True)

    df['Month'] = df['Month'].astype(int)
    df['Day'] = df['Day'].astype(int)
    df['Year'] = df['Year'].astype(int)

    # Replace falsy values with 0's, otherwise the boolean conversion will return True for "0" and "0.0"
    df.fillna(0, inplace=True)
    df = df.replace('0', 0)
    df = df.replace('0.0', 0)
    df = df.replace('False', 0)
    df = df.replace('True', 1)

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
    df.to_csv(f"data/cleaned/{filename}", index=False)


def convert_legacy_resolutions(filename):
    df = pd.read_csv(f"data/legacy/{filename}")
    pd.set_option('display.max_columns', None)
    print(f"Preview of uploaded dataset:\n{df.head()}\n")

    data_start = int(input("index of first column containing resolution data: "))
    data_end = int(input("index of last column containing resolution data: "))

    # Make new df for saving just the data we want
    df_cleaned = pd.DataFrame()

    # Split a column called "Date" or "date"
    try:
        df_cleaned[['Month', 'Day', 'Year']] = df['Date'].str.split('/', expand=True)
    except KeyError as e:
        print(f"No column called={e}: trying 'date' instead")
        df_cleaned[['Month', 'Day', 'Year']] = df['date'].str.split('/', expand=True)
    # Convert 2-digit year to 4-digit year
    df_cleaned['Year'] = ["20" + year if len(year) == 2 else year for year in df_cleaned['Year']]
    df_cleaned['date'] = df_cleaned[['Month', 'Day', 'Year']].apply(lambda row: '/'.join(row.values), axis=1)
    df_cleaned['Month'] = df_cleaned['Month'].astype(int)
    df_cleaned['Day'] = df_cleaned['Day'].astype(int)
    df_cleaned['Year'] = df_cleaned['Year'].astype(int)

    # Replace falsy values with 0's, otherwise the boolean conversion will return True for "0" and "0.0"
    df.fillna(0, inplace=True)
    df = df.replace('0', 0)
    df = df.replace('0.0', 0)

    # Create new column that sums up total resolutions met per day
    resolution_bools = df.iloc[:, data_start:data_end + 1].astype(bool)
    df_cleaned['Resolutions Met'] = resolution_bools.sum(axis=1)
    # Copy over resolution columns as well as create new boolean columns from categorical resolutions
    start = data_start
    while start < data_end + 1:
        end = start + 1
        col_name = df.iloc[:, start:end].columns.values[0]
        df_cleaned[col_name] = df.iloc[:, start:end]
        df_cleaned[f"{col_name}_bool"] = df.iloc[:, start:end].astype(bool).astype(int)
        start += 1

    # Save cleaned df as CSV
    print("*** Saving cleaned csv to data/cleaned/")
    df_cleaned.to_csv(f"data/cleaned/{filename}", index=False)


def generate_heatmap(filepath, notable_month=None, notable_day=None):
    df = pd.read_csv(filepath)

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
    df = pd.read_csv(f"data/cleaned/{filename}")
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
