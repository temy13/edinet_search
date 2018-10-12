from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1280,1024')
driver = webdriver.Chrome(chrome_options=options)
driver.get('https://disclosure.edinet-fsa.go.jp/W00Z0020.html')
print(driver.title) #=> Google
driver.save_screenshot('test.png')
