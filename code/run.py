import os
import random
import subprocess
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from utils import getAddress, getSize

# Ensure the path to the virtual environment activation script is correct
subprocess.run(['..\\.venv\\Scripts\\activate.bat'], shell=True, check=True)


def extract_property_data(url, index, name):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    # create the folder if it doesn't exist
    os.makedirs(name, exist_ok=True)
    # Create a folder inside the previous folder for the htmls
    os.makedirs(f'{name}/htmls', exist_ok=True)
    # Save the HTML content to a file inside the folder
    with open(f'{name}/htmls/page{index}.html', 'w', encoding='utf-8') as file:
        file.write(soup.prettify())

    address, area = getAddress(soup)
    size = getSize(soup)
    return {'Adresse': address, 'Postnummer': area, 'Størrelse': size, 'URL': url}


# Create the directory if it doesn't exist
name = "leie"
os.makedirs(name, exist_ok=True)
# Read URLs from the crawl
urls_df = pd.read_csv(name + "/" + name + '_crawled.csv')
collectedData = []

# Loop through each URL and extract property data
try:
    for index, url in enumerate(urls_df['URL']):
        # wait between 100 and 2000 milliseconds
        time.sleep(random.uniform(0.1, 2))
        print(f'Reading URL at index {index}: {url}')
        try:
            data = extract_property_data(url, index, name)
            print(f'Results at index {index}: {data}')
            collectedData.append(data)
        except Exception as e:
            print(f'Error processing URL at index {index}: {url} - {e}')
finally:
    # Save the combined data to a new CSV file in the output directory
    df = pd.DataFrame(collectedData)
    df.to_csv(f'{name}/{name}_extracted.csv', index=False)
    print('CSV file has been written.')
