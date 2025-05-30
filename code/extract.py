import random
import subprocess
import time
import pandas as pd
from pandas import DataFrame
from utils import *

# Ensure the path to the virtual environment activation script is correct
subprocess.run(['..\\.venv\\Scripts\\activate.bat'], shell=True, check=True)


def get_ad_content(url, projectName, auto_save_new=True, force_save=False):
    """
    Fetches ad data from the given URL and saves the HTML content if specified.
    :param url: The URL of the ad to extract data from.
    :param projectName: The name of the project folder to save the HTML content.
    :param force_save: If True, forces re-fetching of the ad data.
    :return: A dictionary containing extracted ad data.
    """
    finnkode = url.split('finnkode=')[1]
    html_file_path = f'{projectName}/html_extracted/{finnkode}.html'
    exists = os.path.exists(html_file_path)

    if (force_save):
        print(f"Force-saving HTML content for {finnkode}.")
        return save_ad_html_content(url, projectName, finnkode)

    elif (exists or not auto_save_new):
        with open(html_file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            return soup
    else:
        print(f"Saving HTML content for {finnkode}.")
        return save_ad_html_content(url, projectName, finnkode)


def save_ad_html_content(url, projectName, finnkode):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    # Save the HTML content to a file inside the folder
    html_file_path = f'{projectName}/html_extracted/{finnkode}.html'
    with open(html_file_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))
        return soup


def extract_ad_data(url, index, projectName):
    try:
        soup = get_ad_content(url, projectName)
    except Exception as e:
        print(f"Error fetching content for URL {url}: {e}")
        #     throw exception
        raise



    address, area = getAddress(soup)
    sizes = getAllSizes(soup)
    prices = getRentPrice(soup)
    date = getDate(soup)

    statuses = ["warning", "negative"]
    tilgjengelig = None

    for status in statuses:
        searchString = f"!text-m mb-24 py-4 px-8 border-0 rounded-4 text-xs inline-flex bg-[--w-color-badge-{status}-background] s-text"
        element = soup.find('div', class_=searchString)
        if element:
            tilgjengelig = element.get_text(strip=True)
            break

    data = {
        # 'Index': index,
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
        # 'Innflytting': date.get('start'),
        # 'Utflytting': date.get('end'),
    }
    print(f'Index {index}: {data}')

    return data


def extractDataFromAds(projectName: str, urls: DataFrame, outputFileName: str):
    # Create the directory if it doesn't exist
    os.makedirs(projectName, exist_ok=True)

    collectedData = []

    # Loop through each URL and extract property data
    try:
        # Create a folder inside the previous folder for the htmls
        os.makedirs(f'{projectName}/html_extracted', exist_ok=True)
        for index, url in enumerate(urls['URL']):
            time.sleep(random.uniform(0.1, 0.1)) #todo do a deltatime instead of a fixed sleep time
            try:
                data = extract_ad_data(url, index, projectName)
                collectedData.append(data)
            except Exception as e:
                print(f'Error processing URL at index {index}: {url} - {e}')
    finally:
        # Save the combined data to a new CSV file in the output directory
        df = pd.DataFrame(collectedData)
        df.to_csv(f'{projectName}/{outputFileName}', index=False)
        print(f"Data extraction completed. {len(collectedData)} records saved to {projectName}/{outputFileName}")
        return df


if __name__ == "__main__":
    extractDataFromAds('leie', pd.read_csv('leie/live_URLs.csv'), 'live_data.csv')
