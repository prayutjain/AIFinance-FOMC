## Script for scraping all FOMC data into 1 dataframe

from utilities_v1 import FedReserveData

chrome_path = r"C:/Users/Prayut Jain/AppData/Local/Google/Chrome/User Data/Default"

fed_data = FedReserveData(chrome_path)
df = fed_data.get_data(year_range = (1994,2023))

df.to_pickle("../data/raw_data.pkl")
# clean_df.to_pickle("../data/clean_data.pkl")
