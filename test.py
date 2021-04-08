import selenium
import undetected_chromedriver as uc
import time

browser = uc.Chrome()
browser.get("https://www.daraz.pk/products/tcl-remote-for-s6500-lcdled-tv-with-buttonfree-cell-i125954840-s1284064285.html?spm=a2a0e.searchlistcategory.list.12.2d767a40k5w4SF&search=1")

some_flag = False

while not some_flag:

    next_btn = browser.find_element_by_css_selector(
        "div.next-pagination:nth-child(2) > div:nth-child(1) > button:nth-child(3)")
    is_disable = next_btn.get_attribute("disabled")
    next_btn.click()

    print("Clicked on btn, state:", is_disable)

    time.sleep(2)

    if is_disable == "true":
        break
