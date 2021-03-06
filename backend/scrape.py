import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import os.path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from glob import glob
import traceback
import db
import es
import etl
import meta
base = "https://disclosure.edinet-fsa.go.jp/E01EW/BLMainController.jsp?uji.verb=W1E63010CXW1E6A010DSPSch&uji.bean=ee.bean.parent.EECommonSearchBean&TID=W1E63011&PID=W1E63010&SESSIONKEY=1538717569222&lgKbn=2&pkbn=0&skbn=0&dskb=&dflg=0&iflg=0&preId=1&row=100&idx=0&syoruiKanriNo=&mul=%s&fls=on&cal=1&era=H&yer=&mon=&pfs=5"

# def get_soup(url):
#     resp = requests.get(url)
#     soup = BeautifulSoup(resp.text, "html.parser")
#     return soup

def get_codes():
    df = pd.read_csv(os.getcwd() + "/backend/codes.csv")
    return df


def generate_fp(code):
    path = os.getcwd() + "/backend/data/%s" % code
    if not os.path.isdir(path):
        os.mkdir(path)
    fp = webdriver.FirefoxProfile()
    fp.accept_untrusted_certs = True
    # 0:デスクトップ、1:システム規定のフォルファ、2:ユーザ定義フォルダ
    fp.set_preference("browser.download.folderList",2)
    # 上記で2を選択したのでファイルのダウンロード場所を指定

    fp.set_preference("browser.download.dir", path)
    # ダウンロード完了時にダウンロードマネージャウィンドウを表示するかどうかを示す真偽値。
    fp.set_preference("browser.download.manager.showWhenStarting",False)
    # mimeタイプを設定
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")
    return fp


def download(code):
    time.sleep(5)
    fp = generate_fp(code)
    options = Options()
    options.set_headless(headless=True)
    driver = webdriver.Firefox(firefox_profile=fp,firefox_options=options)
    url = base % (code,)
    driver.get(url)
    #base_path = '//table[@class="resultTable table_cellspacing_1 table_border_1 mb_6"]//tr'
    #for ele in driver.find_elements_by_xpath(base_path):
    #    print(ele.find_element_by_xpath('/td[1]').getText())
    # サイトの形式上click->js callゆえ名前をつけることが難しい
    xpath = '//table[@class="resultTable table_cellspacing_1 table_border_1 mb_6"]//tr/td[7]//a'
    for ele in driver.find_elements_by_xpath(xpath):
        time.sleep(1)
        ele.click()
    driver.close()
    driver.quit()


if __name__ == '__main__':
    print("start")
    df = get_codes()
    for index, item in df.iterrows():
        code = item["code"]
        print(code)
        ###filenames = db.get_filenames(code)
        download(code)
        sys.exit(0)
        for fn in glob("backend/data/%s/*.zip" % code):
        ###for fn in filenames:
            try:  
                ###if fn in filenames:
                ###   continue
                items, values= etl.extract(fn, code)
                db.save_items(fn, code, items)
                db.save_values(fn, code, values)
                meta.save_meta(fn)
                es.insert_to_es(fn)
            except:
                print(traceback.format_exc())
    print("done")
