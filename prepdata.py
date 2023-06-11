## Script for scraping all FOMC data into 1 dataframe

from utilities import FedReserveData

chrome_path = r"C:/Users/Prayut Jain/AppData/Local/Google/Chrome/User Data/Default"
base_url = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
output_folder = './data'

fed_data = FedReserveData(chrome_path, base_url, output_folder)

# Get data
df = fed_data.get_data()

# Get cleaned data
# TODO@Prayut: Make this part work
# clean_df = fed_data.get_clean_data(df)

df.to_pickle("../data/raw_data.pkl")
# clean_df.to_pickle("../data/clean_data.pkl")
