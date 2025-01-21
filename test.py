import subprocess
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from utils import getPrice, getAddress, getSize

subprocess.run(['.venv\\Scripts\\activate.bat'], shell=True, check=True)

# Step 1: Send a GET request to the URL
url = 'https://www.finn.no/realestate/homes/ad.html?finnkode=388216797'
response = requests.get(url)
response.raise_for_status()  # Check if the request was successful

# Step 2: Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Save the HTML content to a file
with open('output.html', 'w', encoding='utf-8') as file:
    file.write(soup.prettify())

# Step 3: Extract the relevant data
properties = []
price = getPrice(soup)
address, area = getAddress(soup)
size = getSize(soup)

properties.append({'Prisantydning': price, 'Adresse': address, 'Postnummer': area, 'Størrelse': size})

# Step 4: Store the extracted data in a pandas DataFrame
df = pd.DataFrame(properties)

# Step 5: Save the DataFrame as a CSV file
df.to_csv('property_sales.csv', index=False)
