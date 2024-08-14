# Chihuahua Governors Scraper 🏛️

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.x-yellowgreen)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey)

This project is a web scraper designed to collect data on the Governors of Chihuahua, Mexico. The scraper retrieves information from an official government website and further enriches this data by scraping additional details from Wikipedia, such as birth and death dates, occupation, and nationality. The collected data is stored in a SQLite database.

## Features ✨
- **Web Scraping**: Extracts a list of governors and their terms of service.
- **Sub-scraping from Wikipedia**: Gathers additional biographical data for each governor.
- **Database Storage**: Saves the collected information in a SQLite database.
- **Error Handling**: Manages network issues and missing data gracefully.

## Installation 🛠️

Clone the repository and install the dependencies:

```bash
git clone https://github.com/yourusername/chihuahua-governors-scraper.git
cd chihuahua-governors-scraper
pip install -r requirements.txt
```

## Usage 🚀

Run the scraper with:

```bash
python -m scraper.scraper
```

The data will be saved in a SQLite database named governors.db.

## Project Structure 📂

```bash
chihuahua-governors-scraper/
│
├── README.md
├── requirements.txt
├── scraper/
│   ├── __init__.py
│   ├── scraper.py
│   └── database.py
```

## Contributing 🤝

Contributions are welcome! Please fork the repository and submit a pull request.

## License 📜
This project is licensed under the MIT License - see the LICENSE file for details.