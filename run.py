import os
import random
import subprocess
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from extraction.utils import getPrice, getAddress, getSize

# Ensure the path to the virtual environment activation script is correct
subprocess.run(['.venv\\Scripts\\activate.bat'], shell=True, check=True)

def extract_property_data(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    price = getPrice(soup)
    address, area = getAddress(soup)
    size = getSize(soup)
    return {'Totalpris': price, 'Adresse': address, 'Postnummer': area, 'Størrelse': size, 'URL': url}

# Create the output directory if it doesn't exist
os.makedirs('output', exist_ok=True)

# Read URLs from `property_urls.csv`
urls_df = pd.read_csv('crawling/property_urls.csv')
property_data = []

# Loop through each URL and extract property data
try:
    for index, url in enumerate(urls_df['URL']):
        # wait between 100 and 2000 milliseconds
        time.sleep(random.uniform(0.1, 2))
        print(f'Reading URL at index {index}: {url}')
        try:
            data = extract_property_data(url)
            print(f'Results at index {index}: {data}')
            property_data.append(data)
        except Exception as e:
            print(f'Error processing URL at index {index}: {url} - {e}')
finally:
    # Save the combined data to a new CSV file in the output directory
    df = pd.DataFrame(property_data)
    df.to_csv('output/combined_property_sales.csv', index=False)
    print('CSV file has been written.')