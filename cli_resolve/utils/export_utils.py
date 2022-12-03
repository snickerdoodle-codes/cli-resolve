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


def generate_heatmap(filepath, notable_days={}):
    df = pd.read_csv(filepath)

    try:
        # Date range within single year
        df_map = df.pivot("Month", "Day", "Resolutions Met")
        nyr_map = sns.heatmap(
            df_map,
            cmap="inferno",
            square=True,
            vmin=0,
            vmax=5,
            cbar_kws={'orientation': 'horizontal'},
            xticklabels=True,
            yticklabels=True,
        )
        nyr_map.set(
            title=f"{df['date'][0]} - {df['date'][len(df['date']) - 1]}"
        )
        plt.xticks(rotation=0)
    except ValueError:
        # Date range spanning multiple years
        df_map = df.pivot(columns=["Year", "Month"], index="Day", values="Resolutions Met")
        nyr_map = sns.heatmap(
            df_map,
            cmap="inferno",
            square=True,
            cbar_kws={'orientation': 'vertical'},
            xticklabels=True,
            yticklabels=True,
        )
        nyr_map.set(
            title=f"{df['date'][0]} - {df['date'][len(df['date']) - 1]}"
        )
        start_year = df["Year"][0]
        end_year = df["Year"][len(df["Year"]) - 1]
        start_month = 1
        end_month = 12
        year_month_labs = []
        for year in range(start_year, end_year + 1):
            for month in range(start_month, end_month + 1):
                if month == 1:
                    year_month_labs.append(f"{month}\n{year}")
                else:
                    year_month_labs.append(month)
        nyr_map.set_yticklabels(nyr_map.get_yticklabels(), rotation=0)
        nyr_map.set_xticklabels(year_month_labs, fontdict={'horizontalalignment': 'left'}, rotation=0)

    notable_days = {
        "1/27/2022": "DCA <-> DFW",
        "1/28/2022": "",
        "1/29/2022": "",
        "1/30/2022": "",
        "1/31/2022": "",
        "2/1/2022": "",
        "2/2/2022": "",
        "2/3/2022": "",
        "2/4/2022": "",
        "2/5/2022": "",
        "2/6/2022": "",
        "2/13/2022": "DCA <-> DFW",
        "2/14/2022": "",
        "2/15/2022": "",
        "2/16/2022": "",
        "2/17/2022": "",
        "2/18/2022": "",
        "2/19/2022": "",
        "2/20/2022": "",
        "2/21/2022": "",
        "2/22/2022": "",
        "2/23/2022": "",
        "2/24/2022": "",
        "2/25/2022": "",
        "2/26/2022": "",
        "2/27/2022": "",
        "2/28/2022": "",
        "3/1/2022": "",
        "3/2/2022": "",
        "3/3/2022": "",
        "3/4/2022": "",
        "3/5/2022": "",
        "3/6/2022": "",
        "3/13/2022": "Chicago Trip",
        "3/14/2022": "",
        "3/15/2022": "",
        "3/16/2022": "",
        "3/17/2022": "",
        "3/18/2022": "",
        "3/19/2022": "",
        "3/20/2022": "",
        "3/26/2022": "DCA <-> DFW",
        "3/27/2022": "",
        "3/28/2022": "",
        "3/29/2022": "",
        "6/4/2022": "Midwest Roadtrip",
        "6/5/2022": "",
        "6/6/2022": "",
        "6/7/2022": "",
        "6/8/2022": "",
        "6/9/2022": "",
        "6/10/2022": "",
        "6/11/2022": "",
        "6/12/2022": "",
        "10/11/2022": "Acadia Trip",
        "10/12/2022": "",
        "10/13/2022": "",
        "10/14/2022": "",
        "10/15/2022": "",
        "10/16/2022": "",
    }
    # TODO: currently only works for within-year maps
    if notable_days:
        for date, descript in notable_days.items():
            date_list = date.split("/")
            month = int(date_list[0])
            day = int(date_list[1])
            date_coords = (day - 1, month - 1)
            rect = plt.Rectangle(date_coords, width=1, height=1, color="white", linewidth=0, fill=False, hatch='..',
                                 alpha=0.6)
            nyr_map.add_patch(rect)
            nyr_map.text(day - 0.5,
                         month - 0.5,
                         descript,
                         horizontalalignment='left',
                         verticalalignment='center',
                         size='small',
                         color='white',
                         # backgroundcolor='white',
                         bbox=dict(boxstyle='round', fc='black'))

    plt.show()


def generate_minimap(filename):
    df = pd.read_csv(filename)
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
            try:
                df_map = df.pivot("Month", "Day", res)
            except ValueError:
                df_map = df.pivot(columns=["Year", "Month"], index="Day", values=res)
            nyr_map = sns.heatmap(
                df_map,
                vmin=0,
                vmax=1,
                cmap="binary",
                square=True,
                cbar=False,
                ax=axes[i][j] if num_maps > 2 else axes[j]
            )
            nyr_map.set(
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
