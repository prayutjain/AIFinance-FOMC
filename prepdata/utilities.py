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

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

nltk.download('stopwords')

class FedReserveData:
    def __init__(self, chrome_path, base_url, output_folder):
        self.chrome_path = chrome_path
        self.base_url = base_url
        self.output_folder = output_folder
        self.id_value = 0

        options = webdriver.ChromeOptions()
        options.add_argument("user-data-dir="+chrome_path)
        self.driver = webdriver.Chrome(executable_path="C:\\Users\\chromedriver.exe", options=options)
        self.df = pd.DataFrame(columns=['id', 'date', 'source', 'text', 'title', 'chairman', 'variable'])

    def append_to_df(self, id_value, date_value, source_value, text, title_value, chairman_value, variable_value):
        self.df = self.df.append({
            'id': id_value,
            'date': date_value,
            'source': source_value,
            'text': text,
            'title': title_value,
            'chairman': chairman_value,
            'variable': variable_value
        }, ignore_index=True)

    def get_id_value(self):
        self.id_value += 1
        id_str = f"FIN{str(self.id_value).zfill(7)}"
        return id_str

    def get_date_value(self, url):
        date_string = re.findall(r'\d+', url)
        date_value = datetime.strptime(date_string[0], "%Y%m%d").strftime("%m/%d/%Y")
        return date_value

    ## FOMC Press Conference data
    def get_presconf_links(self):
        self.driver.get(self.base_url)
        link_locator = (By.XPATH, '//a[contains(@href, "fomcpresconf")]')
        presconf_links = self.driver.find_elements(*link_locator)
        presconf_urls = [link.get_attribute('href') for link in presconf_links]
        # self.driver.quit()
        return presconf_urls

    def get_pdf_links(self, presconf_urls):
        pdf_links = list()
        for page in presconf_urls:
            self.driver.get(page)
            link_locator = (By.XPATH, '//a[contains(@href, "FOMCpresconf")]')
            fomc_links = self.driver.find_elements(*link_locator)
            pdf_link = [link.get_attribute('href') for link in fomc_links]
            pdf_links.append(pdf_link[0])
        # self.driver.quit()
        return pdf_links

    def get_pdf_to_txt(self, pdf_links):
        os.makedirs(self.output_folder, exist_ok=True)
        for index, pdf_url in enumerate(pdf_links):
            response = requests.get(pdf_url)
            filename = pdf_url.split('/')[-1]
            filename = filename.replace('.pdf', '')
            pdf_file_path = f'{self.output_folder}/{filename}.pdf'
            with open(pdf_file_path, 'wb') as file:
                file.write(response.content)
            text_file_path = f'{self.output_folder}/{filename}.txt'
            with open(pdf_file_path, 'rb') as file:
                pdf = PdfReader(file)
                text = ''
                for page in range(len(pdf.pages)):
                    text += pdf.pages[page].extract_text()
            with open(text_file_path, 'w', encoding='utf-8') as file:
                file.write(text)
            print(f'Successfully downloaded and converted PDF {index+1}.')

    def process_text_files(self):
        for filename in os.listdir(self.output_folder):
            if filename.endswith('.txt'):
                with open(os.path.join(self.output_folder, filename), 'r', encoding='utf-8') as file:
                    text = file.read()
                id_value = self.get_id_value()
                date_value = self.get_date_value(filename)
                self.append_to_df(id_value, date_value, 'fed_reserve', text, 'Chairman Powell\'s Press Conference', 'Jerome Powell', 'fomc_presconf')

    
    ## FOMC Minutes data
    def get_minutes_links(self):
        self.driver.get(self.base_url)
        link_locator = (By.XPATH, '//a[contains(@href, "monetarypolicy/fomcminutes")]')
        minutes_links = self.driver.find_elements(*link_locator)
        minutes_urls = [link.get_attribute('href') for link in minutes_links]
        return minutes_urls

    def get_minutes(self, url):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        text = soup.get_text()
        parts = text.split("Minutes of the Federal Open Market Committee", 1)

        if len(parts) > 1:
            text = parts[1]  # Keep the part of the text after the specified line
        else:
            text = "" 

        parts = text.split("Last Update:", 1)

        if len(parts) > 1:
            text = parts[0]  # Keep the part of the text before "Last Update:"
        else:
            text = ""

        id_value = self.get_id_value()
        date_value = self.get_date_value(url)
        self.append_to_df(id_value, date_value, 'fed_reserve', text, 'Minutes of the Federal Open Market Committee', 'Jerome Powell', 'fomc_minutes')


    ## FOMC Statements - Press release
    def get_statements_links(self):
        self.driver.get(self.base_url)
        link_locator = (By.XPATH, '//a[contains(@href, "pressreleases/monetary") and contains(@href, "a.htm")]')
        statements_links = self.driver.find_elements(*link_locator)
        statements_urls = [link.get_attribute('href') for link in statements_links]
        return statements_urls

    
    def get_statements(self, url):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        text = soup.get_text()
        parts = text.split("For release at 2:00 p.m. EST", 1)

        if len(parts) > 1:
            text = parts[1]  # Keep the part of the text after the specified line
        else:
            text = "" 

        parts = text.split("Last Update:", 1)

        if len(parts) > 1:
            text = parts[0]  # Keep the part of the text before "Last Update:"
        else:
            text = ""
        
        id_value = self.get_id_value()
        date_value = self.get_date_value(url)
        self.append_to_df(id_value, date_value, 'fed_reserve', text, 'Federal Reserve issues FOMC statement', 'Jerome Powell', 'fomc_statements')

    
    ## FOMC Implementation notes
    def get_impnote_links(self):
        self.driver.get(self.base_url)
        link_locator = (By.XPATH, '//a[contains(@href, "pressreleases/monetary") and contains(@href, "a1.htm")]')
        impnote_links = self.driver.find_elements(*link_locator)
        impnote_urls = [link.get_attribute('href') for link in impnote_links]
        return impnote_urls

    
    def get_impnotes(self, url):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        text = soup.get_text()
        parts = text.split("Decisions Regarding Monetary Policy Implementation", 1)

        if len(parts) > 1:
            text = parts[1]  # Keep the part of the text after the specified line
        else:
            text = "" 

        parts = text.split("Last Update:", 1)

        if len(parts) > 1:
            text = parts[0]  # Keep the part of the text before "Last Update:"
        else:
            text = ""
        
        id_value = self.get_id_value()
        date_value = self.get_date_value(url)
        self.append_to_df(id_value, date_value, 'fed_reserve', text, 'Decisions Regarding Monetary Policy Implementation', 'Jerome Powell', 'fomc_impnotes')


    ## Append all data and return df

    def get_clean_data(self):
        # Preprocess data using CustomizedProcessor
        print('Preprocessing the data...')
        preprocessor = CustomizedProcessor()
        self.df['clean_text'] = preprocessor.preprocessing_pipeline().fit_transform(self.df['text'])
        print('Preprocessing completed.')
        return self.df
    
    def get_data(self):

        print("Loading Press conference data...")
        presconf_urls = self.get_presconf_links()
        pdf_links = self.get_pdf_links(presconf_urls)
        self.get_pdf_to_txt(pdf_links)
        self.process_text_files()
        
        print("Loading FOMC minutes data...")
        minutes_links = self.get_minutes_links()
        for link in minutes_links:
            self.get_minutes(link)
        
        print("Loading FOMC statements data...")
        statements_links = self.get_statements_links()
        for link in statements_links:
            self.get_statements(link)

        print("Loading Implementation notes data...")
        impnote_links = self.get_impnote_links()
        for link in impnote_links:
            self.get_impnotes(link)

        print("Done.")

        ## TODO@Prayut: Mske this functionslity work
        # self.get_clean_data()

        return self.df
    
    


class Preprocessor:
    def __init__(self):
        pass

    def preprocessing_text(self, df):
        """
        Preprocess the text data by removing non-alphabetic characters, urls and mentions
        """
        # encode all text that has encoding starting with \
        df['text'] = df['text'].str.encode('ascii', 'ignore').str.decode('ascii')

        # remove all non-ascii characters
        df['text'] = df['text'].str.replace(r'[^\x00-\x7F]+', '')

        # remove all non-alphanumeric characters
        df['text'] = df['text'].str.replace(r'[^a-zA-Z0-9\s]', '')

        # remove all single characters
        # df['text'] = df['text'].str.replace(r'\b[a-zA-Z]\b', '')

        # trim all leading and trailing whitespaces
        df['text'] = df['text'].str.strip()

        # remove all whitespaces
        df['text'] = df['text'].str.replace(r'\s+', ' ')

        # to lowercase
        df['text'] = df['text'].str.lower()

        return df

    def standardize_text(self, df):
        """
        Standardize the text data by removing non-alphabetic characters, urls and mentions
        """
        df['text'] = df['text'].str.replace(r"http\S+", "")
        df['text'] = df['text'].str.replace(r"http", "")
        df['text'] = df['text'].str.replace(r"@\S+", "")
        df['text'] = df['text'].str.replace(r"[^A-Za-z0-9(),!?@\'\`\"\_\n]", " ")
        df['text'] = df['text'].str.replace(r"@", "at")
        df['text'] = df['text'].str.lower()
        return df

    def lemmatize(self, df):
        """
        Process the text data using nltk library and
        lemmatize the words to their root form
        :return:
        """
        lemmatizer = WordNetLemmatizer()
        df['text'] = df['text'].apply(lambda x: ' '.join([lemmatizer.lemmatize(word) for word in x.split()]))
        return df


    def lowercase(self, df):
        """
        Lowercase the text data
        :return:
        """
        df['text'] = df['text'].str.lower()
        return df


    def remove_stopwords(self, df):
        """
        Remove stopwords from the text data
        :return:
        """
        stop_words = set(stopwords.words('english'))
        df['text'] = df['text'].apply(lambda x: ' '.join([word for word in x.split() if word not in stop_words]))
        return df

    def remove_less_frequent_words(self, df, frequency_threshold=750, train=True):
        """
        Remove words that appear less than 5 times
        :return:
        """
        if train:
            # fit a countvectorizer to the text data
            count_vectorizer = CountVectorizer()
            corpus = df['text'].values
            frequencies = count_vectorizer.fit(corpus)
            words_to_remove = [key for key, value in frequencies.vocabulary_.items() if value < frequency_threshold]
            df['text'] = df['text'].apply(
                lambda x: ' '.join([word for word in x.split() if word not in words_to_remove]))

            print("Saving the count vectorizer")
            print("Number of words removed: ", len(words_to_remove))
            print("Sample of removed words: ", words_to_remove[:10])

            # save the words removed to a pickle file
            # with open('../data/words_removed.pickle', 'wb') as handle:
            #     pickle.dump(words_to_remove, handle, protocol=pickle.HIGHEST_PROTOCOL)

            return df

        else:
            # test data
            with open('../data/words_removed.pickle', 'rb') as handle:
                # load the words removed from the training data
                words_to_remove = pickle.load(handle)

            df['text'] = df['text'].apply(
                lambda x: ' '.join([word for word in x.split() if word not in words_to_remove]))
            return df
        
    def remove_special_characters(self, df):
        df["text"] = df["text"].apply(lambda t: re.sub(r"[^a-zA-Z0-9\s]+", "", t))
        df["text"] = df["text"].apply(lambda t: re.sub(r"[\n]+", "", re.sub(r"[^a-zA-Z0-9\s]+", " ", t)))


        return df

    def keyword_one_hot_encoding(self, df):
        """
        Modify the keyword column
        """
        # apply one-hot encoding to the keyword column
        enc = OneHotEncoder(handle_unknown='ignore')
        df['keyword'] = df['keyword'].fillna('no_keyword')
        df['keyword'] = df['keyword'].apply(lambda t: t.replace('%20', '_'))

        X = list(df['keyword'])
        X = np.array(X).reshape(-1, 1)

        enc.fit(X)
        encoded_array = enc.transform(X).toarray()

        encoded_df = pd.DataFrame(encoded_array, columns=enc.categories_[0])
        return encoded_df
    
class CustomizedProcessor(BaseEstimator, TransformerMixin, Preprocessor):
    def __init__(self):
        super().__init__()
        
    def fit(self, *_):
        return self

    def transform(self, data):
        df = self.lowercase(data)
        df = self.remove_special_characters(df)
        df = self.remove_stopwords(df)
        df = self.standardize_text(df)
        df = self.preprocessing_text(df)
        df = self.remove_less_frequent_words(df, frequency_threshold = 10)
        
        # df = Preprocessor.lemmatize(df)

        # df = df.fillna('no_value')
        
        # change np.nan to 'no_value' for text column
        df['text'] = df['text'].fillna('no_value')
        df['text'] = df['text'].apply(lambda t: t.replace('%20', '_'))

        # encoded_df = self.keyword_one_hot_encoding(df)
        # df = df.join(encoded_df)
        # print("Preprocessing completed.")
        return df
    
    def preprocessing_pipeline(self):
        """
        Preprocessing pipeline
        """
        return Pipeline(steps=[('preprocessor', self)])
    


if __name__ == '__main__':
    import pandas as pd
    import numpy as np
    import nltk
    nltk.download('wordnet')

    chrome_path = r"C:/Users/Prayut Jain/AppData/Local/Google/Chrome/User Data/Default"
    base_url = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
    output_folder = './data'

    fed_data = FedReserveData(chrome_path, base_url, output_folder)

    # Get data
    df = fed_data.get_data()

    # Get cleaned data
    clean_df = fed_data.get_clean_data(df)

    df.to_pickle("../data/raw_data.pkl")
    clean_df.to_pickle("../data/clean_data.pkl")