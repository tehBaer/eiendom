import subprocess

from code.extract import extract_data
from utils import *

# Ensure the path to the virtual environment activation script is correct
subprocess.run(['..\\.venv\\Scripts\\activate.bat'], shell=True, check=True)

# saveToFile("https://www.finn.no/realestate/lettings/ad.html?finnkode=50296946", "html_extracted/page98", "leie")

url = 'https://www.finn.no/realestate/lettings/ad.html?finnkode=405171898'
print(extract_data(url, 0, "leie", True))