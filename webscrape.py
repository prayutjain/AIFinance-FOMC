import requests
from bs4 import BeautifulSoup

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
		print("File ", i, " downloaded")

print("All PDF files downloaded")
