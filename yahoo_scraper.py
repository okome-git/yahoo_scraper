#!/usr/bin/env python
# coding: utf-8

from time import sleep
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from tqdm import tqdm
from PIL import Image
import io
from urllib.request import urlopen
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--word',  help='search word')
parser.add_argument('--word-2',  help='additional search word')
parser.add_argument('--word-3',  help='additional search word')
parser.add_argument('--num',  help='number of download images')
parser.add_argument("--save-dir", default="./images/", help="savedir")
args = parser.parse_args()
#print("serch word = " + args.word + " " + args.word_2 + " " + args.word_3)


if args.word_2 == None and args.word_3 == None:
    print("serch word = ",args.word)
    word = args.word
    save_dir = args.save_dir + word  # スクレイピングした画像を保存するディレクトリパス
    print("save directry = " + save_dir)

elif args.word_3 == None:
    print("serch word = ",args.word, args.word_2)
    word = args.word + "_" + args.word_2
    save_dir = args.save_dir + word
    print("save directry = " + save_dir)

else:
    print("serch word = ",args.word, args.word_2,  args.word_3)
    word = args.word + "_" + args.word_2 + "_" + args.word_3
    save_dir = args.save_dir + word 
    print("save directry = " + save_dir)
    
num = int(args.num) + 1

# ディレクトリが存在しなければ作成する
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# options.add_argument('--start-maximized')
#options.add_argument('--start-fullscreen')
#options.add_argument('--disable-plugins')
#options.add_argument('--disable-extensions')
driver = webdriver.Chrome("./chromedriver.exe", options=options)

# yahoo画像へアクセス
url = "https://search.yahoo.co.jp/image/search?p={}"
driver.get(url.format(word))  # 指定したURLへアクセス


# 1枚の画像を保存する関数
def save_img(url, file_path):
    r = requests.get(url, stream=True)

    if r.status_code == 200:
        with open(file_path, "wb") as f:
            f.write(r.content)

# 複数の画像のダウンロードを行う関数
def download_imgs(img_urls, save_dir):
    for i, url in enumerate(tqdm(img_urls)):
        file_name = f"{i}.png"  # 画像ファイル名
        save_img_path = os.path.join(save_dir, file_name)  # 保存パス

        save_img(url, save_img_path)  # 画像の保存
            
def img_check(num):
    url = urls[num]
    file =io.BytesIO(urlopen(url).read())
    img = Image.open(file)
    img.show()


# 止まるまでスクロールする
print("scrolling .....")
while True:
    prev_html = driver.page_source  # スクロール前のソースコード
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # 最下部までスクロール
    sleep(1.0)   # 1秒待機
    current_html = driver.page_source  # スクロール後のソースコード

    # スクロールの前後で変化が無ければループを抜ける
    if prev_html != current_html:
        prev_html = current_html
    else:
        # 「もっと見る」ボタンがあればクリック
        try:
            button = driver.find_element_by_class_name("sw-Button")
            button.click()
        except:
            break
            
print("Searching Original Image URLs .....")
figures = driver.find_elements_by_class_name("sw-Thumbnail__image")
urls = []
for i, figure in enumerate(tqdm(figures[:num])):
    figure.click()
    sleep(2)
    element = driver.find_element_by_class_name("sw-PreviewPanel__image")
    url = element.get_attribute("src")
    urls.append(url)

driver.close()   # driverをクローズする
print("Download Start !!")
download_imgs(urls, save_dir)


