
# coding: utf-8

# # ユーザー定義の関数たち

# ## BeautifulSoup  
# * htmlの取得
# * BsObjの取得
# * 指定したURLのHTMLをローカルに保存、それを読み込む

# In[2]:


from urllib.request import Request,urlopen
import urllib.request
from urllib.error import HTTPError
from urllib.error import URLError
from bs4 import BeautifulSoup
def getHTML(URL):
    'htmlの取得'
    try:
        req = Request(URL,headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req)
    except HTTPError as e:
        print(e)
    except URLError as e:#サーバーに全く到達できない(URLの記述が間違えているなど)
        print('The server could not be found!')
    else:
        return html
    
def getBS4(html):
    'BsObjの取得'
    return BeautifulSoup(html.read(),"html.parser")

def getBS4_Local(fn):
    'ローカルファイルのBsObjの取得'
    return BeautifulSoup(open(fn), "lxml")
    
def saveHTML(URL,fn):
    '指定したURLのHTMLをローカルに保存'
    html = getHTML(URL)
    bsObj = getBS4(html)
    with open( fn + '.html', mode = 'w', encoding = 'utf-8') as fw:
        fw.write(bsObj.prettify())

def getBS4_FromLocalHTML(fn):
    'saveHTMLで保存したHTMLでBSObjを取得'
    return BeautifulSoup(open( fn + '.html', encoding='utf-8'), 'html.parser')
    


# ## 日付

# In[4]:


def getNowTime():
    '現在の日付を取得する YYYYMMDDhhmmss'
    from datetime import datetime, timezone, timedelta
    import time
    JST = timezone(timedelta(hours=+9), 'JST')
    return datetime.fromtimestamp(time.time(), JST).strftime("%Y%m%d%H%M%S")


# ## ファイル操作

# In[1]:


import os
def fileOpenRead(fn):
    '読み込み用'
    return open(fn,'r')

def fileOpen(fn):
    '書き込み用'
    #cp932問題を解決するためwbで開いている
    return open(fn,'wb')

def fileWrite(f,str):
    #cp932を無視
    try:
        f.write(str.encode('cp932','ignore'))
    except:
        f.write(str)
    finally:
        f.flush()
    
def fileClose(f):
    f.close()

def fileDelete(f):
    'ファイルを削除する'
    os.remove(f)
    
def fileDataSlim(f):
    '重複データを消す'
    with open(f) as _f:
        lines = _f.readlines()
    lines_set = set(lines) #辞書にして重複データを消す
    
    os.remove(f)
    
    with open(f, 'w') as fo:
        for l in lines_set:
            fo.write(l)
            
def fileDataClear(f):
    '中身を消す'
    os.remove(f)
    open(f)
    f.close()
    


# # データ編集

# In[1]:


#リスト内の辞書を値を再帰的に取得
def getlistValue(target_list):
    for l in target_list:
        if isinstance(l,dict):
            for _l in l.values():
                if isinstance(_l,dict):
                    yield from getlistValue(_l)
                else:
                    #print(_l)
                    yield _l
        else:
            #print(l)
            yield l
            
#辞書の値を再帰的に取得
def getDictValue(target_dict):
    if isinstance(target_dict,dict):
        for key in target_dict.keys():
            value = target_dict[key]
            if isinstance(value,dict):
                yield from getDictValue(value)          
            elif isinstance(value,list):                
                for _v in list(getlistValue(value)):
                    #print(_v)
                    yield _v
            else:
                yield value


# # Seleniumでhtml取得

# In[1]:


#def getHTML_Sel(URL,pjs_path):    
def getHTML_Sel():
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as ec
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys    
    import time
    # user agent
    user_agent = 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.66 Safari/537.36'
    # PhantomJS本体のパス
    pjs_path='D:\\Anaconda_Apps\\Scripts\\phantomjs'
#    pjs_path = sys.argv[2]
    dcap = {
        "phantomjs.page.settings.userAgent" : user_agent,
        'marionette' : True
    }
    driver = webdriver.PhantomJS(executable_path=pjs_path, desired_capabilities=dcap)
    # 5秒待機
    wait = WebDriverWait(driver, 10)

    driver.set_window_size(1024, 768)
#    URL="https://www.pinterest.jp/pin/759630662122154864/"
    URL="https://www.pinterest.jp/pin/594686325771495635/"
    driver.get(URL)
    
    wait.until(ec.presence_of_all_elements_located)
    driver.save_screenshot('screen_getURL1.png')
    driver.find_element_by_tag_name("body").send_keys(Keys.F5)
    wait.until(ec.presence_of_all_elements_located)
    driver.save_screenshot('screen_getURL2.png')
    
    html = driver.page_source
    driver.quit()
    print(html)
    #return url_Baselist, url_Imglist

if __name__ == '__main__':
    getHTML_Sel()


# In[2]:


def getHTML_Sel_chrome():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    
    import time

    options = Options()
    options.binary_location = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
    options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=options, executable_path="D:\\Anaconda_Apps\\chromedriver_win32\\chromedriver.exe")
    
    # 5秒待機
    wait = WebDriverWait(driver, 10)

    driver.set_window_size(1024, 768)
#    URL="https://www.pinterest.jp/pin/759630662122154864/"
    URL="https://www.pinterest.jp/pin/594686325771495635/"
    driver.get(URL)
    
    wait.until(ec.presence_of_all_elements_located)
    
    html = driver.page_source
    driver.quit()
    print(html)
    #return url_Baselist, url_Imglist

if __name__ == '__main__':
    getHTML_Sel_chrome()


# # データの暗号化・復号化

# In[35]:


#暗号
from Crypto.Cipher import AES
import hashlib
import base64

def get_encrypt_data(raw_data, key, iv):
    # base64にエンコードし、バイト数を16の倍数にする
    raw_data_base64 = _trans_multiple_of_16byte(base64.b64encode(raw_data.encode("utf8")))
    secret_key = hashlib.sha256(key.encode("utf8")).digest()
    iv = hashlib.md5(iv.encode("utf8")).digest()
    crypto = AES.new(secret_key, AES.MODE_CBC, iv)
    cipher_data = crypto.encrypt(raw_data_base64)
    cipher_data_base64 = base64.b64encode(cipher_data)
    return cipher_data_base64

def _trans_multiple_of_16byte(data):
    # _を付け加えて16バイトの倍数にする
    surplus = len(data) % 16
    if surplus != 0:
        for i in range(16 - surplus):
            data += "_".encode("utf8")
    return data

if __name__ == '__main__':
    message = "ANGOU"
    password = "This is password"
    iv = "hoge"
    encrypt_data = get_encrypt_data(message, password, iv)
    print(encrypt_data)


# In[37]:


#復号
from Crypto.Cipher import AES
import hashlib
import base64

def get_decrypt_data(cipher_data_base64, key, iv):
    cipher_data = base64.b64decode(cipher_data_base64)
    secret_key = hashlib.sha256(key.encode("utf8")).digest()
    iv = hashlib.md5(iv.encode("utf8")).digest()
    crypto = AES.new(secret_key, AES.MODE_CBC, iv)
    raw_data_base64_16byte = crypto.decrypt(cipher_data).decode('utf-8')
    raw_data_base64 = raw_data_base64_16byte.split("_")[0]
    raw_data = base64.b64decode(raw_data_base64)
    return raw_data.decode('utf-8')

def _reverse_multiple_of_16byte(data):
    # 末尾から追加された文字を全て取り除く
    while FILL_CHAR.encode(ENCODE_TYPE) == data[-1]:
        data.pop()
    return data

if __name__ == '__main__':
    password = "This is password"
    iv = "hoge"
    decrypt_data = get_decrypt_data(b'MImZM/MyrGASfR0vB9TQyA==', password, iv)
    print(decrypt_data)

