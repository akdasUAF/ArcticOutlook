import pandas as pd

def read_excel_sheet(path, filename):
    df = pd.read_excel(path)
    df = df.fillna('')
    return convert_df_to_instructs(df)
    
def convert_df_to_instructs(df):
    instructs = []
    num = 0
    for index, row in df.iterrows():
        index = row["Instruction Type"]
        name = row["Instruction Name"]
        notes = row["Notes"]
        params = [row["Parameter"], row["Attribute"], row["Tag"], row["Value"], row["Function Name"], row["Range"]]
        instructs.append((index, params, num, name, notes))
        num += 1
    return instructs