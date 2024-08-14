import requests
import logging
from bs4 import BeautifulSoup
from scraper.database import GovernorDatabase

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ChihuahuaGovernorsScraper:
    def __init__(self, url):
        self.url = url
        self.db = GovernorDatabase()

    def fetch_data(self):
        logging.info(f"Fetching data from {self.url}")
        try:
            response = requests.get(self.url)
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error fetching data: {e}")
            raise
        logging.info("Data fetched successfully")
        return response.content

    def parse_data(self, content):
        logging.info("Parsing data")
        soup = BeautifulSoup(content, "html.parser")
        governors = []
        for li in soup.select("ul.rteindent1 li"):
            governor_data = self.extract_governor_data(li)
            if governor_data and governor_data["wikipedia_link"]:
                wikipedia_info = self.extract_wikipedia_info(
                    governor_data["wikipedia_link"]
                )
                if (
                    wikipedia_info["nationality"] == "Mexicana"
                    or wikipedia_info["nationality"] is None
                ):
                    governor_data.update(wikipedia_info)
                else:
                    logging.warning(
                        f"Nationality of governor {governor_data['name']} from Wikipedia is {wikipedia_info['nationality']}. Skipping Wikipedia data."
                    )
                governors.append(governor_data)
        return governors

    def extract_governor_data(self, li):
        links = li.find_all("a")
        if len(links) < 2:
            logging.warning("Unexpected number of links in list item")
            return None

        start_date = links[0].text.strip()
        if len(links) == 2:
            end_date = None
            name = links[1].text.strip()
            wikipedia_link = links[1].get("href")
        elif len(links) == 3:
            end_date = links[1].text.strip()
            name = links[2].text.strip()
            wikipedia_link = links[2].get("href")
        else:
            logging.warning("Unexpected number of links in list item")
            return None

        return {
            "name": name,
            "wikipedia_link": wikipedia_link,
            "periods": [{"start_date": start_date, "end_date": end_date}],
            "birth_date": None,
            "death_date": None,
            "occupation": None,
            "nationality": None,
        }

    def extract_wikipedia_info(self, wikipedia_link):
        logging.info(f"Fetching Wikipedia data for {wikipedia_link}")

        try:
            response = requests.get(wikipedia_link)
            response.raise_for_status()
        except requests.RequestException as err:
            logging.error(f"Error occurred: {err}")
            return {
                "birth_date": None,
                "death_date": None,
                "occupation": None,
                "nationality": None,
            }

        soup = BeautifulSoup(response.content, "html.parser")

        if soup.find("table", id="disambigbox"):
            logging.warning(f"{wikipedia_link} is a disambiguation page")
            return {
                "birth_date": None,
                "death_date": None,
                "occupation": None,
                "nationality": None,
            }

        if soup.find("div", class_="mw-newarticletextanon") or soup.find(
            "div", class_="noarticletext"
        ):
            logging.warning(f"{wikipedia_link} does not contain any content.")
            return {
                "birth_date": None,
                "death_date": None,
                "occupation": None,
                "nationality": None,
            }

        birth_date = self.extract_info(soup, "Nacimiento")
        death_date = self.extract_info(soup, "Fallecimiento")
        occupation = self.extract_info(soup, "Ocupación")
        nationality = self.extract_info(soup, "Nacionalidad")
        periods = self.extract_governor_periods(soup)

        logging.info("Wikipedia data fetched successfully")
        return {
            "birth_date": birth_date,
            "death_date": death_date,
            "occupation": occupation,
            "nationality": nationality,
            "periods": periods,
        }

    def extract_info(self, soup, label):
        row = soup.find("th", string=label)
        if row:
            info = row.find_next_sibling("td")
            if info:
                return " ".join(info.stripped_strings)
        return None

    def extract_governor_periods(self, soup):
        periods = []

        governor_row = soup.select_one(
            'tr:has(a:-soup-contains("Gobernador de Chihuahua"))'
        )

        if governor_row:
            for sibling in governor_row.find_next_siblings("tr"):
                if not sibling.find("td") or sibling.find(
                    "th", string=lambda text: "Información personal" in text
                ):
                    break

                if sibling.find("th") or sibling.find("hr"):
                    continue

                period_row = sibling.find("td")
                if period_row:
                    period_text = period_row.text.strip()
                    if "-" in period_text:
                        start_date, end_date = period_text.split("-")
                    else:
                        start_date = period_text
                        end_date = None

                    periods.append(
                        {
                            "start_date": start_date.strip(),
                            "end_date": end_date.strip() if end_date else None,
                        }
                    )

        return periods

    def save_to_database(self, governors):
        logging.info("Saving data to database")
        for governor in governors:
            if not self.db.governor_exists(
                governor["name"], governor["wikipedia_link"]
            ):
                gov_id = self.db.insert_governor(
                    governor["name"],
                    governor["wikipedia_link"],
                    governor["birth_date"],
                    governor["death_date"],
                    governor["occupation"],
                    governor["nationality"],
                )
                for period in governor["periods"]:
                    self.db.insert_governor_period(
                        gov_id, period["start_date"], period["end_date"]
                    )
        logging.info("Data saved successfully")

    def run(self):
        logging.info("Starting scraper")
        content = self.fetch_data()
        governors = self.parse_data(content)
        self.save_to_database(governors)
        logging.info("Scraper finished successfully")


if __name__ == "__main__":
    url = "https://chihuahua.gob.mx/info/gobernadores-del-estado"
    scraper = ChihuahuaGovernorsScraper(url)
    scraper.run()
