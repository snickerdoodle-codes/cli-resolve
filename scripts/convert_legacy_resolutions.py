import pandas as pd


def convert_legacy_resolutions(filename):
    df = pd.read_csv(f"../data/legacy/{filename}")
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

    # Replace falsy values with 0's, otherwise the boolean convqersion will return True for "0" and "0.0"
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
    df_cleaned.to_csv(f"../data/cleaned/{filename}", index=False)


convert_legacy_resolutions("nyr22_partial.csv")
