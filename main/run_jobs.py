import subprocess
import pandas as pd

from main.crawl import extract_URLs
from main.export import try_merge_below
from main.extraction_jobs import extractJobDataFromAds

subprocess.run(['..\\.venv\\Scripts\\activate.bat'], shell=True, check=True)

projectName = 'jobbe'
# 1
urlBase = 'https://www.finn.no/job/search?location=1.20001.20061&occupation=0.23'
regex = r'https://www\.finn\.no/job/ad/\d+'

# urls = extract_URLs(urlBase, regex, projectName, "0_URLs.csv")
urls = pd.read_csv(f'{projectName}/0_URLs.csv')  # for debugging quickly
extractJobDataFromAds(projectName, urls, "A_live.csv")

headers = ['Finnkode', 'URL']

try_merge_below("Jobb",
                f"{projectName}/A_live.csv",
                f"{projectName}/sheet_downloaded.csv",
                f"{projectName}/C_filtered.csv",
                f"{projectName}/B_aligned.csv",
                headers)
