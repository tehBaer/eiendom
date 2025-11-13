import subprocess
import pandas as pd
from code.clean import cleanData
from code.crawl import extract_URLs
from code.export import merge
from code.extraction_property import extractPropertyDataFromAds

subprocess.run(['..\\.venv\\Scripts\\activate.bat'], shell=True, check=True)

projectName = 'jobbe'
# 1
urlBase = 'https://www.finn.no/job/search?location=1.20001.20061&occupation=0.23'
regex = r'https://www\.finn\.no/job/ad/\d+'

# urls = extract_URLs(urlBase, regex, projectName, "live_URLs.csv")
urls = pd.read_csv(f'{projectName}/live_URLs.csv')
extractPropertyDataFromAds(projectName, urls, "live_data.csv")

# ALso extract data from the downloaded sheets
#
# data = pd.read_csv(f'{projectName}/live_data.csv')
# cleanData(data, projectName, "live_data_parsed.csv")
#
# # 4
# emptyColCount = 3
# merge(emptyColCount,
#       "Main",
#       f"{projectName}/live_data_parsed.csv",
#       f"{projectName}/sheet_downloaded.csv",
#       f"{projectName}/live_missing_parsed.csv")
