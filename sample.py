from selenium import webdriver
from selenium.webdriver.chrome.options import Options

#options = Options()
#options.binary_location = '/usr/bin/google-chrome'
#options.add_argument('--headless')
options = webdriver.ChromeOptions()
options.binary_location='/usr/bin/google-chrome-stable'
options.add_argument('--headless')
options.add_argument('--start-maximized') 
options.add_argument('disable-infobars')
options.add_argument('--disable-extensions')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#options.add_argument('window-size={}x{}'.format(*self.window_size))                                                                                                                                                                                                                                                                          
self.driver = webdriver.Chrome(chrome_options=options, executable_path='/home/ubuntu/bin/chromedriver') 

print('before')#動作確認
#driver = webdriver.Chrome('/home/ubuntu/bin/chromedriver',chrome_options=options)
print('after')#動作確認
driver.get('https://www.google.co.jp/')
driver.save_screenshot('/tmp/screenshot.png')
driver.quit()
