import requests, json
from bs4 import BeautifulSoup
from datetime import datetime

COMPLAINT_ID = "complaint"
LOCATION_STRING = "Location of Complaint"
RECV_STRING = "Date Received"
SOURCE_NAME_STRING = "Source Name"
SOURCE_ADDRESS_STRING = "Source Address"

OUTPUT_PATH = 'complaints.json'


def scrape_website(url):
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    else:
        raise RuntimeError(f'Scraper failed! Recieved: {response}')


def get_complaint(soup):
    elem = soup.find(id=COMPLAINT_ID)
    if elem:
        elem = elem.find_next_sibling('p')
        if elem: return elem.get_text()
    return None
    

def get_tabe_element(soup, string):
    elem = soup.find('th', string=string)    
    if elem:
        elem = elem.find_next('td')
        if elem: return elem.get_text(strip=True)
    return None


def get_location(soup):
    return get_tabe_element(soup, string=LOCATION_STRING)


def get_date_received(soup):
    date = get_tabe_element(soup, string=RECV_STRING)
    return datetime.strptime(date, '%B %d, %Y, %I:%M %p').strftime("%Y-%m-%d %H:%M:%S")


def get_source_name(soup):
    return get_tabe_element(soup, string=SOURCE_NAME_STRING)


def get_source_location(soup):
    return get_tabe_element(soup, string=SOURCE_ADDRESS_STRING)


def get_href_suffixes(soup, prefix):
    return [l['href'].replace(prefix, '') for l in soup.find_all('a') if l.get('href', '').startswith(prefix)]


def scrape_complaint(complaint_id):
    url = f"https://cts.gaepd.org/Public/ComplaintDetails/{complaint_id}"
    soup = scrape_website(url)

    entry = {}
    entry['_id'] = complaint_id
    entry['complaint'] = get_complaint(soup)
    entry['location'] = get_location(soup)
    entry['date_received'] = get_date_received(soup)
    entry['source_name'] = get_source_name(soup)
    entry['source_location'] = get_source_location(soup)
    return entry


def get_complaint_ids(date_from, date_to):
    complaint_ids, n = [], 1
    while True:
        print(f'Looking for complaints on page {n}...')
        url = f'https://cts.gaepd.org/Public?submit=Page&page={n}&sort=IdDesc&DateFrom={date_from}&DateTo={date_to}&TypeId=800670b6-2ae3-49e0-afef-37156006bf1f#search-results'
        soup = scrape_website(url)
        ids = get_href_suffixes(soup, '/Public/ComplaintDetails/')
        if len(ids) > 0:
            complaint_ids += ids
            n += 1
        else:
            break
    return complaint_ids


def main():
    complaint_ids = get_complaint_ids('1-1-2020', '4-1-2024')

    data = []
    for _id in complaint_ids:
        print(f'Scraping complaint id {_id}...')
        data += [scrape_complaint(_id)]

        with open(OUTPUT_PATH, 'w') as f:
            json.dump(data, f, indent=4)


if __name__ == '__main__':
    main()