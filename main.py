import requests
import time
import threading
import re
from requests.packages import urllib3
urllib3.disable_warnings()

DownloadUrl = []


class Download:
    def __init__(self, name, url):
        self.url = url
        self.name = name
        self.header = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://www.pixiv.net/'
        }

    def download(self):
        print(f"正在下载{self.name}")
        while True:
            try:
                res = requests.get(self.url, headers=self.header, verify=False)
                with open("image/" + self.name, 'wb+') as w:
                    w.write(res.content)
            except Exception as error:
                print(f"{self.name}下载出错{error}")
                continue
            else:
                break


def geturl():
    html_header = {
        'Accept': 'text/html',
        'Host': 'www.pixiv.net',
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://www.pixiv.net/'
    }
    image_header = {

    }
    page_url = "https://www.pixiv.net/ranking.php?mode=weekly&&content=illust&p=1&format=json"
    res_page = requests.get(page_url, headers=html_header, verify=False).json()
    # 获取作品id
    artwork_id = [item['illust_id'] for item in res_page['contents']]
    # 获取作品名称
    '''
        re 用于去除非法字符
        使用for遍历list获得正确的名称
    '''
    artwork_name = [re.sub('[\/:*?"<>|]', '-', item['title']) for item in
                    res_page['contents']]
    # 获作品原图url
    artwork_url = []
    for id_item in artwork_id:
        while True:
            time.sleep(0.1)
            try:
                res = requests.get(f"https://www.pixiv.net/artworks/{id_item}", headers=html_header, verify=False)
            except:
                continue
            else:
                artwork_url.append(re.findall(r'"original":"(.+?)"', res.text))
                break
    artwork = []  # 用于储存作品名称与url
    # 合并
    for id_item, name_item, url_item in zip(artwork_id, artwork_name, artwork_url):
        artwork.append([name_item + "_" + str(id_item) + ".jpg", url_item])
    return artwork


if __name__ == "__main__":
    # info = geturl()
    '''    for item in info:
        download = Download(item[0], item[1][0])
        thread_ = threading.Thread(target=download.download)
        thread_.start()'''
    download = Download("abc.txt", "https://www.pixiv.net/tags/%E8%83%A1%E6%A1%83/illustrations")
    download.download()
