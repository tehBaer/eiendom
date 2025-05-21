import random
import subprocess
import time
import pandas as pd
from pandas import DataFrame

from utils import *

# Ensure the path to the virtual environment activation script is correct
subprocess.run(['..\\.venv\\Scripts\\activate.bat'], shell=True, check=True)


def extract_ad_data(url, index, name, saveToHTML=False):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    # create the folder if it doesn't exist
    os.makedirs(name, exist_ok=True)
    # Create a folder inside the previous folder for the htmls
    os.makedirs(f'{name}/html_extracted', exist_ok=True)

    if (saveToHTML):
        # Save the HTML content to a file inside the folder
        with open(f'{name}/html_extracted/page{index}.html', 'w', encoding='utf-8') as file:
            file.write(soup.prettify())

    address, area = getAddress(soup)
    sizes = getAllSizes(soup)
    prices = getRentPrice(soup)

    statuses = ["warning", "negative"]
    tilgjengelig = None

    for status in statuses:
        searchString = f"!text-m mb-24 py-4 px-8 border-0 rounded-4 text-xs inline-flex bg-[--w-color-badge-{status}-background] s-text"
        element = soup.find('div', class_=searchString)
        if element:
            tilgjengelig = element.get_text(strip=True)
            break

    data = {
        'Index': index,
        'Finnkode': url.split('finnkode=')[1],
        'Tilgjengelighet': tilgjengelig,
        'Adresse': address,
        'Postnummer': area,
        'Leiepris': prices.get('monthly'),
        'Depositum': prices.get('deposit'),
        'URL': url,
        'Primærrom': sizes.get('info-primary-area'),
        'Internt bruksareal (BRA-i)': sizes.get('info-usable-i-area'),
        'Bruksareal': sizes.get('info-usable-area'),
        'Eksternt bruksareal (BRA-e)': sizes.get('info-usable-e-area'),
        'Balkong/Terrasse (TBA)': sizes.get('info-open-area'),
        'Bruttoareal': sizes.get('info-gross-area'),
    }
    print(f'Index {index}: {data}')

    return data


def extractDataFromAds(name: str, urls: DataFrame, outputFileName: str):
    # Create the directory if it doesn't exist
    os.makedirs(name, exist_ok=True)

    collectedData = []

    # Loop through each URL and extract property data
    try:
        # Create a folder inside the previous folder for the htmls
        os.makedirs(f'{name}/html_extracted', exist_ok=True)
        for index, url in enumerate(urls['URL']):
            time.sleep(random.uniform(0.1, 0.1))
            try:
                data = extract_ad_data(url, index, name)
                collectedData.append(data)
            except Exception as e:
                print(f'Error processing URL at index {index}: {url} - {e}')
    finally:
        # Save the combined data to a new CSV file in the output directory
        df = pd.DataFrame(collectedData)
        df.to_csv(f'{name}/{outputFileName}', index=False)
        print(f"Data extraction completed. {len(collectedData)} records saved to {name}/{outputFileName}")
        return df


if __name__ == "__main__":
    extractDataFromAds('leie', pd.read_csv('leie/crawled.csv'), 'extracted.csv')
