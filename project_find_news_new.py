from selenium  import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from datetime import datetime, timedelta

driver = webdriver.Chrome()

driver.get('https://search.naver.com/search.naver?where=news&query=%EC%82%AC%EC%9D%B4%EB%B2%84%EB%B3%B4%EC%95%88&sm=tab_opt&sort=1&photo=0&field=0&pd=13&ds=&de=&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Add%2Cp%3Aall&is_sug_officeid=0&office_category=0&service_area=0')

# three_months_ago = (datetime.now() - timedelta(days = 90)).strftime('%Y-%m-%d')

def collect_articles(driver):
    articles = []

    while True:
        try:
            #news content to be present in the DOM
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "news_area")]'))
            )

            print("News items found")

            news_items = driver.find_elements(By.XPATH, '//div[contains(@class, "news_area")]')

            for item in news_items:
                try:
                    media_element = item.find_element(By.CLASS_NAME, 'info.press')
                    media_name = media_element.text
                    print(f'Media Name: {media_name}')

                    title_element = item.find_element(By.CLASS_NAME, "news_tit")
                    title = title_element.get_attribute('title')

                    print(f'Found the title: {title}')


                    initial_window_handles = driver.window_handles
                    #print(f'initial window handles: {initial_window_handles}')

                    item.find_element(By.CLASS_NAME, "news_tit").click()
                    time.sleep(1)


                    driver.switch_to.window(driver.window_handles[1])
                    print("Switched to new tab")



                    # WebDriverWait(driver, 10).until(
                    #     lambda driver: len(driver.window_handles) > len(initial_window_handles)
                    # )

                    # #print("New tab opened")

                    # driver.switch_to.window(driver.window_handles[-1]) #focus on the new popup 

                    articles.append({
                        'media_name': media_name,
                        'title': title,
                    })

                    
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    print("Closed new tab and switched back to original window")

                except Exception as e:
                    print(f'Error process itme:{e}')
                    if len(driver.window_handles) > len(initial_window_handles):
                        driver.close()
                        driver.switch_to.window(initial_window_handles[0])

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)


        except Exception as e:
            print(f'Error in main loop: {e}')
            break

    return articles
            

articles = collect_articles(driver)
df = pd.DataFrame(articles)
df.to_csv('naver_news.csv', index = False)
