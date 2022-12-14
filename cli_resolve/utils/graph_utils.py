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
                'pad': 0.08
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


def generate_minimaps(filename, years_list):
    df = pd.read_csv(filename)
    num_years = len(years_list)

    pd.set_option('display.max_columns', None)
    # TODO: Make it easier to see distinct values in preview
    print(f"Preview of uploaded dataset:\n{df.head()}\n")

    # TODO: Add "all" option (or "all bools")
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

    # Calculate display size
    inches_per_col = 3
    inches_per_row = 5
    # single res x single year (wide map)
    graph_width = 12
    graph_height = 5
    # muliple res x multiple years
    if num_maps > 1 and num_years >= 1:
        graph_width = inches_per_col * num_cols
        graph_height = inches_per_row * num_rows
    # single res x multiple years (long map)
    elif num_maps == 1 and num_years > 1:
        graph_height = inches_per_row * num_years
    plt.rcParams["figure.figsize"] = (graph_width, graph_height)

    fig, axes = plt.subplots(
        nrows=num_rows,
        ncols=num_cols,
        sharex=True,
        sharey=True
    )
    i = 0
    j = 0
    for res in col_list:
        try:
            if num_years == 1:
                df_map = df.pivot("Month", "Day", res)
            else:
                df_map = df.pivot(index=["Year", "Month"], columns="Day", values=res)

            # Use qualitative colormap to display non-binary resolutions and show cbar
            if "bool" not in res:
                # Get categories from categorical data
                categories = pd.unique(df_map.values.ravel())
                categories = [x for x in categories if not pd.isnull(x)]
                cat_to_int = {j: i for i, j in enumerate(categories)}
                n = len(cat_to_int)
                df_map = df_map.replace(cat_to_int)
                # Generate colors based on a cmap, with 0's as white
                if n > 2:
                    palette = sns.color_palette("turbo", n - 1)
                    colors = ["white"] + palette
                else:  # if there's only 2 categories (including 0) it might as well be binary
                    colors = ["white", "black"]
                display_cbar = True
            else:
                colors = "binary"
                display_cbar = False

            nyr_map = sns.heatmap(
                df_map,
                cmap=colors,
                square=True,
                cbar=display_cbar,
                cbar_kws={
                    "orientation": "horizontal",
                    "fraction": 0.03,
                    "pad": 0.08
                },
                ax=axes[i][j] if num_maps > 2 else axes[j] if num_maps == 2 else axes
            )

            # Modify cbar for categorical resolutions
            if display_cbar:
                colorbar = nyr_map.collections[0].colorbar
                r = colorbar.vmax - colorbar.vmin
                colorbar.set_ticks([colorbar.vmin + r / n * (0.5 + i) for i in range(n)])
                colorbar.set_ticklabels(list(cat_to_int.keys()))

            # Turn off labels on minimaps
            nyr_map.set(
                title=f"{res}",
                xlabel="",
                ylabel="",
            )
            # Set tick bins and rotation
            xbins = 7  # weekly ticks
            if num_years == 1:
                ybins = 2  # semiannual ticks
            else:
                ybins = num_years
            nyr_map.locator_params(axis='x', nbins=xbins)
            nyr_map.tick_params(axis='x', labelrotation=0)
            nyr_map.locator_params(axis='y', nbins=ybins)
            nyr_map.tick_params(axis='y', labelrotation=90)

            sns.despine(
                top=False,
                right=False,
                left=False,
                bottom=False,
            )

            # Fill grid across columns first, then move down to next row
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

    fig.subplots_adjust(hspace=0.2, wspace=0)

    # Add background axis with hidden frame for common xlabel and ylabel
    fig.add_subplot(111, frameon=False)
    plt.tick_params(labelcolor='none', which='both', top=False, bottom=False, left=False, right=False)
    plt.xlabel("Day")
    plt.ylabel("Year-Month")

    print("*** Saving to data/exports folder")
    plt.savefig("data/exports/temp_minimaps.pdf", dpi=300)
