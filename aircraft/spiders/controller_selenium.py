# -*- coding: utf-8 -*-

from selenium import webdriver
import traceback
import os
import time

DEBUG_MODE = False


def _init_chromium():
    chrome_options = webdriver.ChromeOptions()  # this is for Chromium
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--hide-scrollbars")
    chrome_options.add_argument("--window-size=%s" % '{},{}'.format(1024, 800))
    executable_path = '/usr/sbin/chromedriver'
    if not os.path.exists(executable_path):
        executable_path = '/usr/local/bin/chromedriver'
    # initialize webdriver, open the page and make a screenshot
    driver = webdriver.Chrome(chrome_options=chrome_options,
                              executable_path=executable_path
                              )
    return driver


if __name__ == "__main__":
    driver = _init_chromium()

    if driver:
        try:
            driver.get('https://www.controller.com/listings/aircraft/for-sale/list?SortOrder=35&scf=False&LS=1')
            time.sleep(5)

            search_results = driver.find_elements_by_xpath('//div[@class="listing-name"]/a/@href')

            for search_result in search_results:
                try:
                    driver = _init_chromium()
                    search_result = 'https://www.controller.com' + search_result
                    driver.get(search_result)
                    driver.quit()

                except:
                    print('Found no product links: {}'.format(traceback.format_exc()))
        except:
            print('Found no product links: {}'.format(traceback.format_exc()))

        if 'driver' in locals():
            driver.quit()
