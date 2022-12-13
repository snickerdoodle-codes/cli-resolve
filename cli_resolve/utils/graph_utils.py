import json
import math

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


def generate_heatmap(filepath, years_list, notable_days=None):
    df = pd.read_csv(filepath)
    num_years = len(years_list)

    if num_years == 1:
        # Date range within single year
        print("*** Generating heatmap")
        plt.rcParams["figure.figsize"] = (12, 8)

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
        plt.yticks(rotation=0)
    else:
        # Date range spanning multiple years
        print("*** Generating multi-year heatmap")
        inches_per_year = 5
        graph_height = inches_per_year * num_years
        plt.rcParams["figure.figsize"] = (12, graph_height)

        df_map = df.pivot(index=["Year", "Month"], columns="Day", values="Resolutions Met")
        nyr_map = sns.heatmap(
            df_map,
            cmap="inferno",
            square=True,
            cbar_kws={
                'orientation': 'horizontal',
                'fraction': 0.04,
                'pad': 0.04
            },
            xticklabels=True,
            yticklabels=True,
        )
        nyr_map.set(
            title=f"{df['date'][0]} - {df['date'][len(df['date']) - 1]}"
        )

        # Generate special tick labels that display the year for only the first month of that year
        start_year = df["Year"][0]
        end_year = df["Year"][len(df["Year"]) - 1]
        start_month = 1
        end_month = 12
        year_month_labs = []
        for year in range(start_year, end_year + 1):
            for month in range(start_month, end_month + 1):
                if month == 1:
                    year_month_labs.append(f"{year} - {month}")
                else:
                    year_month_labs.append(month)
        nyr_map.set_xticklabels(nyr_map.get_xticklabels(), rotation=0)
        nyr_map.set_yticklabels(year_month_labs, rotation=0)

    if notable_days:
        # Load from JSON file passed into parameter
        try:
            with open(f"data/{notable_days}.json", "r") as f:
                notable_days = json.load(f)

            for date, descript in notable_days.items():
                date_list = date.split("/")
                month = int(date_list[0])
                day = int(date_list[1])
                year = int(date_list[2])
                if num_years == 1:
                    date_coords = (day - 1, month - 1)
                else:
                    months_in_year = 12
                    year_idx = years_list.index(year)
                    year_month = (year_idx * months_in_year) + month
                    date_coords = (day - 1, year_month - 1)
                rect = plt.Rectangle(date_coords,
                                     width=1,
                                     height=1,
                                     color="white",
                                     linewidth=0,
                                     fill=False,
                                     hatch='..',
                                     alpha=0.6)
                nyr_map.add_patch(rect)
                nyr_map.text(day - 0.5,
                             month - 0.5 if num_years == 1 else year_month - 0.5,
                             descript,
                             horizontalalignment='left',
                             verticalalignment='center',
                             size='small',
                             color='white',
                             bbox=dict(boxstyle='round', fc='black'))
        except Exception as e:
            print(f"No such file: {e}")

    print("*** Saving to data/exports folder")
    plt.savefig("data/exports/temp_graph.pdf", orientation='portrait')
    # plt.show()


def generate_minimaps(filename, years_list):
    df = pd.read_csv(filename)
    num_years = len(years_list)

    pd.set_option('display.max_columns', None)
    print(f"Preview of uploaded dataset:\n{df.head()}\n")

    cols = input("Enter a comma-separated list of columns to create minimaps from (e.g. exercise,skincare): ")
    cols = "".join(cols.split())  # remove whitespace
    col_list = cols.split(",")
    col_list = [x for x in col_list if x]  # remove empty elements

    # Calculate the smallest squarish grid that will hold all plots
    num_maps = len(col_list)
    num_cols = math.ceil(math.sqrt(num_maps))
    num_rows = num_cols
    while (num_rows * num_cols) >= num_maps:
        if ((num_rows - 1) * num_cols) >= num_maps:
            num_rows -= 1
        else:
            break

    inches_per_col = 4
    graph_width = inches_per_col * num_cols
    plt.rcParams["figure.figsize"] = (graph_width, 8)
    fig, axes = plt.subplots(nrows=num_rows,
                             ncols=num_cols,
                             sharex=True,
                             sharey=True)
    i = 0
    j = 0
    for res in col_list:
        try:
            try:
                df_map = df.pivot("Month", "Day", res)
            except ValueError:
                df_map = df.pivot(index=["Year", "Month"], columns="Day", values=res)

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
                title=f"{res}",
                xlabel="",
                ylabel="",
                # yticks=[],
                # xticks=[],
            )
            days_in_week = 7
            xbins = days_in_week
            ybins = num_years
            nyr_map.set_xticklabels(nyr_map.get_xticklabels(), rotation=0)
            nyr_map.locator_params(axis='x', nbins=xbins)
            nyr_map.locator_params(axis='y', nbins=ybins)

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

    fig.subplots_adjust(hspace=0, wspace=0)

    # Add background axis with hidden frame
    fig.add_subplot(111, frameon=False)
    # Hide tick and tick label of background axis
    plt.tick_params(labelcolor='none', which='both', top=False, bottom=False, left=False, right=False)
    plt.xlabel("Day")
    plt.ylabel("Year-Month")

    print("*** Saving to data/exports folder")
    plt.savefig("data/exports/temp_minimaps.pdf", dpi=300)
    # plt.show()
