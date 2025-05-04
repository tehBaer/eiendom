import os
import subprocess
import pandas as pd
import requests
from bs4 import BeautifulSoup
from extraction.utils import OLD_getBuyPrice, getAddress, getSize

# Ensure the path to the virtual environment activation script is correct
subprocess.run(['.venv\\Scripts\\activate.bat'], shell=True, check=True)

def extract_property_data(url, file_name):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    # Save the HTML content to a file
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(soup.prettify())

    price = OLD_getBuyPrice(soup)
    address, area = getAddress(soup)
    size = getSize(soup)
    return {'Prisantydning': price, 'Adresse': address, 'Postnummer': area, 'Størrelse': size}

# Create the output directory if it doesn't exist
os.makedirs('output', exist_ok=True)

# Read URLs from `property_urls.csv`
urls_df = pd.read_csv('crawling/property_urls.csv').head(3)
property_data = []

# Loop through each URL and extract property data
# for i, url in enumerate(urls_df['URL']):
#     print(f'Reading URL: {url}')
#     file_name = f'output/property_{i + 1}.html'
#     data = extract_property_data(url, file_name)
#     print(f'Results: {data}')
#     property_data.append(data)
data = extract_property_data('https://www.finn.no/realestate/homes/ad.html?finnkode=365034375', 'output/property_FAULTY.html')
print(f'Results: {data}')
property_data.append(data)

# Save the combined data to a new CSV file
df = pd.DataFrame(property_data)
df.to_csv('combined_property_sales.csv', index=False)