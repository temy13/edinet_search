import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

options = Options()
# Chromeのパス（Stableチャネルで--headlessが使えるようになったら不要なはず）
options.binary_location = '/usr/bin/google-chrome'
# ヘッドレスモードを有効にする（次の行をコメントアウトすると画面が表示される）。
options.add_argument('--headless')
# ChromeのWebDriverオブジェクトを作成する。
driver = webdriver.Chrome(chrome_options=options)

# Googleのトップ画面を開く。
url = "http://disclosure.edinet-fsa.go.jp/E01EW/BLMainController.jsp?uji.verb=W1E63010CXW1E6A010DSPSch&uji.bean=ee.bean.parent.EECommonSearchBean&TID=W1E63011&PID=W1E63010&SESSIONKEY=1538717569222&lgKbn=2&pkbn=0&skbn=0&dskb=&dflg=0&iflg=0&preId=1&row=100&idx=0&syoruiKanriNo=&mul=E14394&fls=on&cal=1&era=H&yer=&mon=&pfs=5"
driver.get(url)
time.sleep(10)
driver.save_screenshot('search_results.png')
print(driver.title)

url = "https://www.google.co.jp/"
driver.get(url)
time.sleep(10)
driver.save_screenshot('search_results2.png')
print(driver.title)
url = "http://disclosure.edinet-fsa.go.jp/"
driver.get(url)
time.sleep(10)
driver.save_screenshot('search_results3.png')
print(driver.title) 

# driver.get('https://www.google.co.jp/')

# # タイトルに'Google'が含まれていることを確認する。
# assert 'Google' in driver.title
#
# # 検索語を入力して送信する。
# input_element = driver.find_element_by_name('q')
# input_element.send_keys('Python')
# input_element.send_keys(Keys.RETURN)
#
# time.sleep(2)  # Chromeの場合はAjaxで遷移するので、とりあえず適当に2秒待つ。
#
# # タイトルに'Python'が含まれていることを確認する。
# assert 'Python' in driver.title

# スクリーンショットを撮る。
driver.save_screenshot('search_results.png')

# 検索結果を表示する。
# for a in driver.find_elements_by_css_selector('h3 > a'):
#     print(a.text)
#     print(a.get_attribute('href'))

driver.quit()  # ブラウザーを終了する。
