# 暂时弃用
import requests
import time
import re

from requests.packages import urllib3
urllib3.disable_warnings()  # 将来的修改，使用HTTPS请求


class PixivCatcherError(Exception):
    pass

class PixivCatcher:
    def __init__(self):
        self.url = "https://app-api.pixiv.net" # 防止api变动，方便维护
        self.access_token = None
        self.header = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://www.pixiv.net/',
            'Accept-Language': 'zh_cn'
        }

    def set_language(self, language):
        self.header["Accept-Language"] = language

    def set_token(self, token):
        self.access_token = token

    def auth(self, token):
        """
            未来加入使用账户密码登录，目前仅支持使用access token
        """
        self.header['Authorization'] = token

    def search_illust(self, word, search_target, sort, access= True):
        # 通过解包Pixiv Android APK 获得
        # 感谢来自Mikubill的帮助
        # https://github.com/upbit/pixivpy/discussions/205#discussioncomment-2112598

        client_id = "MOBrBDS8blbauoSck0ZfDbtuzpyT"
        client_secret = "lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj"
        hash_secret = "28c1fdd170a5204386cb1313c7077b34f83e4aaf4aa829ce78c231e05b0bae2c"

        url = "%s/v1/search/illust" % self.url

        params = {
            "word": word,
            "sort": sort,
            "search_target": search_target
        }




    def download(self, name, url):
        print(f"正在下载{name}")
        while True:
            try:
                res = requests.get(url, headers=self.header, verify=False)
                with open("image/" + name, 'wb+') as w:
                    w.write(res.content)
            except Exception as error:
                print(f"{name}下载出错{error}")
                continue
            else:
                break

    def geturl(self):
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
        artwork_name = [re.sub('[/:*?"<>|]', '-', item['title']) for item in
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

