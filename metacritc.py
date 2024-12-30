import requests
from bs4 import BeautifulSoup
import csv
from concurrent.futures import ThreadPoolExecutor
import logging
import time
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Constants
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}

def scrape_metacritic(url):
    time.sleep(random.uniform(1, 3))
    
    """
    Scrapes details of a game from a Metacritic URL.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch {url}: {e}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    # Parsing data with robust selectors
    def safe_extract(selector, single=True, attribute=None):
        try:
            if single:
                element = soup.select_one(selector)
                return element[attribute].strip() if attribute else element.text.strip()
            else:
                elements = soup.select(selector)
                return [el.text.strip() for el in elements]
        except (AttributeError, TypeError):
            return "Not found"

    data = {
        "URL": url,
        "Title": safe_extract(".c-productHero_score-container h1"),
        "Metascore": safe_extract(".c-siteReviewScore_background span"),
        "User Score": safe_extract(".c-siteReviewScore_user span"),
        "Publisher": safe_extract(".c-gameDetails_Distributor .g-color-gray70"),
        "Developers": ", ".join(safe_extract(".c-gameDetails_Developer li", single=False)),
        "Genres": ", ".join(safe_extract(".c-genreList li .c-globalButton_label", single=False)),
        "Release Date": safe_extract(".c-gameDetails_ReleaseDate span.g-color-gray70"),
        "Platforms": ", ".join(safe_extract(".c-gameDetails_Platforms ul li", single=False))
    }

    logging.info(f"Scraped data for {data['Title']}")
    return data


def scrape_multiple_games(urls, max_workers=5):
    """
    Scrapes data for multiple games concurrently.
    """
    logging.info("Starting batch scraping...")
    all_data = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(scrape_metacritic, urls)
        for result in results:
            if result:
                all_data.append(result)
    logging.info(f"Finished scraping {len(all_data)} games.")
    return all_data

def validate_metacritic_url(url):
    """Validate if a URL is a valid Metacritic game URL."""
    import re
    pattern = r'https?://www\.metacritic\.com/game/[^/]+/[^/]+'
    return bool(re.match(pattern, url))


def save_to_csv(data, filename="output.csv"):
    """
    Saves scraped data to a CSV file.
    """
    if not data:
        logging.warning("No data to save.")
        return

    keys = data[0].keys()
    try:
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        logging.info(f"Data successfully saved to {filename}")
    except IOError as e:
        logging.error(f"Failed to save data to {filename}: {e}")


def main():
    """
    Main function with options for manual entry or file-based scraping.
    """
    while True:
        print("\nMetacritic Web Scraper")
        print("1. Enter URLs manually")
        print("2. Load URLs from a file")
        print("3. Quit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            urls = []
            print("Enter game URLs (type 'done' when finished):")
            while True:
                url = input("> ").strip()
                if url.lower() == "done":
                    break
                elif not url.startswith("https://www.metacritic.com"):
                    print("Invalid URL. Please enter a valid Metacritic URL.")
                else:
                    urls.append(url)

            if urls:
                all_data = scrape_multiple_games(urls)
                save_to_csv(all_data)

        elif choice == "2":
            try:
                with open("urls.txt", "r") as file:
                    urls = [line.strip() for line in file]
                if urls:
                    all_data = scrape_multiple_games(urls)
                    save_to_csv(all_data)
            except FileNotFoundError:
                print(f"File not found: {file_path}")
            except Exception as e:
                logging.error(f"An error occurred while reading the file: {e}")

        elif choice == "3":
            print("Exiting the scraper. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()