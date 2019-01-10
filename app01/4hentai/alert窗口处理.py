import time
from selenium import webdriver

"""
处理alert弹窗
"""
driver = webdriver.Chrome()
driver.get('C:\\Users\\jiangwenhui\\PycharmProjects\\Fiction\\app01\\4hentai\\alert.html')
time.sleep(1)
# 获取alert对话框的按钮，点击按钮，弹出alert对话框
driver.find_element_by_id('alert').click()
time.sleep(1)
# 获取alert对话框
dig_alert = driver.switch_to.alert
time.sleep(1)
# 打印警告对话框内容
print(dig_alert.text)
# alert对话框属于警告对话框，我们这里只能接受弹窗
dig_alert.accept()
time.sleep(1)

driver.quit()
