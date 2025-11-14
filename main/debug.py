from bs4 import BeautifulSoup

from main.parsing_helpers_jobs import getJobTitle, getOccupation, getJobPositions, getIndustry, getAdTitle, getDeadline
from parsing_helpers_jobs import getCompany

with open('jobbe/html_extracted/436826659.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')
result = getDeadline(soup)
print(f"Output: {result}")
