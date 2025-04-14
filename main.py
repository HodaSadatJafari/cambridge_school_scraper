import json
import random
import time

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

BASE_URL = (
    "https://www.cambridgeinternational.org/why-choose-us/find-a-cambridge-school/"
)


def scrape_cambridge_schools():
    # Set up Chrome options
    chrome_options = Options()
    # Remove headless mode to debug
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.page_load_strategy = "normal"

    # Initialize data storage
    all_schools = []

    # Keep track of progress for resuming
    progress_file = "scraping_progress.json"
    try:
        with open(progress_file, "r") as f:
            progress = json.load(f)
            completed_pairs = progress.get("completed_pairs", [])
            print(
                f"Loaded progress: {len(completed_pairs)} country-city pairs already processed"
            )
    except (FileNotFoundError, json.JSONDecodeError):
        completed_pairs = []

    try:
        # Initialize the driver
        driver_path = (
            "/usr/bin/chromedriver"  # Specify the path to chromedriver on Ubuntu
        )

        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(180)

        # Get the main page
        driver.get(BASE_URL)

        # Wait for the page to load
        wait = WebDriverWait(driver, 3)

        # Accept cookies if the banner appears
        try:
            accept_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.accept"))
            )
            accept_button.click()
            print("Accepted cookies")
        except Exception:
            try:
                accept_button = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(text(), 'Accept')]")
                    )
                )
                accept_button.click()
                print("Accepted cookies")
            except Exception:
                print("No cookie banner found or could not click accept")

        # Wait for the spinner to disappear
        try:
            WebDriverWait(driver, 3).until_not(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".spinner"))
            )
            print("Page loaded, spinner disappeared")
        except Exception:
            print("No spinner found or timeout waiting for spinner to disappear")

        # Wait for country dropdown to be available
        try:
            country_select = wait.until(
                EC.presence_of_element_located((By.ID, "SelectedRegionId"))
            )
            country_dropdown = Select(country_select)
            print("Found country dropdown")
        except Exception:
            # Try alternative selector
            country_select = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "select.location-select"))
            )
            country_dropdown = Select(country_select)
            print("Found country dropdown using alternative selector")

        # Get all country options (skip the first one which is the placeholder)
        country_options = [
            option
            for option in country_dropdown.options
            if option.get_attribute("value")
        ]
        print(f"Found {len(country_options)} countries")

        # Loop through each country
        for country_option in country_options:
            country_name = country_option.text
            country_value = country_option.get_attribute("value")

            if country_name != "Select a location":
                # Try to select the country
                try:
                    # Re-find elements to avoid stale element references
                    country_select = wait.until(
                        EC.presence_of_element_located((By.ID, "SelectedRegionId"))
                    )
                    country_dropdown = Select(country_select)

                    print(f"Processing country: {country_name}")
                    country_dropdown.select_by_value(country_value)

                    # Find the city dropdown with more robust waiting
                    try:
                        city_select = wait.until(
                            EC.presence_of_element_located((By.ID, "SelectedCity"))
                        )
                        city_dropdown = Select(city_select)
                        print(f"Found city dropdown for {country_name}")
                    except Exception:
                        print(
                            f"No city dropdown found for {country_name}, proceeding with country only"
                        )
                        city_dropdown = None

                    # Get all city options if city dropdown exists
                    if city_dropdown:
                        city_options = [
                            option for option in city_dropdown.options if option.text
                        ]
                        print(f"Found {len(city_options)} cities for {country_name}")
                    else:
                        city_options = []

                    if not city_options:
                        # If no cities, just search with the country
                        country_city_pair = f"{country_name}||"
                        if country_city_pair in completed_pairs:
                            print(
                                f"  Skipping already processed: {country_name} (no city)"
                            )

                        try:
                            search_button = wait.until(
                                EC.element_to_be_clickable((By.ID, "search"))
                            )
                        except Exception:
                            print("Coudn't fine the search button!")

                        search_button.click()
                        print(f"Clicked search for {country_name}")

                        # Wait for results to load
                        time.sleep(random.uniform(5, 8))

                        # Extract school data
                        schools = extract_school_data(driver, wait, country_name, "")
                        all_schools.extend(schools)

                        # Save progress
                        completed_pairs.append(country_city_pair)
                        save_progress(progress_file, completed_pairs, all_schools)

                    else:
                        # Loop through each city for the country
                        for city_option in city_options:
                            city_name = city_option.text
                            city_value = city_option.get_attribute("value")

                            if city_value != "Select a city":
                                # Check if this country-city pair has already been processed
                                country_city_pair = f"{country_name}||{city_name}"
                                if country_city_pair in completed_pairs:
                                    print(
                                        f"  Skipping already processed: {country_name} - {city_name}"
                                    )
                                    continue

                                print(f"  Processing city: {city_name}")

                                try:
                                    # Re-find elements to avoid stale element references
                                    country_select = wait.until(
                                        EC.presence_of_element_located(
                                            (By.ID, "SelectedRegionId")
                                        )
                                    )
                                    country_dropdown = Select(country_select)
                                    country_dropdown.select_by_value(country_value)

                                    city_select = wait.until(
                                        EC.presence_of_element_located(
                                            (By.ID, "SelectedCity")
                                        )
                                    )
                                    city_dropdown = Select(city_select)
                                    city_dropdown.select_by_value(city_value)
                                    time.sleep(2)

                                    # Click search
                                    search_button = wait.until(
                                        EC.element_to_be_clickable((By.ID, "search"))
                                    )

                                    search_button.click()
                                    print(
                                        f"Clicked search for {country_name} - {city_name}"
                                    )

                                    # Wait for results to load
                                    time.sleep(random.uniform(5, 8))

                                    # Extract school data
                                    schools = extract_school_data(
                                        driver, wait, country_name, city_name
                                    )
                                    all_schools.extend(schools)

                                    # Save progress
                                    completed_pairs.append(country_city_pair)
                                    save_progress(
                                        progress_file, completed_pairs, all_schools
                                    )

                                except Exception as e:
                                    print(
                                        f"Error processing {country_name} - {city_name}: {str(e)}"
                                    )
                except Exception as e:
                    print(f"Error processing country {country_name}: {str(e)}")
                    # Try to recover by refreshing the page
                    try:
                        driver.get(BASE_URL)
                        time.sleep(random.uniform(5, 10))
                    except Exception:
                        pass
                    continue

    except Exception as e:
        print(f"Critical error: {str(e)}")

    finally:
        try:
            driver.quit()
        except Exception:
            pass

        # Save the final data
        save_data(all_schools)

        print(f"Scraped {len(all_schools)} schools successfully.")
        return all_schools


def extract_school_data(driver, wait, country, city):
    schools = []

    try:

        print(f"    Processing {city if city else country}")

        # Wait for the page to load completely
        time.sleep(5)

        # Check if there are any results
        no_results_elements = driver.find_elements(By.CSS_SELECTOR, ".no-results")
        if no_results_elements:
            print(f"    No schools found in {city}, {country}")
            return schools

        # Wait for school cards to load
        try:
            tbody_element = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#facs-result-block tbody")
                )
            )
        except TimeoutException:
            print(f"    No school cards for {city}, {country}")
            # Take a screenshot for debugging
            driver.save_screenshot(f"debug_{country}_{city}.png")

        if not tbody_element:
            print(f"    No school for {city}, {country}")
            # Take a screenshot for debugging
            driver.save_screenshot(f"debug_{country}_{city}.png")

        row_elements = tbody_element.find_elements(By.TAG_NAME, "tr")

        for row_element in row_elements:
            school_data = {
                "country": country,
                "city": city,
                "center": "",
                "private_candidates_accepted": "",
            }

            cell_elements = row_element.find_elements(By.TAG_NAME, "td")

            school_data["center"] = cell_elements[0].text.strip()
            try:
                school_data["private_candidates_accepted"] = cell_elements[
                    2
                ].text.strip()
            except Exception:
                pass

            schools.append(school_data)

    except Exception as e:
        print(f"Error extracting school data for {city}, {country}: {str(e)}")
        # Take a screenshot for debugging
        driver.save_screenshot(f"error_{country}_{city}.png")

    return schools


def save_progress(progress_file, completed_pairs, all_schools):
    # Save progress
    with open(progress_file, "w") as f:
        json.dump({"completed_pairs": completed_pairs}, f, indent=4)

    # Save current data snapshot
    save_data(all_schools, suffix="_partial")


def save_data(all_schools, suffix=""):
    # Save the data
    df = pd.DataFrame(all_schools)
    df.to_csv(f"cambridge_schools{suffix}.csv", index=False)
    with open(f"cambridge_schools{suffix}.json", "w") as f:
        json.dump(all_schools, f, indent=4)


if __name__ == "__main__":
    scrape_cambridge_schools()
