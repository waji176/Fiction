from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select, WebDriverWait
import time, re, os, sys, json, requests, itertools
from bs4 import BeautifulSoup


def While_cmd(driver, cmd):
    while True:
        try:
            exec(cmd)
        except Exception as e:
            # print(e)
            time.sleep(0.5)
        else:
            break


def is_element_exist(driver, xpath):
    s = driver.find_elements_by_xpath(xpath)
    if len(s) == 0:
        print("元素未找到:%s" % xpath)
        return False
    elif len(s) == 1:
        return len(s)
    else:
        print("找到%s个元素：%s" % (len(s), xpath))
        return len(s)


def main(url):
    allparams = [[1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], ]
    driver = webdriver.Chrome("D:\\chromedriver.exe")
    driver.get(url)
    title = driver.find_element_by_xpath('''//p[@class="title"]''').text
    # with open("{}.csv".format(title), "w") as f:
    #     s1 = ''
    #     for x in range(12):
    #         option_title = driver.find_element_by_xpath('''/html/body/div[2]/form/div/div/div/div/div[2]''').text
    #         driver.find_element_by_xpath('''//div/input[1]''').click()
    #         s1 += option_title + ","
    #     f.write(s1 + '结果' + '\n')

    num = 0
    for i in eval('itertools.product' + str(tuple(allparams))):  # 1、笛卡尔积 对参数分组全排列
        num += 1
        if num < 45062: continue
        js = 'window.location.href="{}";'.format(url)
        driver.execute_script(js)
        s2 = ''
        for j in i:
            while True:
                if is_element_exist(driver, '''//div/input[{}]'''.format(j)):
                    break
            option = driver.find_element_by_xpath('''//div/input[{}]'''.format(j)).get_attribute("value")
            try:
                driver.find_element_by_xpath('''//div/input[{}]'''.format(j)).click()
            except Exception as e:
                print(e)
                time.sleep(5)
            # While_cmd(driver, """driver.find_element_by_xpath('''//div/input[{}]''').click()""".format(j))
            s2 += option + ','
        result = driver.find_element_by_xpath('''//div[@class="conclusion"]''').text
        result = result.replace("\n", '   ')
        with open("{}.csv".format(title), "a") as f:
            f.write(s2 + result + '\n')
            # break
        print("第 {} 个结果写入成功".format(num))
    time.sleep(60)


if __name__ == '__main__':
    main("http://product.astro.sina.com.cn/test/20962")
