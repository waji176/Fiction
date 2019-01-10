import time
from selenium import webdriver
from selenium.webdriver.common.alert import Alert

"""
处理confirm对话框
"""
driver = webdriver.Chrome()
driver.get('C:\\Users\\jiangwenhui\\PycharmProjects\\Fiction\\app01\\4hentai\\1.html')
# 获取confirm对话框的按钮，点击按钮，弹出confirm对话框
driver.find_element_by_xpath('''//input[@name="post_title"]''').send_keys("1234")
js = 'window.location.href="{}";'.format("https://www.baidu.com")
driver.execute_script(js)
time.sleep(1)
# 获取confirm对话框
# dig_confirm = driver.switch_to.alert
time.sleep(1)
# 打印对话框的内容
# print(dig_confirm.text)
print(Alert(driver).text)
# 点击“取消”按钮
# dig_confirm.dismiss()
Alert(driver).dismiss()
driver.execute_script(js)
# 点击“确认”按钮
# dig_confirm.accept()
Alert(driver).accept()
time.sleep(60)

driver.quit()
