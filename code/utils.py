﻿import os
import re

import requests
from bs4 import BeautifulSoup


def saveToFile(url, filename, projectname):
    # Create the folder if it doesn't exist
    os.makedirs(projectname, exist_ok=True)
    # Create a folder inside the previous folder for the htmls
    os.makedirs(f'{projectname}/html_extracted', exist_ok=True)

    # Save the HTML content to a file inside the folder
    with open(f'{projectname}/html_extracted/{filename}.html', 'w', encoding='utf-8') as file:
        file.write(url.prettify())


def saveToFile(url, filename, folder):
    # Create the folder if it doesn't exist
    os.makedirs(folder, exist_ok=True)
    # Create a folder inside the previous folder for the htmls
    os.makedirs(f'{folder}/html_extracted', exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful
    soup = BeautifulSoup(response.text, 'html.parser')  # Parse the HTML content
    with open(f"{folder}/{filename}.html", "w", encoding="utf-8") as file:
        file.write(soup.prettify())  # Use prettify on the BeautifulSoup object


def OLD_getBuyPrice(soup):
    pricing_section = soup.find('section', {'aria-labelledby': 'sales-costs'})

    prisantydning_match = re.search(r'kr\s*([\d\s]+),-', pricing_section.get_text())
    prisantydning = None
    if prisantydning_match:
        prisantydning = prisantydning_match.group(1).replace('\xa0', '')
    return prisantydning


def getBuyPrice(soup):
    pricing_section = soup.find('div', {'data-testid': 'pricing-total-price'})
    total_price_match = re.search(r'([\d\xa0\s]+) kr', pricing_section.get_text())
    total_price = None
    if total_price_match:
        total_price = total_price_match.group(1).replace('\xa0', '').replace(' ', '')
    return total_price


def getAddress(soup):
    address_element = soup.find('span', {'data-testid': 'object-address'})
    if address_element:
        full_address = address_element.get_text().strip()
        if ',' in full_address:
            address, area_part = map(str.strip, full_address.split(',', 1))
            area = GetArea(area_part)
        else:
            address = None
            area = GetArea(full_address)
    else:
        address = None
        area = None
    return address, area


def GetArea(part):
    area = part.strip()
    area_match = re.search(r'(\d+)', area)
    area = area_match.group(1) if area_match else None
    return area


def getSize(soup):
    element = soup.find('div', {'data-testid': 'info-usable-area'})
    output = getSizeHelper(soup, element)
    if not output:
        element = soup.find('div', {'data-testid': 'info-usable-i-area'})
        output = getSizeHelper(soup, element)
    return output


def getSizeHelper(soup, element):
    usable_area = element.get_text().strip() if element else ""
    # print(usable_area)
    if usable_area:
        usable_area_match = re.search(r'(\d+)\s*m²', usable_area)
        usable_area = usable_area_match.group(1) if usable_area_match else ""
    return usable_area


def getAllSizes(soup):
    sizes = {}
    test_ids = [
        'info-usable-area',
        'info-usable-i-area',
        'info-primary-area',
        'info-gross-area',
        'info-usable-e-area'
        'info-open-area'
    ]

    for test_id in test_ids:
        element = soup.find('div', {'data-testid': test_id})
        sizes[test_id] = getSizeHelper(soup, element)

    return sizes


def getPriceHelper(pricing_section, term):
    text = pricing_section.get_text().strip() if pricing_section else ""

    rent_price_match = re.search(rf'{term}\s*([\d\xa0\s]+)', text)
    if rent_price_match:
        rent_price = removeSpaces(rent_price_match.group(1))
        return rent_price


def getRentPrice(soup):
    pricing_sections = soup.find('div', {'data-testid': 'pricing-common-monthly-cost'})
    rent_price = getPriceHelper(pricing_sections, "Månedsleie") if pricing_sections else None

    deposit_sections = soup.find('div', {'data-testid': 'pricing-deposit'})
    deposit_price = getPriceHelper(deposit_sections, "Depositum")

    return {
        'monthly': rent_price,
        'deposit': deposit_price
    }


def removeSpaces(string):
    return string.replace('\xa0', '').replace(' ', '')
