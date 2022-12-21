import json
import math
import os
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from .export_utils import get_years_list
from .resolution_utils import get_boolean_response
from .menu_utils import goto_menu


def print_files(list_of_files):
    files = ""
    for idx, f in enumerate(list_of_files):
        files += "{0:30}  {1}".format(f, idx)
        files += "\n"
    print("\n{0:30}  {1}".format("FILE", "INDEX"))
    print(files)


def get_index_response(prompt, num_cols):
    while True:
        try:
            command = input(prompt)
            if command == "menu":
                goto_menu()
            value = int(command)
            if value < 0 or value > num_cols - 1:
                raise ValueError(f"Index {value} out of range for current dataset")
            else:
                return value
        except ValueError as value_e:
            print(f"Invalid input: {value_e}")
            continue


def export_graph_from_file():
    path = "data/cleaned"
    dir_list = os.listdir(path)
    dir_list.sort()
    print_files(dir_list)
    index = get_index_response("Enter the index of the file from which you wish to generate graphs: ", len(dir_list))
    file = dir_list[index]
    filepath = f"data/cleaned/{file}"

    export_minimaps = get_boolean_response("Do you want minimaps for select resolutions? (Y/N): ")
    generate_heatmap(filepath)
    if export_minimaps:
        generate_minimaps(filepath)
    plt.show()


def generate_heatmap(filepath, years_list=None, notable_days=None):
    df = pd.read_csv(filepath)
    if not years_list:
        start_date_str = df["date"][0]
        end_date_str = df["date"][len(df) - 1]
        years_list = get_years_list(start_date_str, end_date_str)
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


def get_resolution_choice_set(df):
    non_options = ["date", "Month", "Day", "Year", "Resolutions Met"]
    return [x for x in df if x not in non_options]


def get_resolution_columns_and_values(df):
    choice_set = get_resolution_choice_set(df)
    options = ""
    for col in choice_set:
        values = df[col].unique()
        options += "{0:20}  {1}".format(col, values)
        options += "\n"
    return options


def get_columns(prompt, df):
    cols = input(prompt)
    if cols == "menu":
        goto_menu()
    cols = "".join(cols.split())  # remove whitespace
    all_options = get_resolution_choice_set(df)

    if cols.lower() == "all":
        return all_options
    if cols.lower() == "binary":
        return [x for x in all_options if "bool" in x]
    if cols.lower() == "nonbinary":
        return [x for x in all_options if "bool" not in x]

    col_list = cols.split(",")
    col_list = [x for x in col_list if x]  # remove empty elements
    validated_list = []
    for col in col_list:
        if col not in all_options:
            print(f"`{col}` is not a valid column -- removing from list to generate minimaps from")
        else:
            validated_list.append(col)
    return validated_list


def optimize_display_size(num_cols, num_rows, num_years):
    # Determine height and width of final figure
    months_in_year = 12
    days_in_month = 31
    h = months_in_year * num_years * num_rows
    w = days_in_month * num_cols
    # Set inches per horizontal and vertical unit
    inches_per_col = 2
    inches_per_year = 4.5
    # Set minimum display sizes for long and short sides of canvas
    min_long = 12
    min_short = 8
    if w > h:  # wide display
        graph_width = min_long if inches_per_col * num_cols < min_long else inches_per_col * num_cols
        graph_height = min_short if inches_per_year * num_years < min_short else inches_per_year * num_years
    else:  # long display
        graph_width = min_short if inches_per_col * num_cols < min_short else inches_per_col * num_cols
        graph_height = min_long if inches_per_year * num_years < min_long else inches_per_year * num_years
    return graph_height, graph_width


def calculate_grid_dimensions(num_maps):
    num_cols = math.ceil(math.sqrt(num_maps))
    num_rows = num_cols
    while (num_rows * num_cols) >= num_maps:
        if ((num_rows - 1) * num_cols) >= num_maps:
            num_rows -= 1
        else:
            break
    return num_cols, num_rows


def generate_minimaps(filename, years_list=None):
    df = pd.read_csv(filename)
    if not years_list:
        start_date_str = df["date"][0]
        end_date_str = df["date"][len(df) - 1]
        years_list = get_years_list(start_date_str, end_date_str)
    num_years = len(years_list)

    options = get_resolution_columns_and_values(df)
    print(f"\nPreview of data from uploaded dataset:\n{options}")

    instructions = "Enter a comma-separated list of columns to create minimaps from (e.g. exercise,skincare).\n" \
                   "You may also enter:\n" \
                   "--'all' to use all columns, \n" \
                   "--'binary' to use all boolean columns, or\n" \
                   "--'nonbinary' to use all non-boolean columns\n"
    print(f"INSTRUCTIONS: {instructions}")
    col_list = []
    while len(col_list) == 0:
        col_list = get_columns(
            "Which resolutions do you want to create minimaps from?: ",
            df
        )

    # Calculate the smallest squarish grid that will hold all plots
    num_maps = len(col_list)
    num_cols, num_rows = calculate_grid_dimensions(num_maps)

    graph_height, graph_width = optimize_display_size(num_cols, num_rows, num_years)
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

            # Keep border around each subplot
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
            print(f"Something went wrong: {e}")

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
    if num_years == 1:
        plt.ylabel("Month")
    else:
        plt.ylabel("Year-Month")

    print("*** Saving to data/exports folder")
    plt.savefig("data/exports/temp_minimaps.pdf", dpi=300)
