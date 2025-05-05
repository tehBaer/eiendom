import subprocess

from utils import *

# Ensure the path to the virtual environment activation script is correct
subprocess.run(['..\\.venv\\Scripts\\activate.bat'], shell=True, check=True)

saveToFile("https://www.finn.no/realestate/lettings/ad.html?finnkode=181354831", "page12", "leie")
