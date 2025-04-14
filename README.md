# Cambridge School Scraper

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.7+-blue.svg" alt="Python 3.7+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">
</div>

## Overview

A robust web scraping tool designed to extract comprehensive information about Cambridge schools worldwide from the official Cambridge International Education website: [Find a Cambridge School](https://www.cambridgeinternational.org/why-choose-us/find-a-cambridge-school/).

## Features

- Extract school data from 160+ countries
- Collect detailed school information including location, center and if private candidates accepted
- Export data in multiple formats (CSV, JSON)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cambridge_school_scraper.git
   cd cambridge_school_scraper
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Requirements

This project requires:
- Python 3.7+
- Selenium WebDriver
- Chrome/Firefox WebDriver (depending on your configuration)
- Additional dependencies listed in `requirements.txt`

## Usage

```python
from cambridge_scraper import CambridgeSchoolScraper

# Initialize the scraper
scraper = CambridgeSchoolScraper()
```

## Contributing

Contributions are welcome! To contribute:

1. Fork this repository
2. Clone your fork
3. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```
4. Create a new branch for your feature
5. Make your changes
6. Submit a pull request


## License

This project is licensed under the MIT License 
