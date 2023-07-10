import os
import re
import requests
import pandas as pd
import numpy as np
import pickle
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from PyPDF2 import PdfReader


class FedReserveData:
    def __init__(self, chrome_path):
        self.chrome_path = chrome_path
        # self.base_url = base_url
        # self.output_folder = output_folder
        self.id_value = 0
        self.year_range = (1994,2023)

        options = webdriver.ChromeOptions()
        options.add_argument("user-data-dir="+chrome_path)
        self.driver = webdriver.Chrome(executable_path="C:\\Users\\chromedriver.exe", options=options)
        self.df = pd.DataFrame(columns=['date', 'source', 'text', 'title', 'chairman', 'variable'])

    def append_to_df(self, date_value, source_value, text, title_value, variable_value):
        new_row = pd.DataFrame({
            'date': [date_value],
            'source': [source_value],
            'text': [text],
            'title': [title_value],
            'variable': [variable_value]
        })
        
        self.df = pd.concat([self.df, new_row], ignore_index=True)

    def get_id_value(self):
        self.id_value += 1
        id_str = f"FIN{str(self.id_value).zfill(7)}"
        return id_str

    def get_date_value(self, url):
        date_string = re.findall(r'\d{8}', url)
        if date_string:
            date_value = datetime.strptime(date_string[0], "%Y%m%d").strftime("%m/%d/%Y")
            return date_value
        else:
            return None
    
    def fomc_chairman(self):
        data = {
        "Start Date": ["August 10, 1914", "August 10, 1916", "May 1, 1923", "October 4, 1927", "September 16, 1930", "May 19, 1933", "November 15, 1934", "April 15, 1948", "April 2, 1951", "February 1, 1970", "March 8, 1978", "August 6, 1979", "August 11, 1987", "February 1, 2006", "February 3, 2014", "February 5, 2018"],
        "End Date": ["August 9, 1916", "August 9, 1922", "September 15, 1927", "August 31, 1930", "May 10, 1933", "August 15, 1934", "January 31, 1948", "March 31, 1951", "January 31, 1970", "January 31, 1978", "August 6, 1979", "August 11, 1987", "January 31, 2006", "January 31, 2014", "February 3, 2018", "December 31, 2030"],
        "chairman": ["Charles S. Hamlin", "W.P.G. Harding", "Daniel R. Crissinger", "Roy A. Young", "Eugene Meyer", "Eugene R. Black", "Marriner S. Eccles", "Thomas B. McCabe", "William McChesney Martin, Jr.", "Arthur F. Burns", "G. William Miller", "Paul A. Volcker", "Alan Greenspan", "Ben S. Bernanke", "Janet L. Yellen", "Jerome H. Powell"]
        }

        df = pd.DataFrame(data)
        df['Start Date'] = pd.to_datetime(df['Start Date'])
        df['End Date'] = pd.to_datetime(df['End Date'])
        

        return df
    

    ## Pull FOMC calendar and parse dates
    def date_parser(self, tags, year_range):
        # Define regular expressions for each date pattern
        pattern1 = re.compile(r"([A-Za-z/]+) (\d{1,2}-\d{1,2}) Meeting - (\d{4})")
        pattern2 = re.compile(r"([A-Za-z]+) (\d{1,2}) - ([A-Za-z]+) (\d{1,2}) Meeting - (\d{4})")
        pattern3 = re.compile(r"([A-Za-z]+) (\d{1,2}) Meeting - (\d{4})")
        dates = []

        for tag in tags:
            str_tag = str(tag)
            if pattern1.search(str_tag):
                months, days, year = pattern1.search(str_tag).groups()
                # Split months and days
                if '/' in months:
                    _, month = months.split('/')
                else:
                    month = months
                _, day = days.split('-')
            elif pattern2.search(str_tag):
                month1, day1, month2, day2, year = pattern2.search(str_tag).groups()
                month, day = month2, day2
            elif pattern3.search(str_tag):
                month, day, year = pattern3.search(str_tag).groups()

            month_number = datetime.strptime(month, "%B" if len(month) > 3 else "%b").month

            if int(year) in range(year_range[0], year_range[1] + 1):
                date = datetime(year=int(year), month=month_number, day=int(day))
                dates.append(date)

            ## Remove dups
            dates = list(dict.fromkeys(dates).keys())

            ## Manual date manipulation 
            ####### DO NOT CHANGE #########
            target_date1 = datetime.strptime("01-31-1996", "%m-%d-%Y")
            replacement_date1 = datetime.strptime("01-30-1996", "%m-%d-%Y")

            target_date2 = datetime.strptime("07-03-1996", "%m-%d-%Y")
            replacement_date2 = datetime.strptime("07-02-1996", "%m-%d-%Y")
            for i, date in enumerate(dates):
                if date == target_date1:
                    dates[i] = replacement_date1
                elif date == target_date2:
                    dates[i] = replacement_date2
            ####### DO NOT CHANGE #########
                
        return dates
    
    def get_2017onw_links(self, base_url):
        self.driver.get(base_url)
        link_locator = (By.XPATH, '//a[contains(@href, "pressreleases/monetary") and contains(@href, "a.htm")]')
        statements_links = self.driver.find_elements(*link_locator)
        statements_urls = [link.get_attribute('href') for link in statements_links]
        return statements_urls
    
    def get_fomc_dates(self, year_range):

        years = range(year_range[0], 2018)
        year_links = ["https://www.federalreserve.gov/monetarypolicy/fomchistorical" + str(year) + ".htm" for year in years]

        h5_tags = []
        for link in year_links:
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')
            tags = soup.find_all('h5')

            h5_tags.append(tags)

        dates = [item for sublist in h5_tags for item in sublist]
        list_dates = self.date_parser(dates, year_range)

        base_url = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
        post2017_links = self.get_2017onw_links(base_url)

        for url in post2017_links:
            list_dates.append(datetime.strptime(self.get_date_value(url),"%m/%d/%Y"))

        list_dates = list(dict.fromkeys(list_dates).keys())
        list_dates.sort()

        ## Manually limiting the dates
        start_date = datetime(year_range[0], 1, 1)
        end_date = datetime(year_range[1], 12, 31)

        filtered_dates = [date for date in list_dates if start_date <= date <= end_date]
        
        return filtered_dates
    
    ## Download minutes data
    def get_minutes(self, date):
        """
        date: datetime object
        """

        #### IMPORTANT: DO NOT CHANGE ####

        if date > datetime.strptime("10-30-2007", "%m-%d-%Y"):
            minute_link = "https://www.federalreserve.gov/monetarypolicy/fomcminutes"
            url = minute_link + date.strftime("%Y%m%d") + ".htm"

        elif date > datetime.strptime("01-01-1996", "%m-%d-%Y"):
            minute_link = "https://www.federalreserve.gov/fomc/minutes/"
            url = minute_link + date.strftime("%Y%m%d") + ".htm"

        elif date > datetime.strptime("01-01-1993", "%m-%d-%Y"):
            minute_link = "https://www.federalreserve.gov/fomc/MINUTES/"
            url = minute_link + date.strftime("%Y") + "/" + date.strftime("%Y%m%d") + "min.htm"
            
        else:
            ## Before 1993 it was available in a pdf format, need to define a separate function to pull that
            return None
        
        ##################################

        page = requests.get(url)
        if page.status_code != 200:
            print(f"Failed to access: {url}")
            return None
        
        soup = BeautifulSoup(page.content, 'html.parser')
        text = soup.get_text()
        
        if date > datetime.strptime("01-01-2012", "%m-%d-%Y"):
            text = text[8180:]
        elif date > datetime.strptime("10-30-2007", "%m-%d-%Y"):
            text = text[630:]

        # id_value = self.get_id_value()
        date_value = self.get_date_value(url)
        self.append_to_df(date_value, 'fed_reserve', text, 'Minutes of the Federal Open Market Committee', 'fomc_minutes')


    
    ## Download statements
    def get_statements(self, date):
        """
        date: datetime object
        """

        #### IMPORTANT: DO NOT CHANGE ####

        if date >= datetime.strptime("01-01-2006", "%m-%d-%Y"):
            stat_link = "https://www.federalreserve.gov/newsevents/pressreleases/monetary"
            url = stat_link + date.strftime("%Y%m%d") + "a.htm"

        elif date >= datetime.strptime("01-01-2003", "%m-%d-%Y"):
            stat_link = "https://www.federalreserve.gov/boarddocs/press/monetary/"
            url = stat_link + date.strftime("%Y") + "/" + date.strftime("%Y%m%d") + "/default.htm"

        elif date >= datetime.strptime("01-01-1997", "%m-%d-%Y"):
            stat_link = "https://www.federalreserve.gov/boarddocs/press/monetary/"
            url = stat_link + date.strftime("%Y") + "/" + date.strftime("%Y%m%d") + "/"

        elif date >= datetime.strptime("01-01-1996", "%m-%d-%Y"):
            stat_link = "https://www.federalreserve.gov/fomc/"
            url = stat_link + date.strftime("%Y%m%d") + "DEFAULT.htm"

        elif date >= datetime.strptime("01-01-1995", "%m-%d-%Y"):
            stat_link = "https://www.federalreserve.gov/fomc/"
            url = stat_link + date.strftime("%Y%m%d") + "default.htm"
            
        else:
            ## Not available before 1995
            return None
        ##################################

        page = requests.get(url)
        if page.status_code != 200:
            print(f"Failed to access: {url}")
            return None
        
        soup = BeautifulSoup(page.content, 'html.parser')
        text = soup.get_text()
        
        if date > datetime.strptime("01-01-2006", "%m-%d-%Y"):
            text = text[7730:]

        # id_value = self.get_id_value()
        date_value = self.get_date_value(url)
        self.append_to_df(date_value, 'fed_reserve', text, 'Federal Reserve issues FOMC statement', 'fomc_statements')

    ## Rest are in pdf format
    def get_pdf_to_txt(self, pdf_url, output_folder):
        os.makedirs(output_folder, exist_ok=True)
        # for index, pdf_url in enumerate(pdf_links):
        response = requests.get(pdf_url)

        if response.status_code != 200:  
            print("Requested url not available: ", pdf_url)
            return 
    
        filename = pdf_url.split('/')[-1]
        filename = filename.replace('.pdf', '')
        pdf_file_path = f'{output_folder}/{filename}.pdf'
        with open(pdf_file_path, 'wb') as file:
            file.write(response.content)
        text_file_path = f'{output_folder}/{filename}.txt'
        with open(pdf_file_path, 'rb') as file:
            pdf = PdfReader(file)
            text = ''
            for page in range(len(pdf.pages)):
                text += pdf.pages[page].extract_text()
        with open(text_file_path, 'w', encoding='utf-8') as file:
            file.write(text)
        print(f'Successfully downloaded and converted PDF.')

    def process_text_files(self, title, item, output_folder):
        for filename in os.listdir(output_folder):
            if filename.endswith('.txt'):
                with open(os.path.join(output_folder, filename), 'r', encoding='utf-8') as file:
                    text = file.read()
                # id_value = self.get_id_value()
                date_value = self.get_date_value(filename)
                self.append_to_df(date_value, 'fed_reserve', text, title, item)

    
    def get_data(self, year_range):

        fomc_dates = self.get_fomc_dates(year_range)
        print("Starts from ", fomc_dates[0].strftime("%Y-%m-%d"), " to ", fomc_dates[-1].strftime("%Y-%m-%d"), " totalling ", len(fomc_dates), " meetings")

        for date in fomc_dates:
            
            print("FOMC meeting: ", datetime.strftime(date, "%Y/%m/%d"))
            self.get_minutes(date)
            self.get_statements(date)

            ## Pull Transcripts
            trans_url = "https://www.federalreserve.gov/monetarypolicy/files/FOMC" + date.strftime("%Y%m%d") + "meeting.pdf"
            self.get_pdf_to_txt(trans_url,"./data/transcript")

            ## Pull Press conference - only 2011 onwards
            if date >= datetime.strptime("01-01-2011", "%m-%d-%Y"):

                pconf_url = "https://www.federalreserve.gov/mediacenter/files/FOMCpresconf" + date.strftime("%Y%m%d") + ".pdf"
                self.get_pdf_to_txt(pconf_url,"./data/presconf")

            ## Pull Agenda?
            ag_url = "https://www.federalreserve.gov/monetarypolicy/files/FOMC" + date.strftime("%Y%m%d") + "Agenda.pdf"
            self.get_pdf_to_txt(ag_url,"./data/agenda")

        print("All files downloaded.")
        self.process_text_files("Meeting of the FOMC - Transcript", "fomc_transcript", "./data/transcript")
        self.process_text_files("Press Conference Transcript", "fomc_presconf", "./data/presconf")
        self.process_text_files("Agenda of FOMC Meeting", "fomc_agenda", "./data/agenda")

        print("Attaching chaiman name...")
        ## Attach chairman name
        chair_df = self.fomc_chairman()
        
        # Ensure the dates are in the correct format
        self.df['date'] = pd.to_datetime(self.df['date'])
        chair_df['Start Date'] = pd.to_datetime(chair_df['Start Date'])
        chair_df['End Date'] = pd.to_datetime(chair_df['End Date'])

        self.df = self.df.sort_values('date')
        chair_df = chair_df.sort_values('Start Date')

        # Set the index to be an interval for the term of each chair
        chair_df.set_index(pd.IntervalIndex.from_arrays(chair_df['Start Date'], chair_df['End Date'], closed='both'), inplace=True)

        # Now you can lookup the chair for each date with the .loc indexer
        self.df['chairman'] = self.df['date'].apply(lambda x: chair_df.loc[x]['chairman'] if any(chair_df.loc[x]) else None)
        print("Done.")

        return self.df