
警报实施。

    from selenium.webdriver.common.alert import Alert
    class selenium.webdriver.common.alert.Alert(driver)
基地：对象

允许使用警报。

使用此类与警报提示进行交互。 它包含从警报提示中解除，接受，输入和获取文本的方法。

接受/取消警报提示：

    Alert(driver).accept()
    Alert(driver).dismiss()
在警报提示中输入值：

    name_prompt = Alert(driver) name_prompt.send_keys(“Willian Shakesphere”)
    name_prompt.accept()
阅读提示进行验证的文本：

    alert_text = Alert(driver).text self.assertEqual(“Do you wish to quit?”, alert_text)
    
accept()
接受可用的警报。
用法:: Alert(driver).accept() # 确认警报对话框。

authenticate(username, password)
将用户名/密码发送到Authenticated对话框（与Basic HTTP Auth一样）。 隐含'点击确定'

用法:: driver.switch_to.alert.authenticate(‘cheese’, ‘secretGouda’)

Args:	-username: 要在对话框的用户名部分中设置的字符串 -password: 要在对话框的密码部分中设置的字符串
dismiss()
驳回可用的警报。

send_keys(keysToSend)
将密钥发送到警报。

Args:
keysToSend: 要发送到Alert的文本。
text
获取Alert的文本.