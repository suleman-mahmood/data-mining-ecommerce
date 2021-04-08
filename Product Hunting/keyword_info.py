import undetected_chromedriver as uc
import numpy as np
import copy
import queue
import time
import util
import csv
import threading

from selenium import webdriver
from selenium.webdriver.chrome.options import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType

start_time = time.time()

"""Constants """

# 3 sec wait time
WAIT_TIME = 5
# Decides whether the keyword is too broad or not
MIN_RELEVANCY_COUNT = 4
# The number of maximum concurrent browsers/threads to run at a time
MAX_CONCURRENT_BROWSERS = 10


"""Main function that opens browser and gets the info for each keyword"""


def get_info_from_keyword(keyword, keywords_info_queue, thread_completed):

    browser = free_browsers.get()

    # Format the keyword into the url
    keyword_query = "https://www.daraz.pk/catalog/?q=" + \
        "+".join(keyword.split())

    browser.get(keyword_query)

    reviews_count = []
    listed_price = []

    for i in range(1, 11):
        try:
            reviews_count.append(browser.find_element_by_css_selector(
                "div.c2prKC:nth-child(%d) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(5) > div:nth-child(1) > span:nth-child(6)" % i))
        except:
            reviews_count.append("not exist")

        try:
            listed_price.append(browser.find_element_by_css_selector(
                "div.c2prKC:nth-child(%d) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(3) > span:nth-child(1)" % i))
        except:
            listed_price.append("not exist")

    # check whether the new keyword is relevant or not
    relevant_list_count = 0

    for i in range(1, 11):
        try:
            text_title = browser.find_element_by_css_selector(
                "div.c2prKC:nth-child(%d) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > a:nth-child(1)" % i)
        except:

            # Exit functions becuase there are not enough results for your search keyword
            print("Quitting thread with too few or no results:", keyword)

            time.sleep(WAIT_TIME)
            free_browsers.put(browser)

            keyword_info = []
            keyword_info.append(keyword)

            for i in range(32):
                keyword_info.append(0)

            keywords_info_queue.put(keyword_info)
            temp = thread_completed.get()

            return

        if keyword in text_title.text:
            relevant_list_count += 1

    if relevant_list_count < MIN_RELEVANCY_COUNT:

        # The keyword is broad and irrelevant to search results so exit immediately
        print("Quitting thread with broad keyword:", keyword)

        time.sleep(WAIT_TIME)
        free_browsers.put(browser)

        keyword_info = []
        keyword_info.append(keyword)

        for i in range(32):
            keyword_info.append(0)

        keywords_info_queue.put(keyword_info)
        temp = thread_completed.get()

        return

    reviews_count_int = []
    listed_price_int = []

    for i in range(10):
        try:
            reviews_count_int.append(int(reviews_count[i].text[1:-1]))
        except:
            reviews_count_int.append(0)

        try:
            listed_price_int.append(listed_price[i].text.split()[1])
        except:
            listed_price_int.append(0)

    reviews_greater_fifty = 0

    for review in reviews_count_int:
        if review >= 50:
            reviews_greater_fifty += 1

    recent_reviews = []

    for i in range(1, 11):

        # Go into the next product listing
        curr_link = browser.find_element_by_css_selector(
            "div.c2prKC:nth-child(%d) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > a:nth-child(1)" % i)
        curr_link.click()
        time.sleep(WAIT_TIME)

        # Click on reviews button
        try:
            sort_btn = browser.find_element_by_css_selector(
                "div.oper:nth-child(3)")
            sort_btn.click()
            time.sleep(WAIT_TIME)
        except:
            recent_reviews.append(0)

            print("Recent Reviews:", 0)

            browser.back()
            time.sleep(WAIT_TIME)
            continue

        # Sort it by recent
        recent_btn = browser.find_element_by_css_selector(
            "li.next-menu-item:nth-child(2)")
        recent_btn.click()
        time.sleep(WAIT_TIME)

        count_recent_week_reviews = 0
        recent_reviews_ended = False

        while not recent_reviews_ended:

            for i in range(1, 6):
                review_date = ""
                try:
                    review_date = browser.find_element_by_css_selector(
                        "div.item:nth-child(%d) > div:nth-child(1) > span:nth-child(2)" % i)
                except:
                    review_date = browser.find_element_by_css_selector("a")

                if util.is_recent(review_date.text):
                    count_recent_week_reviews += 1
                else:
                    recent_reviews_ended = True
                    print("Breaking on:", review_date.text)
                    break

            try:
                next_btn = browser.find_element_by_css_selector(
                    "div.next-pagination:nth-child(2) > div:nth-child(1) > button:nth-child(3)")
                is_disable = next_btn.get_attribute("disabled")
                next_btn.click()

                if is_disable == "true":
                    recent_reviews_ended = True
            except:
                recent_reviews_ended = True

            time.sleep(WAIT_TIME)

        recent_reviews.append(count_recent_week_reviews)

        browser.back()
        time.sleep(WAIT_TIME)

    fbd_exists = True

    try:
        fbd_btn = browser.find_element_by_css_selector(
            "div.c2cYd1:nth-child(3) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > label:nth-child(3) > span:nth-child(1) > input:nth-child(1)")
        fbd_btn.click()
        time.sleep(WAIT_TIME)

        pk_btn = browser.find_element_by_css_selector(
            "div.c2cYd1:nth-child(4) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > label:nth-child(1) > span:nth-child(1) > input:nth-child(1)")
        pk_btn.click()
        time.sleep(WAIT_TIME)
    except:
        fbd_exists = False

    fbd_listings = 0
    i = 1

    while fbd_exists:
        try:
            text_title = browser.find_element_by_css_selector(
                "div.c2prKC:nth-child(%d) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > a:nth-child(1)" % i)
        except:
            break

        if keyword in text_title.text:
            fbd_listings += 1

        i += 1

    print("Quitting thread with keyword:", keyword)
    time.sleep(WAIT_TIME)
    free_browsers.put(browser)

    keyword_info = []
    keyword_info.append(keyword)
    keyword_info.append(fbd_listings)
    keyword_info.append(reviews_greater_fifty)
    keyword_info += reviews_count_int
    keyword_info += recent_reviews
    keyword_info += listed_price_int

    keywords_info_queue.put(keyword_info)
    temp = thread_completed.get()


"""Get Proxy List"""

PROXIES = []

co = webdriver.ChromeOptions()
co.add_argument("log-level=3")
co.add_argument("--headless")

driver = webdriver.Chrome(chrome_options=co)
driver.get("https://free-proxy-list.net/")

while len(PROXIES) < MAX_CONCURRENT_BROWSERS:

    proxies = driver.find_elements_by_css_selector("tr[role='row']")
    for p in proxies:
        result = p.text.split(" ")

        if result[-1] == "yes":
            PROXIES.append(result[0]+":"+result[1])

    driver.find_element_by_css_selector(
        "#proxylisttable_next > a:nth-child(1)").click()

    time.sleep(1)

driver.close()

"""Initialize Browsers and store them in browsers_list"""

browsers_list = []

if len(PROXIES) < MAX_CONCURRENT_BROWSERS:
    print("Number of proxies are less than the browser!")
    print("Exiting!!")

for i in range(MAX_CONCURRENT_BROWSERS):
    curr_proxy = PROXIES[i]

    options = uc.ChromeOptions()

    proxy = Proxy()
    proxy.proxyType = ProxyType.MANUAL
    proxy.autodetect = False
    proxy.httpProxy = proxy.sslProxy = proxy.socksProxy = curr_proxy
    options.Proxy = proxy
    options.add_argument("ignore-certificate-errors")

    curr_browser = uc.Chrome(chrome_options=options)

    browsers_list.append(curr_browser)

"""Initialize the free browsers queue"""

free_browsers = queue.Queue()

for brow in browsers_list:
    free_browsers.put(brow)

"""Read keywords file"""

data_file = open("keywords.csv")
file_reader = csv.reader(data_file)
file_data = list(file_reader)

# copy the first column of the file (which contains keywords)
keywords = np.array(file_data)
keywords = copy.deepcopy(keywords[:, 0])

"""Do threading and gain info for each keyword"""

keywords_info_queue = queue.Queue()
thread_completed = queue.Queue()

for k in keywords:

    # Create a thread for this keyword and the save the info
    thread_completed.put(k)
    curr_thread = threading.Thread(
        target=get_info_from_keyword, args=(k, keywords_info_queue, thread_completed,))
    curr_thread.start()

    # If there are more than max threads running then wait for them to complete
    while thread_completed.qsize() >= MAX_CONCURRENT_BROWSERS:
        time.sleep(WAIT_TIME)

while not thread_completed.empty():
    time.sleep(WAIT_TIME)


"""Close all the browsers"""

while not free_browsers.empty():
    temp = free_browsers.get()
    temp.close()

"""Write back to keywords file"""

output_file = open("keywords-info.csv", "w", newline="")
output_writer = csv.writer(output_file)

# Execution is completed, now extract the lists from the queue
while not keywords_info_queue.empty():
    temp = keywords_info_queue.get()
    output_writer.writerow(temp)

output_file.close()

"""Calculate time elapsed"""

end_time = time.time()
time_elapsed = (end_time - start_time) / 60

print("Time elapsed:", time_elapsed, "minutes!")
