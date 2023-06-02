import requests
from bs4 import BeautifulSoup
import PyPDF2

url = "https://www.federalreserve.gov/monetarypolicy/publications/mpr_default.htm"

response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')
li = soup.find_all('a')

i = 0

for link in li:
	if ('.pdf' in link.get('href', [])):
		i += 1
		print("Downloading file: ", i)
		kal = 'https://www.federalreserve.gov' + link['href']
		response = requests.get(kal)
		pdf = open("FOMC_Press "+str(i)+".pdf", 'wb')
		pdf.write(response.content)
		pdf.close()
		pdf_file = open("FOMC_Press "+str(i)+".pdf", 'rb')
		pdf_reader = PyPDF2.PdfReader(pdf_file)
		txt_file = open("FOMC_Press "+str(i)+".txt", 'w',encoding="utf-8")
		for page_num in range(len(pdf_reader.pages)):
			page = pdf_reader.pages[page_num]
			txt_file.write(page.extract_text())
		pdf_file.close()
		txt_file.close()
		print("File ", i, " downloaded")

print("All PDF files downloaded")
