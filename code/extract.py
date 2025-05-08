import random
import subprocess
import time

import pandas as pd

from utils import *

# Ensure the path to the virtual environment activation script is correct
subprocess.run(['..\\.venv\\Scripts\\activate.bat'], shell=True, check=True)

saveHTMLcount = 5


def extract_data(url, index, name, save=False):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    # create the folder if it doesn't exist
    os.makedirs(name, exist_ok=True)
    # Create a folder inside the previous folder for the htmls
    os.makedirs(f'{name}/html_extracted', exist_ok=True)

    if (index < saveHTMLcount or save):
        # Save the HTML content to a file inside the folder
        with open(f'{name}/html_extracted/page{index}.html', 'w', encoding='utf-8') as file:
            file.write(soup.prettify())

    address, area = getAddress(soup)
    sizes = getAllSizes(soup)
    price = getRentPrice(soup)
    return {
        'Index': index,
        'Adresse': address,
        'Postnummer': area,
        'URL': url,
        'Leiepris': price,
        'Primærrom': sizes.get('info-primary-area'), #Primærrom
        'Internt bruksareal (BRA-i)': sizes.get('info-usable-i-area'), #Internt bruksareal(BRA-i)
        'Bruksareal': sizes.get('info-usable-area'), #Bruksareal
        'Eksternt bruksareal (BRA-e)': sizes.get('info-usable-e-area'), #Eksternt bruksareal (BRA-e)
        'Balkong/Terrasse (TBA)': sizes.get('info-open-area'), #Balkong/Terrasse (TBA)
        '#Bruttoareal': sizes.get('info-gross-area'), #Bruttoareal
    }

if __name__ == "__main__":

    # Create the directory if it doesn't exist
    name = "leie"
    os.makedirs(name, exist_ok=True)
    # Read URLs from the crawl
    urls_df = pd.read_csv(f'{name}/crawled.csv')
    collectedData = []

    # Loop through each URL and extract property data
    try:
        # Create a folder inside the previous folder for the htmls
        os.makedirs(f'{name}/html_extracted', exist_ok=True)
        for index, url in enumerate(urls_df['URL']):
            time.sleep(random.uniform(0.1, 0.1))
            try:
                data = extract_data(url, index, name)
                print(f'Index {index}: {data}')
                collectedData.append(data)
            except Exception as e:
                print(f'Error processing URL at index {index}: {url} - {e}')
    finally:
        # Save the combined data to a new CSV file in the output directory
        df = pd.DataFrame(collectedData)
        df.to_csv(f'{name}/extracted.csv', index=False)
        print('CSV file has been written.')
