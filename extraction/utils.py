import re


def OLD_getPrice(soup):
    pricing_section = soup.find('section', {'aria-labelledby': 'sales-costs'})

    prisantydning_match = re.search(r'kr\s*([\d\s]+),-', pricing_section.get_text())
    prisantydning = None
    if prisantydning_match:
        prisantydning = prisantydning_match.group(1).replace('\xa0', '')
    return prisantydning


def getPriceHelper(section):
    total_price_match = re.search(r'([\d\xa0\s]+) kr', section.get_text())
    total_price = None
    if total_price_match:
        total_price = total_price_match.group(1).replace('\xa0', '').replace(' ', '')
    return total_price

def getPrice(soup):
    pricing_section = soup.find('div', {'data-testid': 'pricing-total-price'})
    price = getPriceHelper(pricing_section)
    return price



def getAddress(soup):
    address_element = soup.find('span', {'data-testid': 'object-address'})
    address = address_element.get_text().strip() if address_element else None
    if address:
        parts = address.split(',')
        if len(parts) > 1:
            address = parts[0].strip()
            area = parts[1].strip()
        else:
            address = parts[0].strip()
            area = None
    else:
        address = None
        area = None
    return address, area


def getSize(soup):
    bruksareal_element = soup.find('div', {'data-testid': 'info-usable-area'}).find('dd', {'class': 'm-0 font-bold'})
    bruksareal = bruksareal_element.get_text().strip() if bruksareal_element else None
    if bruksareal:
        bruksareal_match = re.search(r'(\d+)\s*m²', bruksareal)
        bruksareal = bruksareal_match.group(1) if bruksareal_match else None
    return bruksareal