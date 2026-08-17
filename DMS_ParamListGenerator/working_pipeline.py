# loading...
from pathlib import Path
from azure.storage.blob import BlobServiceClient
import pandas as pd, sys, os

script_dir = Path(__file__).resolve().parent
os.chdir(script_dir)

# load refs
sp_ref = pd.read_csv("mappings/REF_2026-08-04_SamplingParameters_Export.csv")
pl_ref = pd.read_csv("mappings/REF_2026-08-04_ParameterLists_Export.csv")
star_ref = pd.read_csv("mappings/REF_2026-04-14_STAR_Mapping.csv")
# file_name = input("Paste name of target file in root folder; e.g. = 'star_target.txt' : ")
file_name = sys.argv[1]
target = pd.read_csv(file_name, header=None, names=["CODE"])
# keep only integer values (filters out any header row or non-numeric text)
target = target[pd.to_numeric(target["CODE"], errors="coerce").notna()]
target["CODE"] = target["CODE"].astype(int)

# verify parameter list mappings are 1:1 - otherwise it will always take first parameter list value
pl_test = pl_ref.groupby("Parameter short name")["Name"].nunique()
dup_check = pl_test[pl_test > 1]
if len(dup_check) > 0:
    print(f"Parameter list mapping not 1:1; {len(dup_check)} parameter(s) mapped twice or more!")
    sys.exit()

# remove duplicates from parameter list reference to prevent one to many merges - necessitates dup_check = 0
pl_ref = pl_ref.drop_duplicates(subset=["Parameter short name"])

# If STAR codes, merge target star codes with their mapped VMVs
# is_star = input("Is this a list of STAR codes? 'Yes' or 'No' : ")
is_star = sys.argv[2]
if is_star.lower() == "yes":
    target_merge = target.merge(
        star_ref[['CODE', 'National_VMV_Code']], 
        on='CODE',
        how='left')

    #checking unmapped STAR codes in star_ref
    unmapped_star_codes = target_merge.loc[target_merge["National_VMV_Code"].isna(), "CODE"]
    if not unmapped_star_codes.empty:
        print(f"The following STAR codes are not mapped: {unmapped_star_codes.to_list()}")
        sys.exit()

    target_merge["National_VMV_Code"] = target_merge["National_VMV_Code"].astype(int)

elif is_star.lower() == "no":
    target_merge = target.rename(columns={"CODE": "National_VMV_Code"})

else:
    print("Please answer 'Yes' or 'No'")

# merge DMS parameter codes. 
# Use left_on and right_on instead of on and how because different column names.
target_merge = target_merge.merge(
    sp_ref[["Hydstra code", "Name", "Long name"]], 
    left_on='National_VMV_Code', 
    right_on='Hydstra code',
    how="left")
target_merge = target_merge.drop(columns=['Hydstra code'])

# check for unmapped VMV codes
check_unmapped_vmv = target_merge[target_merge.isna().any(axis=1)]
if len(check_unmapped_vmv) > 0:
    missing_vmvs = check_unmapped_vmv["National_VMV_Code"].tolist()
    print(f"The following VMV codes are not mapped to DMS parameter type codes: {missing_vmvs}")
    sys.exit()

# merge parameter list values, add column for unique parameter list values
target_merge = target_merge.merge(
    pl_ref[["Name", "Parameter short name"]],
    left_on="Name",
    right_on="Parameter short name",
    how="left",)
target_merge.drop(columns=["Parameter short name"], inplace=True)
target_merge.rename(columns={"Name_x": "Parameter type code", "Name_y": "Parameter list value"}, inplace=True)
unique_vals = sorted(target_merge["Parameter list value"].dropna().unique())
print("Unique parameter list values:")
print("\n".join(str(v) for v in unique_vals))

# final NA check
check_na = target_merge[target_merge.iloc[:, :4].isna().any(axis=1)]
if len(check_na) > 0:
    print(f'Rows with NA values found: {check_na[["National_VMV_Code", "Parameter type code", "Parameter list value"]]}')

container_name = "ethan-resources"
blob_name = f"{file_name.rsplit('.',1)[0]}_output.csv"
connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]

blob_client = BlobServiceClient.from_connection_string(conn_str=connection_string).get_blob_client(container=container_name, blob=blob_name)
blob_client.upload_blob(target_merge.to_csv(index=False), overwrite=True)
# target_merge.to_csv(f"{file_name.rsplit('.',1)[0]}_output.csv", index=False)