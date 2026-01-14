import json
import random
import re
import time

import undetected_chromedriver as uc
from bs4 import BeautifulSoup


def initialize_webdriver():

    options = uc.ChromeOptions()

    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = uc.Chrome(options=options)


    return driver

def scrape_sites(site_name, URL, driver, price_thresh, rooms, b_rooms):
    all_results = []
    unique_urls = set()
    page = 1

    while True:
        if site_name.lower() == "redfin":
            current_url = URL if page == 1 else URL.replace("/rentals", f"/rentals/page-{page}")
        elif site_name.lower() == "zillow":
            current_url = URL if page == 1 else URL.rstrip('/') + f"/{page}_p/"
        else:
            break

        driver.get(current_url)
        time.sleep(random.uniform(3, 5))

        if page > 1 and driver.current_url.rstrip('/') == URL.rstrip('/'):
            break

        if site_name.lower() == "zillow":
            try:
                scroll_element_selector = "#search-page-list-container"

                for i in range(1, 11):
                    driver.execute_script(
                        f"document.querySelector('{scroll_element_selector}').scrollTo(0, document.querySelector('{scroll_element_selector}').scrollHeight * {i/10});"
                    )
                    time.sleep(random.uniform(0.7, 1.2))
            except Exception:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        else:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(3, 5))
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        if site_name.lower() == "redfin":
            new_listings = parse_redfin(soup, price_thresh, rooms, b_rooms)
        elif site_name.lower() == "zillow":
            new_listings = parse_zillow(soup, price_thresh, rooms, b_rooms)
        
        if not new_listings:
            break
            
        for item in new_listings:
            if item['url'] not in unique_urls:
                all_results.append(item)
                unique_urls.add(item['url'])
        
        print(f"[{site_name}] Page {page} done. Found {len(new_listings)} matching listings.")
        page += 1

    return all_results

def parse_redfin(soup, price_thresh, rooms, b_rooms):
    listings = []
    containers = soup.find_all("div", class_="HomeCardContainer")
    
    for box in containers:
        try:
            json_script = box.find('script', {'type': 'application/ld+json'})
            if not json_script: continue
            
            data = json.loads(json_script.string)
            prop, offer = data[0], data[1]

            price = int(offer['offers']['price'])
            beds = int(prop.get('numberOfRooms', 0))
            
            baths_text = box.select_one('.bp-Homecard__Stats--baths').text
            baths = int(''.join(filter(str.isdigit, baths_text)))

            price_per_bed = price / beds if beds > 0 else price
            if price_per_bed <= price_thresh and beds >= rooms and baths >= b_rooms:
                listings.append({
                    "address": prop['name'],
                    "price": price,
                    "beds": beds,
                    "baths": baths,
                    "price_per_bed": price_per_bed,
                    "url": offer['url'],
                    "source": "Redfin"
                })
        except Exception:
            continue
    return listings

def parse_zillow(soup, price_thresh, rooms, b_rooms):
    listings = []
    containers = soup.find_all("article", {"data-test": "property-card"})
    
    for box in containers:
        try:
            price_elem = box.find(attrs={"data-test": "property-card-price"})
            if not price_elem: continue
            price_text = price_elem.get_text()
            price = int(re.sub(r'[^\d]', '', price_text))


            details_list = box.find("ul", {"data-testid": "property-card-details"})
            if not details_list: continue

            stats = details_list.find_all("li")
            beds = int(re.sub(r'[^\d]', '', stats[0].get_text())) if len(stats) > 0 else 0
            baths = int(re.sub(r'[^\d]', '', stats[1].get_text())) if len(stats) > 1 else 0

            address_elem = box.find("address")
            address = address_elem.get_text() if address_elem else "Unknown Address"
            
            link_elem = box.find("a", {"data-test": "property-card-link"})
            url = link_elem['href'] if link_elem else ""
            if url and not url.startswith("http"):
                url = "https://www.zillow.com" + url

            price_per_bed = price / beds if beds > 0 else price
            
            if price_per_bed <= price_thresh and beds >= rooms and baths >= b_rooms:
                listings.append({
                    "address": address,
                    "price": price,
                    "beds": beds,
                    "baths": baths,
                    "price_per_bed": price_per_bed,
                    "url": url,
                    "source": "Zillow"
                })
        except Exception as e:
            continue
            
    return listings
