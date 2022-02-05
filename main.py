from PixivCatcher import PixivCatcherError
from pixivpy3 import *
import json
import requests
import logging
import time
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
header = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://www.pixiv.net/',
    'Accept-Language': 'zh_cn'
}


class PixivCatcher:
    def __init__(self):
        self.header = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://www.pixiv.net/',
            'Accept-Language': 'zh_cn'
        }

    def download(self, name, url):
        logging.info(f"正在下载{name}")
        while True:
            try:
                res = requests.get(url, headers=self.header, verify=False)
                with open("image/" + name, 'wb+') as w:
                    w.write(res.content)
            except Exception as errors:
                logging.error(f"{name}下载出错{errors},重试中")
                continue
            else:
                break


def login(refresh_token="0zeYA-PllRYp1tfrsq_w3vHGU1rPy237JMf5oDt73c4"):
    while True:
        try:
            api = AppPixivAPI()
            api.auth(refresh_token=refresh_token)
        except PixivError as errors:
            logging.error("登录出错,0.5秒后重试:%s" % errors)
            time.sleep(0.5)
            continue
        else:
            logging.info("登录成功")
            return api


def search(api, keyword, sort="popular_desc", search_target="partial_match_for_tags"):
    # 搜索 (Search)
    # search_target - 搜索类型
    #   partial_match_for_tags  - 标签部分一致
    #   exact_match_for_tags    - 标签完全一致
    #   title_and_caption       - 标题说明文
    # sort: [date_desc, date_asc, popular_desc] - popular_desc为会员的热门排序
    logging.info("开始搜索")
    while True:
        try:
            result = api.search_illust(keyword, search_target=search_target, sort=sort)
        except Exception as errors:
            logging.error("搜索出错,0.5秒后重试: %s" % errors)
        else:
            logging.info("搜索成功")
            return result


def ranking(mode="daily", page_num=1):
    """
    :param mode: 日榜 daily 周榜 weekly 月榜 monthly
    :param page_num: 页数
    :return:
    """
    sort_list = ["daily", "weekly", "monthly"]
    if mode not in sort_list:
        raise PixivCatcherError("不存在的排行榜")
    url = "https://www.pixiv.net/ranking.php?mode=%s&&content=illust&p=%s&format=json" % (mode, page_num)
    return requests.request("GET", url, headers=header, verify=False).json()


def data_processing(mode, jsonc=None, quality="large"):
    """
    :param mode: 处理数据的模式 search ranking
    :param jsonc: 一个经过函数处理过的json
    :param quality: 图片的质量:square_medium,medium,large
    :return: 将会返回一个经处理的list数据,格式[图片的名称, 图片的url地址]
    """
    if mode == "search":
        quality_list = ["square_medium", "medium", "large"]
        if quality not in quality_list:
            raise PixivCatcherError("未包括%s此图片质量" % quality)
        artword_id = [item['id'] for item in jsonc['illusts']]
        artword_title = [re.sub('[/:*?"<>|]', '-', item['title']) for item in jsonc['illusts']]
        artword_url = [item['image_urls'][quality] for item in jsonc['illusts']]

        result = []
        for id_item, title_item, url_item in zip(artword_id, artword_title, artword_url):
            result.append(["%s_%s.jpg" % (title_item, id_item), url_item])
        return result
    if mode == "ranking":
        artwork_id = [item['illust_id'] for item in jsonc['contents']]
        artwork_title = [re.sub('[/:*?"<>|]', '-', item['title']) for item in jsonc['contents']]
        artwork_url = []

        for id_item, title_item in zip(artwork_id, artwork_title):
            logging.info("正在获取排行榜作品: %s" % title_item)
            while True:
                time.sleep(0.01)
                try:
                    res = requests.get(f"https://www.pixiv.net/artworks/{id_item}", headers=header, verify=False)
                except Exception as errors:
                    logging.error("获取排行榜作品详情错误,0.5秒后重试:target:%s,error:%s" % (title_item, errors))
                    continue
                else:
                    artwork_url.append(re.findall(r'"original":"(.+?)"', res.text)[0])
                    break
        result = []
        for id_item, title_item, url_item in zip(artwork_id, artwork_title, artwork_url):
            result.append(["%s_%s.jpg" % (title_item, id_item), url_item])
        return result


if __name__ == "__main__":
    try:
        mode = str(input("请输入下载的模式(search,ranking):"))
        mode_list = ["search", "ranking"]
        if mode not in mode_list:
            raise PixivCatcherError("错误的模式")
        if mode == "search":
            typein = str(input("请键入搜索关键词:"))
            search_result = data_processing("search", search(login(), typein))
            logging.info("初始化完毕，开始下载")
            for info_item in search_result:
                d = PixivCatcher()
                d.download(info_item[0], info_item[1])
        if mode == "ranking":
            ranking_mode = str(input("请键入排行榜模式(daily, weekly, monthly):"))
            page = 1
            while True:
                logging.info("当前排行榜模式:%s, 页数:%s" % (ranking_mode, page))
                while True:
                    try:
                        ranking_result = data_processing("ranking", jsonc=ranking(mode=ranking_mode, page_num=page))
                    except Exception as errors:
                        logging.error("获取排行榜错误,0.5秒后重试:%s" % errors)
                    else:
                        logging.info("初始化完毕，开始下载")
                        for info_item in ranking_result:
                            d = PixivCatcher()
                            d.download(info_item[0], info_item[1])
                        decision = str(input("当前页数为%s是否继续(y/n)?:" % page))
                        if decision == "y" or decision == "yes":
                            page += 1
                            continue
                        else:
                            break
                break
    except Exception as error:
        logging.error("出现错误: %s" % error)
