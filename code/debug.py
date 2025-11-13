import requests

url = "https://www.finn.no/job/search?location=1.20001.20061&occupation=0.23"
response = requests.get(url)
response.raise_for_status()  # Raises an error if the request failed



with open("page.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("HTML downloaded and saved to page.html")