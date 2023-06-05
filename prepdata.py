import os
import pandas as pd
from datetime import datetime
import re

# Define the path to the folder
folder_path = './data'

# Create an empty dataframe with the desired schema
df = pd.DataFrame(columns=['ID', 'DATE', 'SOURCE', 'TEXT', 'TITLE', 'CHAIRMAN', 'VARIABLE'])

# Initialize id_value
id_value = 0

# Loop through all .txt files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.txt'):
        # Open the file
        with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as file:
            text = file.read()

        # Increment id_value
        id_value += 1
        id_str = f"FIN{str(id_value).zfill(7)}"

        # Extract the date from the filename
        date_string = re.findall(r'\d+', filename)  # Assumes the format is FOMCpresconfYYYYMMDD
        date_value = datetime.strptime(date_string[0], "%Y%m%d").strftime("%m/%d/%Y")

        # Here, you will need to derive the other fields (SOURCE, TITLE, CHAIRMAN VARIABLE)
        # from either the filename or the text contents.
        # I will assume placeholder values for now.
        source_value = "fed_reserve"
        title_value = "Chairman Powell's Press Conference"
        chairman_value = "Jerome Powell"
        variable_value = "fomc_transcript"
        
        # Append the data to the dataframe
        df = df.append({
            'ID': id_str,
            'DATE': date_value,
            'SOURCE': source_value,
            'TEXT': text,
            'TITLE': title_value,
            'CHAIRMAN': chairman_value,
            'VARIABLE': variable_value
        }, ignore_index=True)

# Save the dataframe to a pickle file
df.to_pickle("./data/final_data.pkl")