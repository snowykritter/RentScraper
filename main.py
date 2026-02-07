import json
import time

from scraping.scraping_functions import initialize_webdriver, scrape_sites


def main():
    SEARCH_CONFIG = [
        {
            "site": "Redfin",
            "url": "https://www.redfin.com/city/17680/CA/Santa-Cruz/rentals",
            "max_price": 1500,
            "min_beds": 1,
            "min_baths": 1
        },
        {
            "site": "Zillow",
            "url": "https://www.zillow.com/santa-cruz-ca/rentals",
            "max_price": 1500,
            "min_beds": 1,
            "min_baths": 1
        }
    ]

    print("Initializing WebDriver")
    driver = initialize_webdriver()
    all_results = []

    try:
        for config in SEARCH_CONFIG:
            print(f"Scraping {config['site']}")
            
            results = scrape_sites(
                site_name=config['site'],
                URL=config['url'],
                driver=driver,
                price_thresh=config['max_price'],
                rooms=config['min_beds'],
                b_rooms=config['min_baths']
            )
            
            all_results.extend(results)
            time.sleep(3)

    finally:
        print("Kill browser")
        driver.quit()

    save_results(all_results)

def save_results(data):
    if not data:
        print("No listings found")
        return
        
    filename = "rentals.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Found {len(data)} listings. Saved to {filename}")

if __name__ == "__main__":
    main()