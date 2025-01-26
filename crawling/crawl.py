import random
import subprocess
import time

import pandas as pd
import requests
import re
from bs4 import BeautifulSoup

subprocess.run(['..\\.venv\\Scripts\\activate.bat'], shell=True, check=True)

# Step 1: Send a GET request to the URL
urlBase = 'https://www.finn.no/realestate/homes/search.html?lifecycle=1&location=0.20061&sort=AREA_PROM_DESC&price_collective_to=6500000'

def crawl_finn_realestate(append: str = '', df=None):
    url = urlBase + append

    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful

    # Step 2: Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Save the HTML content to a file
    with open('output.html', 'w', encoding='utf-8') as file:
        file.write(soup.prettify())

    # Step 3: Extract the relevant data
    pattern = re.compile(r'/realestate/homes/ad\.html\?finnkode=\d+')
    matches = set(pattern.findall(str(soup)))  # Use a set to store unique matches

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

# Initialize an empty DataFrame
df = pd.DataFrame(columns=['URL'])

# Run the function 16 times and append the results to the DataFrame
for page in range(1, 17):
    print(f'Analyzing page {page}')
    if page == 1:
        df = crawl_finn_realestate('', df)
    else:
        df = crawl_finn_realestate(f'&page={page}', df)
    time.sleep(random.uniform(100, 2000) / 1000)  # Add a random wait time between 2000 and 4000 milliseconds


# Save the DataFrame as a CSV file
df.to_csv('property_urls.csv', index=False)