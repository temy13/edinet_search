from selenium import webdriver
#ブラウザを指定して起動
browser = webdriver.PhantomJS()
#Googleのサイトにアクセス
browser.get('https://www.google.com/')
#この下のbrowser.quitまでの間にいろいろな処理を書いていく
browser.save_screenshot('ss.png')
#ブラウザを終了させる
browser.quit()
