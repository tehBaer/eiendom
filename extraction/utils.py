import re


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
    address = address_element.get_text().strip() if address_element else None
    if address:
        parts = address.split(',')
        if len(parts) > 1:
            address = parts[0].strip()
            area = parts[1].strip()
            area_match = re.search(r'(\d+)', area)
            area = area_match.group(1) if area_match else None
        else:
            address = parts[0].strip()
            area = None
    else:
        address = None
        area = None
    return address, area


def getSize(soup):
    element = soup.find('div', {'data-testid': 'info-usable-area'})
    output = getSizeHelper(soup, element)
    if not output:
        element = soup.find('div', {'data-testid': 'info-usable-i-area'})
        output = getSizeHelper(soup, element)
    return output

def getSizeHelper(soup, element):
    usable_area = element.get_text().strip() if element else None
    if usable_area:
        usable_area_match = re.search(r'(\d+)\s*m²', usable_area)
        usable_area = usable_area_match.group(1) if usable_area_match else None
    return usable_area
