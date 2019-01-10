from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time, re, os, sys, json
from concurrent.futures import ThreadPoolExecutor
import ruku


def done(request, *args, **kwargs):  #
    result = request.result()
    # print(result, args, kwargs)


def get_info(url):
    driver = webdriver.Chrome()
    driver.get(url)
    try:
        driver.find_element_by_xpath('''//input[@name="email"]''').send_keys('邮箱@qq.com')
        driver.find_element_by_xpath('''//input[@name="password"]''').send_keys('密码')
        driver.find_element_by_xpath('''//button[@type="submit"]''').click()
    except Exception:
        pass

    driver.find_element_by_xpath(
        '''//*[@id="zplusframe"]/div[3]/div/div[2]/div[3]/div[2]/div[2]/ul/li/div[2]/footer/div/span[1]''').click()

    photo = driver.find_element_by_xpath('''//figure[@class="_1Ai3K7V _1g_rgDt"]/img''').get_attribute('src')  # 头像
    print(photo)
    # driver.close()


if __name__ == "__main__":
    get_info("https://www.zoosk.com/personals/search?page=1&view=slideshow")
