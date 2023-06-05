import requests
import os
from PyPDF2 import PdfReader
from selenium import webdriver

def get_presconf_links(chrome_path, base_url):

    options = webdriver.ChromeOptions()
    options.add_argument("user-data-dir="+chrome_path)
    #options.add_experimental_option('prefs', {'download.default_directory': download_path})
    driver = webdriver.Chrome(executable_path="C:\\Users\\chromedriver.exe", options=options)

    driver.get(base_url)

    link_locator = (By.XPATH, '//a[contains(@href, "fomcpresconf")]')

    # Find all elements matching the locator strategy
    presconf_links = driver.find_elements(*link_locator)

    # Extract the href attribute from each link
    presconf_urls = [link.get_attribute('href') for link in presconf_links]
    
    return presconf_urls

def get_pdf_links(presconf_urls):

    pdf_links = list()
    for page in presconf_urls:

        driver.get(page)
        link_locator = (By.XPATH, '//a[contains(@href, "FOMCpresconf")]')

        # Find all elements matching the locator strategy
        fomc_links = driver.find_elements(*link_locator)
        pdf_link = [link.get_attribute('href') for link in fomc_links]

        # Extract the href attribute from each link
        pdf_links.append(pdf_link[1])

    return pdf_links

def get_pdf_to_txt(pdf_links, output_folder):

    # Create a folder to store the downloaded PDFs
    os.makedirs(output_folder, exist_ok=True)

    # Iterate over the PDF URLs
    for index, pdf_url in enumerate(pdf_links):
        # Download the PDF file
        response = requests.get(pdf_url)

        filename = pdf_url.split('/')[-1]
        filename = filename.replace('.pdf', '')

        pdf_file_path = f'{output_folder}/{filename}.pdf'
        with open(pdf_file_path, 'wb') as file:
            file.write(response.content)

        # Convert the PDF to text
        text_file_path = f'{output_folder}/{filename}.txt'
        with open(pdf_file_path, 'rb') as file:
            pdf = PdfReader(file)
            text = ''

            for page in range(len(pdf.pages)):
                text += pdf.pages[page].extract_text()

        # Save the text to a text file
        with open(text_file_path, 'w', encoding='utf-8') as file:
            file.write(text)

        print(f'Successfully downloaded and converted PDF {index+1}.')

chrome_path = r"C:/Users/Prayut Jain/AppData/Local/Google/Chrome/User Data/Default"
BASE_URL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
output_folder = './data'

presconf_urls = get_presconf_links(chrome_path=chrome_path, base_url=BASE_URL)
pdf_links = get_pdf_links(presconf_urls)
get_pdf_to_txt(pdf_links)
