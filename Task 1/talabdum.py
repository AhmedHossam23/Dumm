import time
import pandas as pd
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

st.title("New Cairo Restaurants and Cafés Scraper")

def scrape_restaurants():
    # Initialize the WebDriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=service, options=options)

    restaurants = []

    try:
        # Open Google Maps
        driver.get("https://www.google.com/maps")
        st.write("Opened Google Maps")

        # Search for restaurants and cafés in New Cairo
        search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "searchboxinput")))
        st.write("Located search box")
        search_box.send_keys("restaurants and cafés in New Cairo")
        search_box.send_keys(Keys.RETURN)
        st.write("Performed search")

        time.sleep(5)  # Allow the page to load

        # Scroll down to load more results
        for _ in range(5):  # Reduced the number of scrolls for debugging
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            st.write("Scrolled down to load more results")

        # Extract data
        restaurant_elements = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[role='article']"))
        )
        st.write(f"Found {len(restaurant_elements)} restaurant elements")

        for element in restaurant_elements:
            try:
                name = element.find_element(By.CSS_SELECTOR, "h3").text
            except NoSuchElementException:
                name = "N/A"
            try:
                rating = element.find_element(By.CSS_SELECTOR, "span[aria-label*='stars']").get_attribute("aria-label")
            except NoSuchElementException:
                rating = "N/A"
            try:
                reviews_count = element.find_element(By.CSS_SELECTOR, "span[aria-label*='reviews']").text
            except NoSuchElementException:
                reviews_count = "N/A"
            try:
                location_element = element.find_element(By.CSS_SELECTOR, "span.section-result-location")
                location = location_element.text
                # Extract latitude and longitude from the URL (mock values as placeholders)
                latitude = "N/A"
                longitude = "N/A"
            except NoSuchElementException:
                location = "N/A"
                latitude = "N/A"
                longitude = "N/A"
            try:
                url = element.find_element(By.CSS_SELECTOR, "a[role='link']").get_attribute("href")
            except NoSuchElementException:
                url = "N/A"

            restaurants.append([name, rating, reviews_count, location, latitude, longitude, url])
            st.write(f"Scraped data for restaurant: {name}")

    except TimeoutException as e:
        st.warning("Timed out waiting for page elements to load. Returning the data collected so far.")
    finally:
        driver.quit()

    return pd.DataFrame(restaurants, columns=["Restaurant Name", "Star Rating", "Reviews Count", "Location", "Latitude", "Longitude", "URL"])

if st.button("Scrape Restaurants"):
    df = scrape_restaurants()
    if not df.empty:
        df.drop_duplicates(subset=["Restaurant Name", "Location"], inplace=True)
        st.write("Scraped Restaurants Data", df)
        df.to_excel("New_Cairo_Restaurants_Cleaned.xlsx", index=False)
        st.success("Data scraped and saved to New_Cairo_Restaurants_Cleaned.xlsx")
    else:
        st.warning("No data was scraped. Please check the script and try again.")
