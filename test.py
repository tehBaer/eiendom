import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import subprocess


subprocess.run(['.venv\\Scripts\\activate.bat'], shell=True, check=True)

# Step 1: Send a GET request to the URL
# url = 'https://www.finn.no/realestate/homes/search.html?radius=700&lat=59.91638034358857&lon=10.78986414267564&polylocation=&ownership_type=3'
url = 'https://www.finn.no/realestate/homes/ad.html?finnkode=388216797'
response = requests.get(url)
response.raise_for_status()  # Check if the request was successful

# Step 2: Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

with open('output.html', 'w', encoding='utf-8') as file:
    file.write(soup.prettify())





# Step 3: Extract the relevant data
# properties = []
# for listing in soup.find_all('article', class_='ads__unit'):
#     title = listing.find('a', class_='ads__unit__link').get_text(strip=True)
#     price = listing.find('div', class_='ads__unit__price').get_text(strip=True)
#     location = listing.find('div', class_='ads__unit__location').get_text(strip=True)
#     properties.append({'Title': title, 'Price': price, 'Location': location})

# Step 4: Store the extracted data in a pandas DataFrame
# df = pd.DataFrame(properties)

# Step 5: Save the DataFrame as a CSV file
# df.to_csv('property_sales.csv', index=False)

price_attr = {'aria-labelledby': 'sales-costs'}

pricing_section = soup.find('section', price_attr)

prisantydning_match = re.search(r'kr\s*([\d\s]+),-', pricing_section.get_text())
if prisantydning_match:
    prisantydning = prisantydning_match.group(1).replace('\xa0', ' ')
    print(f'Prisantydning: {prisantydning}')
else:
    print('Prisantydning not found')