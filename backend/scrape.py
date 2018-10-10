import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import os.path
from selenium import webdriver
# from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from glob import glob

import db
import etl


base = "https://disclosure.edinet-fsa.go.jp/E01EW/BLMainController.jsp?uji.verb=W1E63010CXW1E6A010DSPSch&uji.bean=ee.bean.parent.EECommonSearchBean&TID=W1E63011&PID=W1E63010&SESSIONKEY=1538717569222&lgKbn=2&pkbn=0&skbn=0&dskb=&dflg=0&iflg=0&preId=1&row=100&idx=0&syoruiKanriNo=&mul=%s&fls=on&cal=1&era=H&yer=&mon=&pfs=5"

# def get_soup(url):
#     resp = requests.get(url)
#     soup = BeautifulSoup(resp.text, "html.parser")
#     return soup

def get_codes():
    df = pd.read_csv(os.getcwd() + "/backend/codes.csv")
    return df


def generate_op(code):
    path = os.getcwd() + "/backend/data/%s" % code
    if not os.path.isdir(path):
        os.mkdir(path)
    options = Options()
    options.binary_location = '/usr/bin/google-chrome'
    options.add_argument('--headless')
    options.add_argument('--window-size=1280,1024')
    #chrome_options.add_argument("--disable-extensions")
    prefs = {"download.default_directory" : path}
    options.add_experimental_option("prefs",prefs)
    #chrome_options.add_argument('--ignore-certificate-errors')     # fp = webdriver.FirefoxProfile()
    # # 0:デスクトップ、1:システム規定のフォルファ、2:ユーザ定義フォルダ
    # fp.set_preference("browser.download.folderList",2)
    # # 上記で2を選択したのでファイルのダウンロード場所を指定
    # # ダウンロード完了時にダウンロードマネージャウィンドウを表示するかどうかを示す真偽値。
    # fp.set_preference("browser.download.manager.showWhenStarting",False)
    # # mimeタイプを設定
    # fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")
    return options


def download(code):
    #time.sleep(5)
    op = generate_op(code)
    # driver = webdriver.Firefox(firefox_profile=fp,firefox_binary=binary)
    driver = webdriver.Chrome(chrome_options=op)
    url = base % (code,)
    print(url)
    driver.get(url)
    driver.save_screenshot(os.getcwd() + '/screenshot1.png')
    element = WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.CLASS_NAME, "resultTable"))
    )
    driver.save_screenshot(os.getcwd() + '/screenshot2.png')
    for ele in driver.find_elements_by_xpath('//table[@class="resultTable table_cellspacing_1 table_border_1 mb_6"]//tr/td[7]//a'):
        #time.sleep(1)
        print(ele)
        ele.click()
    driver.close()


if __name__ == '__main__':
    df = get_codes()
    for index, item in df[:1].iterrows():
        code = item["code"]
        filenames = db.get_filenames(code)
        #print(filenames)
        download(code)
        for fn in glob("backend/data/%s/*.zip" % code):
            if fn in filenames:
               continue
            print(fn)
#           [{"key":str, "value":str, "ishtml": boolean }]
            ds= etl.extract(fn, code)
            db.save_items(fn, code, ds)
