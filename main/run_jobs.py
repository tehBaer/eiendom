import subprocess
import pandas as pd
from main.export import  try_merge_below
from main.extraction_jobs import extractJobDataFromAds

subprocess.run(['..\\.venv\\Scripts\\activate.bat'], shell=True, check=True)

projectName = 'jobbe'
# 1
urlBase = 'https://www.finn.no/job/search?location=1.20001.20061&occupation=0.23'
regex = r'https://www\.finn\.no/job/ad/\d+'

# urls = extract_URLs(urlBase, regex, projectName, "live_URLs.csv")
urls = pd.read_csv(f'{projectName}/live_URLs.csv')  # for debugging quickly
extractJobDataFromAds(projectName, urls, "live_data.csv")

headers = ['Finnkode', 'URL']

try_merge_below(projectName,
                "Jobb",
                f"{projectName}/live_data.csv",
                f"{projectName}/sheet_downloaded.csv",
                f"{projectName}/live_missing.csv",
                f"{projectName}/live_missing_aligned.csv",
                headers)
