from selenium import webdriver
from selenium.webdriver.firefox.options import Options

profile = webdriver.FirefoxProfile()
profile.accept_untrusted_certs = True
options = Options()
options.set_headless(headless=True)

driver = webdriver.Firefox(firefox_profile=profile,firefox_options=options)
driver.get("https://disclosure.edinet-fsa.go.jp/E01EW/BLMainController.jsp?uji.verb=W1E63010CXW1E6A010DSPSch&uji.bean=ee.bean.parent.EECommonSearchBean&TID=W1E63011&PID=W1E63010&SESSIONKEY=1538717569222&lgKbn=2&pkbn=0&skbn=0&dskb=&dflg=0&iflg=0&preId=1&row=100&idx=0&syoruiKanriNo=&mul=E14394&fls=on&cal=1&era=H&yer=&mon=&pfs=5")

driver.save_screenshot("edifo.png")
driver.close()
