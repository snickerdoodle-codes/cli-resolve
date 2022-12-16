import pandas as pd

# INPUTS
filename = "nyr22_partial.csv"


def get_index_response(prompt, num_cols):
    while True:
        try:
            value = int(input(prompt))
            if value < 0 or value > num_cols - 1:
                raise ValueError(f"Index {value} out of range for current dataset")
            else:
                return value
        except ValueError as value_e:
            print(f"Invalid input: {value_e}")
            continue


df = pd.read_csv(f"../data/legacy/{filename}")
col_list = list(df.columns)
cols = ""
for idx, col_name in enumerate(col_list):
    cols += "{0:20}  {1}".format(col_name, idx)
    cols += "\n"
print("{0:20}  {1}".format("COLUMN", "INDEX"))
print(cols)

data_start = get_index_response("Index of first column containing resolution data: ", len(col_list))
data_end = get_index_response("Index of last column containing resolution data: ", len(col_list))

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
clean_binary_dict = {
    '0': 0,
    '0.0': 0,
    'False': 0,
    False: 0,
    'True': 1,
    True: 1,
}
df.replace(clean_binary_dict, inplace=True)

# Create new column that sums up total resolutions met per day
resolution_bools = df.iloc[:, data_start:data_end + 1].astype(bool)
df_cleaned['Resolutions Met'] = resolution_bools.sum(axis=1)

# Copy over resolution columns as well as create new boolean columns from categorical resolutions
start = data_start
while start < data_end + 1:
    end = start + 1
    col_name = df.iloc[:, start:end].columns.values[0].lower()
    df_cleaned[col_name] = df.iloc[:, start:end]
    df_cleaned[f"{col_name}_bool"] = df.iloc[:, start:end].astype(bool).astype(int)
    start += 1

# Save cleaned df as CSV
print("*** Saving cleaned csv to data/cleaned/")
df_cleaned.to_csv(f"../data/cleaned/{filename}", index=False)
