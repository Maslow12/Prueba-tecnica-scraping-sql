import os
import random
import time
import urllib3

import requests

from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor, as_completed

from logger_ import logger
from utils import execute_sql_query, get_fresh_proxies, json_to_excel, json_to_sqlite, time_to_minutes
from bs4 import BeautifulSoup

from settings import ScraperSettings

urllib3.disable_warnings()

settings = ScraperSettings()

def fetch_data(url:str, tries:int)->str:
    session = requests.Session()
    session.headers.update(settings.headers)
    for i in range(tries):
        proxy = get_fresh_proxies()
        proxy = proxy if proxy else get_fresh_proxies()
        logger.info(
            "Try with the proxy {0}. Proxy number {1}".format(str(proxy), i)
        )
        try:
            response = session.get(url,
                proxies=proxy,
                timeout=10,
                cookies={
                  'session-id': str(random.randint(100000, 999999))
                }, 
                verify=False
            )
            if response.status_code == 200 and response.text != "" and "script" in response.text:
                #logger.debug(
                #    "Page {0} extracted with the try {1} and proxy {2}".format(url, i, str(proxy))
                #)
                return response.text
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            pass
    return None

def find_in_single_page(url: str, prefix: str, tries:int=10) -> dict:
    page_url = url + prefix
    html = fetch_data(page_url, tries)
    logger.info(
        "Finish to extract information for {0}".format(page_url)
    )
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        metascore = soup.find("span", class_="metacritic-score-box")
        elements = soup.find_all(
            "ul", class_="ipc-inline-list ipc-inline-list--show-dividers ipc-inline-list--inline ipc-metadata-list-item__list-content baseAlt")
        if elements and len(elements) > 0:
            casts = elements[-1]
            names = ",".join([cast.text for cast in casts])
            names = names if names and names != "," else ""
            return {
                "cast": names,
                "metascore": metascore.text if metascore else "Not find metascore"
            }
        else:
            logger.error(
                "Cannot extract information for the page {0}".format(url)
            )
            return {
                "cast": "Not find cast",
                "metascore": "Not find metascore"
            }
    logger.error(
        "Not information for the page, set more tries {0}".format(page_url)
    )
    return {
        "cast": "Not find cast",
        "metascore": "Not find metascore"
    }
    
def scrape_imdb(prefix:str, tries:int)->dict:
    host = settings.host
    url = host + prefix
    html = fetch_data(url, tries)
    single_movie_page = host + "es"
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        list_elements = soup.find_all("li", class_="ipc-metadata-list-summary-item")
        json_data = []
        for element in list_elements:
            element_div = element.find("div", class_="ipc-metadata-list-summary-item__c").find("div")
            prefix = element_div.find("a", class_="ipc-title-link-wrapper")["href"]
            extra_data = find_in_single_page(url=single_movie_page, prefix=prefix, tries=tries)
            duration = time_to_minutes(element_div.find_all("span", class_="cli-title-metadata-item")[1].text)
            movie_data = {
                "title": element_div.find("h3", class_="ipc-title__text").text,
                "year": element_div.find_all("span", class_="cli-title-metadata-item")[0].text.split()[0],
                "duration": duration,
                "rating": element_div.find("span", class_="ipc-rating-star").text.split()[0],
            }
            movie_data.update(extra_data)
            json_data.append(movie_data)
        return json_data
    logger.error(
        "Not information for the page, set more tries {0}".format(url)
    )
    return {}

def find_information(element:any)->dict:
    host = settings.host
    single_movie_page = host + "es"
    element_div = element.find(
        "div", class_="ipc-metadata-list-summary-item__c").find("div")
    prefix = element_div.find(
        "a", class_="ipc-title-link-wrapper")["href"]
    extra_data = find_in_single_page(url=single_movie_page, prefix=prefix, tries=settings.tries)
    duration = time_to_minutes(element_div.find_all(
        "span", class_="cli-title-metadata-item")[1].text)
    movie_data = {
        "title": element_div.find("h3", class_="ipc-title__text").text,
        "year": element_div.find_all("span", class_="cli-title-metadata-item")[0].text.split()[0],
        "duration": duration,
        "rating": element_div.find("span", class_="ipc-rating-star").text.split()[0],
    }
    movie_data.update(extra_data)
    return movie_data


def scrape_imdb_concurrent(prefix: str, tries: int) -> dict:
    host = settings.host
    url = host + prefix
    html = fetch_data(url, tries)
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        list_elements = soup.find_all(
            "li", class_="ipc-metadata-list-summary-item")
        json_data = []
        with ThreadPoolExecutor(max_workers=settings.max_workers) as executor:
            future_to_url = {
                executor.submit(find_information, element): element
                for element in list_elements
            }
            for i, future in enumerate(as_completed(future_to_url)):
                data = future_to_url[future]
                try:
                    data = future.result()
                    if data:
                        logger.info(f"Successfully fetched {i}")
                        json_data.append(data)
                except Exception as e:
                    pass
        return json_data
    logger.error(
        "Not information for the page, set more tries {0}".format(url)
    )
    return {}

def get_questions(db_name: str, json_data: dict)->None:
    db_name = json_to_sqlite(json_data, 'result.db', 'movies')
    better_movies_sql = "SELECT * FROM movies ORDER BY rating DESC LIMIT 5"
    more_than_150_sql = "SELECT * FROM movies WHERE duration > 150"
    sql = "SELECT * FROM movies"

    # EXPORT CSV
    current_dir = os.getcwd()
    dir_path = "results"
    path = os.path.join(current_dir, dir_path)
    if not os.path.exists(path=path):
        os.makedirs(path)

    better_movies = execute_sql_query(
        sql_query=better_movies_sql, db_path=db_name)
    more_than_150 = execute_sql_query(
        sql_query=more_than_150_sql, db_path=db_name)
    all_movies = execute_sql_query(sql_query=sql, db_path=db_name)

    for json_data_, name in zip([better_movies, more_than_150, all_movies], ["better_movies.xlsx", "more_than_150.xlsx", "movies.xlsx"]):
        json_to_excel(json_data=json_data_, file_name=os.path.join(path, name))
        
def manage(sort:str)->None:
    data = scrape_imdb_concurrent(prefix=f"chart/top/{sort}", tries=settings.tries)
    return data

def multiprocess_manage(sorts:list[str])->None:
    db_name = 'result.db'
    json_ = []
    with Pool(processes=2) as pool:
        results = pool.map(manage, sorts)
    for result in results:
        json_.extend(result)
    get_questions(db_name=db_name, json_data=json_)
