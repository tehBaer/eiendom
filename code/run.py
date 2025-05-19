import subprocess
import pandas as pd
from code.clean import cleanData
from code.crawl import extract_URLs
from code.export import merge
from code.extract import extractDataFromAds

subprocess.run(['..\\.venv\\Scripts\\activate.bat'], shell=True, check=True)


projectName = 'leie'
# 1
urlBase = 'https://www.finn.no/realestate/lettings/search.html?lat=59.922591746076556&lon=10.73632512241602&radius=7000&price_to=18500&price_from=13000&start_month=202507&start_month=202508&stored-id=79416555&start_month=202509&area_from=30'
regex = r'/realestate/.*?/ad\.html\?finnkode=\d+'
urls = extract_URLs(urlBase, regex, projectName, "live_URLs.csv")


# 2
# urls = pd.read_csv(f'{projectName}/live_URLs.csv')
# extractDataFromAds(projectName, urls, "live_data.csv")

# ALso extract data from the downloaded sheets

# 3
data = pd.read_csv(f'{projectName}/live_data.csv')
cleanedData = cleanData(data, projectName, "live_data_cleaned.csv")

# 4
emptyColCount = 2
merge(emptyColCount, "Main")