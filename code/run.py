import subprocess
import os
import pandas as pd
import time
import random
from bs4 import BeautifulSoup

from code.analyze import analyze
from code.export import export
from utils import getAddress, getAllSizes, getRentPrice
from code.extract import extract_data
import requests
import re
from code.crawl import extract_URLs

subprocess.run(['..\\.venv\\Scripts\\activate.bat'], shell=True, check=True)


# 1
# urlBase = 'https://www.finn.no/realestate/lettings/search.html?lat=59.922591746076556&lon=10.73632512241602&radius=7000&price_to=18500&price_from=13000&start_month=202507&start_month=202508&stored-id=79416555&start_month=202509&area_from=30'
# regex = r'/realestate/.*?/ad\.html\?finnkode=\d+'
# df = extract_URLs(urlBase, regex, "leie", 5)


# 2
# Create the directory if it doesn't exist
# name = "leie"
# os.makedirs(name, exist_ok=True)
# # Read URLs from the crawl
# urls_df = pd.read_csv(f'{name}/crawled.csv')
# collectedData = []

# 3
analyze()

# 4
export()