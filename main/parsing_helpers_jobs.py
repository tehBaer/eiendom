import re


def getCompany(soup):
    """Extract company name from the advertising JSON data or company logo."""
    import json

    # First, try to extract from the advertising-initial-state script tag
    script_tag = soup.find('script', {'id': 'advertising-initial-state', 'type': 'application/json'})
    if script_tag:
        try:
            data = json.loads(script_tag.string)
            # Navigate to the targeting array in GAM config
            targeting = data.get('config', {}).get('adServer', {}).get('gam', {}).get('targeting', [])

            # Find the company_name entry
            for item in targeting:
                if item.get('key') == 'company_name' and item.get('value'):
                    return item['value'][0]
        except (json.JSONDecodeError, KeyError, IndexError):
            pass

    # Fallback: Try to find company logo image which contains company ID in URL
    logo_img = soup.find('img', src=re.compile(r'finncdn\.no/mmo/logo'))
    if logo_img and logo_img.get('alt'):
        return logo_img.get('alt').strip()

    return None

def getJobTitle(soup):
    """Extract job title from the advertising JSON data."""
    import json

    # Try to extract from the advertising-initial-state script tag
    script_tag = soup.find('script', {'id': 'advertising-initial-state', 'type': 'application/json'})
    if script_tag:
        try:
            data = json.loads(script_tag.string)
            # Navigate to the targeting array in GAM config
            targeting = data.get('config', {}).get('adServer', {}).get('gam', {}).get('targeting', [])

            # Find the job_title entry
            for item in targeting:
                if item.get('key') == 'job_title' and item.get('value'):
                    return item['value'][0]
        except (json.JSONDecodeError, KeyError, IndexError):
            pass

    return None

def getOccupation(soup):
    """Extract occupation codes from the advertising JSON data."""
    import json

    # Try to extract from the advertising-initial-state script tag
    script_tag = soup.find('script', {'id': 'advertising-initial-state', 'type': 'application/json'})
    if script_tag:
        try:
            data = json.loads(script_tag.string)
            # Navigate to the targeting array in GAM config
            targeting = data.get('config', {}).get('adServer', {}).get('gam', {}).get('targeting', [])

            # Find the occupation entry
            for item in targeting:
                if item.get('key') == 'occupation' and item.get('value'):
                    return item['value']  # Return all occupation codes as a list
        except (json.JSONDecodeError, KeyError, IndexError):
            pass

    return None

def getJobPositions(soup):
    """Extract number of job positions from the advertising JSON data."""
    import json

    # Try to extract from the advertising-initial-state script tag
    script_tag = soup.find('script', {'id': 'advertising-initial-state', 'type': 'application/json'})
    if script_tag:
        try:
            data = json.loads(script_tag.string)
            # Navigate to the targeting array in GAM config
            targeting = data.get('config', {}).get('adServer', {}).get('gam', {}).get('targeting', [])

            # Find the job_positions entry
            for item in targeting:
                if item.get('key') == 'job_positions' and item.get('value'):
                    return item['value'][0]  # Return as string or convert to int if needed
        except (json.JSONDecodeError, KeyError, IndexError):
            pass

    return None

def getIndustry(soup):
    """Extract industry from the advertising JSON data."""
    import json

    # Try to extract from the advertising-initial-state script tag
    script_tag = soup.find('script', {'id': 'advertising-initial-state', 'type': 'application/json'})
    if script_tag:
        try:
            data = json.loads(script_tag.string)
            # Navigate to the targeting array in GAM config
            targeting = data.get('config', {}).get('adServer', {}).get('gam', {}).get('targeting', [])

            # Find the industry entry
            for item in targeting:
                if item.get('key') == 'industry' and item.get('value'):
                    return item['value'][0]
        except (json.JSONDecodeError, KeyError, IndexError):
            pass

    return None




def getAdTitle(soup):
    """Extract job ad title from the page title."""
    # Find the title tag
    title_tag = soup.find('title')
    if title_tag:
        title = title_tag.get_text()
        # Remove " | FINN.no" suffix if present
        if ' | FINN.no' in title:
            title = title.split(' | FINN.no')[0]
        return title.strip()

    return None


def getDeadline(soup):
    """Extract application deadline from the job ad."""
    import re

    # Find all list items
    list_items = soup.find_all('li')

    for li in list_items:
        text = li.get_text()
        # Check if this item contains "Frist"
        if 'Frist' in text:
            # Look for date pattern (dd.mm.yyyy)
            date_match = re.search(r'\d{2}\.\d{2}\.\d{4}', text)
            if date_match:
                return date_match.group(0)

    return None