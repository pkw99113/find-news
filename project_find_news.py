import requests
from lxml import html
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time

URL = 'https://search.naver.com/search.naver?where=news&ie=utf8&sm=nws_hty&query=사이버보안'

def fetch_news(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.get(url)
    
    time.sleep(3)  # Wait for the page to load
    
    page_content = driver.page_source
    driver.quit()
    return page_content

def parse_articles(page_content):
    tree = html.fromstring(page_content)

    title_xpath = '/html/body/div[1]/div[5]/div[5]/div[1]/div[1]/div[1]/h1'
    articles_xpath = '/html/body/div[3]/div[2]/div[1]/div[1]/section/div[1]/div[2]/ul/li[3]/div[1]/div/div[2]'
    journalist_link_xpath = '/html/body/div/div[3]/div/div[1]/div[6]/div[1]/a'
    media_xpath = '/html/body/div/div[1]/div[1]/div/h1/a/img'

    articles = tree.xpath(articles_xpath)

    parsed_data = []

    for article in articles:
        title_element = tree.xpath(title_xpath)
        title = title_element[0].text if title_element else 'No Title'

        # Extract the journalist link
        journalist_link_element = article.xpath(journalist_link_xpath)
        journalist_name, journalist_email = 'No Journalist', 'No Email'
        if journalist_link_element:
            journalist_link = journalist_link_element[0].get('href')
            journalist_name, journalist_email = fetch_journalist_details(journalist_link)

        media_elements = article.xpath(media_xpath)
        media_name = media_elements[0].get('alt') if media_elements else 'No Media'

        parsed_data.append({
            'Title': title,
            'Media Name': media_name,
            'Journalist Name': journalist_name,
            'Journalist Email': journalist_email
        })

    return parsed_data

def fetch_journalist_details(link):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.get(link)
    
    time.sleep(3)  # Wait for the page to load
    
    journalist_name = driver.find_element(By.XPATH, '/html/body/div/div[3]/div/div[1]/div[6]/div[1]/a/span').text
    journalist_email = 'No Email'  # Modify if there's an actual way to get the email
    
    driver.quit()
    return journalist_name, journalist_email

def main():
    page_content = fetch_news(URL)
    if page_content:
        articles = parse_articles(page_content)
        if articles:
            df = pd.DataFrame(articles)
            df.to_csv('cyber_security_news.csv', index=False)
            print("News articles saved to cyber_security_news.csv")
        else:
            print("No articles found")
    else:
        print("Failed to fetch news articles")

if __name__ == '__main__':
    main()
