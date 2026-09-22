# setup vars
import pandas as pd, numpy as np, sys, os
from pathlib import Path

script_dir = Path(__file__).resolve().parent
os.chdir(script_dir)

file_name = input("File path: ")
sheet_name = input("Identify data sheet name: ").strip() or 0
n_rows_skip = None
columns_used = None
metadata_col_count = 11  # number of leading id columns

def load_data(target_file, columns_used=None, sheet_name=None, n_rows_skip=None):
    # header=None keeps every column position-addressable, so pandas never
    # gets to silently mangle duplicate labels (two "Flag" columns, two "PH"
    # columns) before we've had a say in how to handle them ourselves
    df = pd.read_excel(io=target_file,
                        sheet_name=sheet_name,
                        skiprows=n_rows_skip,
                        usecols=columns_used,
                        header=None)
    return df

raw = load_data(target_file=file_name, sheet_name=sheet_name)

        # split off the metadata rows instead of concatenating them into headers
param_names   = raw.iloc[0].to_list()   # parameter/column name
sampling_type = raw.iloc[1].to_list()   # Grouped / Field / Lab
unit_list     = raw.iloc[2].to_list()   # unit

df = raw.iloc[3:].reset_index(drop=True)
df.columns = range(df.shape[1])         # plain integer positions - nothing to collide

        # verify column alternation - is it flag, param OR param, flag?
id_pos    = list(range(metadata_col_count))
flag_pos  = list(range(metadata_col_count, df.shape[1], 2))
param_pos = list(range(metadata_col_count + 1, df.shape[1], 2))
assert len(flag_pos) == len(param_pos)

        # melt separately, keyed by position instead of by name
df_flags = pd.melt(df, id_vars=id_pos, value_vars=flag_pos,
                    var_name="_flag_col", value_name="Flag")
df_melt  = pd.melt(df, id_vars=id_pos, value_vars=param_pos,
                    var_name="_param_col", value_name="Measurement Value")

        # melt visits param_pos in the order given, len(df) rows per column,
        # so repeating each metadata list in that same order lines it up
        # exactly - no merge/lookup, and no header text to build or parse apart
n = len(df)
df_melt["Flag"]          = df_flags["Flag"]
df_melt["Parameter"]     = np.repeat([param_names[c]   for c in param_pos], n)
df_melt["Sampling Type"] = np.repeat([sampling_type[c] for c in param_pos], n)
df_melt["Unit"]          = np.repeat([unit_list[c]     for c in param_pos], n)
df_melt = df_melt.drop(columns="_param_col")

        # restore the real id column names (row 0 already holds them)
df_melt = df_melt.rename(columns=dict(zip(id_pos, param_names[:metadata_col_count])))

df_melt.to_csv(f"{file_name[:-4]}_output.csv", index=False)