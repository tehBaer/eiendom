import os
import random
import subprocess
import time

import pandas as pd
import requests
import re
from bs4 import BeautifulSoup

subprocess.run(['..\\.venv\\Scripts\\activate.bat'], shell=True, check=True)


def parse_resultpage(urlBase, term, folder, page: int = 1, df=None):
    append = ''
    if page != 1:
        append = f'&page=' + str(page)
    url = urlBase + append

    print("Analyzing URL: ", url)
    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful

    # Step 2: Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Save the HTML content to a file inside the folder
    with open(os.path.join(folder, 'page' + str(page) + '.html'), 'w', encoding='utf-8') as file:
        file.write(soup.prettify())

    # Extract the relevant data
    pattern = re.compile(term)
    # Filter out matches longer than 100 characters
    matches = {match for match in pattern.findall(str(soup)) if len(match) <= 100}

    full_urls = ['https://www.finn.no' + match for match in matches]

    # Count the unique matches
    count = len(matches)
    print(f'Number of unique matches: {count}')

    # Step 4: Store the URLs in a pandas DataFrame
    new_df = pd.DataFrame(full_urls, columns=['URL'])

    # Append new URLs to the existing DataFrame
    if df is not None:
        df = pd.concat([df, new_df], ignore_index=True)
    else:
        df = new_df
    return df


def extract_URLs(url, searchTerm, searchName, pageCount):
    # Initialize an empty DataFrame
    df = pd.DataFrame(columns=['URL'])

    # Create a folder in the parent directory of this file if it doesn't exist
    os.makedirs(searchName, exist_ok=True)

    #  Create a folder inside the previous folder for the htmls
    os.makedirs(os.path.join(searchName, 'htmls'), exist_ok=True)

    # # Run the function pagecount times and append the results to the DataFrame
    for page in range(1, pageCount + 1):
        folder = os.path.join(searchName, 'htmls')
        df = parse_resultpage(url, searchTerm, folder, page, df)
        time.sleep(random.uniform(100, 2000) / 1000)  # Add a random wait time between 2000 and 4000 milliseconds

    # Save the DataFrame as a CSV file inside the folder
    #  TODO don't overwrite the file if it exists
    df.to_csv(os.path.join(searchName, f'{searchName}_crawled.csv'), index=False)


# urlBase = 'https://www.finn.no/realestate/homes/search.html?filters=&location=0.20061&price_collective_to=5000000'
# regex = r'/realestate/.*?/ad\.html\?finnkode=\d+'
# df = extract_URLs(urlBase, regex, "oslotest", 3)

urlBase = 'https://www.finn.no/realestate/lettings/search.html?filters=&location=0.20061&price_to=20000'
regex = r'/realestate/.*?/ad\.html\?finnkode=\d+'
df = extract_URLs(urlBase, regex, "leie", 3)