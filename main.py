# -*- coding: utf-8 -*-

from pixivpy3 import *
from requests.packages import urllib3
import threading
import requests
import logging
import json
import time
import os
import re
import sys

urllib3.disable_warnings()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
header = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://www.pixiv.net/',
    'Accept-Language': 'zh_cn'
}


class PixivCatcherError(Exception):
    pass


download_header = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://www.pixiv.net/',
    'Accept-Language': 'zh_cn'
}


def download(name, url):
    if not os.path.exists("image/" + name):    
        while True:
            logging.info("download(): 开始下载 %s" % name)
            try:
                res = requests.get(url, headers=download_header, verify=False)
                with open("image/" + name, 'wb+') as w:
                    w.write(res.content)
                logging.info("download(): %s下载完成" % name)
            except FileNotFoundError:
                os.mkdir("image")
                logging.info("download(): 创建image文件夹")
                continue
            except KeyboardInterrupt:
                logging.info("download(): 终止程序")
                os._exit(0)
            except Exception as download_error:
                logging.error(f"download(): 即将重新下载%s,因为%s" % (name, download_error))
                continue
            finally:
                if not os.path.exists("image/" + name):
                    logging.error("download(): 即将重新下载%s,因为文件不存在" % name)
                    continue
                else:
                    break
    else:
        logging.info("download(): %s已存在, 跳过下载" % name)


def set_default_config():
    default_config = {
        "start_mode": "ranking",
        "search_config": {
            "search_keyword": "Hutao",
            "search_target": "partial_match_for_tags",
            "search_sort": "date_desc"
        },
        "ranking_config": {
            "ranking_mode": "daily",
            "ranking_goon": False,
            "ranking_start_page": 1,
        }
    }
    with open("config.json", "w") as w:
        w.write(json.dumps(default_config, sort_keys=True, indent=4, separators=(',', ':')))


def login(refresh_token="0zeYA-PllRYp1tfrsq_w3vHGU1rPy237JMf5oDt73c4"):
    while True:
        try:
            api = AppPixivAPI()
            api.auth(refresh_token=refresh_token)
        except PixivError as login_error:
            logging.error("login(): 登录出错,0.5秒后重试:%s" % login_error)
            time.sleep(0.5)
            continue
        else:
            logging.info("login(): 登录成功")
            return api


def search(api, _keyword, _sort="popular_desc", _search_target="partial_match_for_tags"):
    # 搜索 (Search)
    # search_target - 搜索类型
    #   partial_match_for_tags  - 标签部分一致
    #   exact_match_for_tags    - 标签完全一致
    #   title_and_caption       - 标题说明文
    # sort: [date_desc, date_asc, popular_desc] - popular_desc为会员的热门排序
    logging.info("开始搜索")
    while True:
        try:
            result = api.search_illust(_keyword, search_target=_search_target, sort=_sort)
        except Exception as search_error:
            logging.error("search(): 搜索出错,0.5秒后重试: %s" % search_error)
        else:
            logging.info("search(): 搜索成功")
            return result


def ranking(mode="daily", page_num=1):
    """
    :param mode: 日榜 daily 周榜 weekly 月榜 monthly
    :param page_num: 页数
    :return:
    """
    sort_list = ["daily", "weekly", "monthly"]
    if mode not in sort_list:
        raise PixivCatcherError("ranking(): 不存在的排行榜")
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
            raise PixivCatcherError("data_processing(): 未包括%s此图片质量" % quality)
        artword_id = [item['id'] for item in jsonc['illusts']]
        artword_title = [re.sub('[/:*?"<>|]', '-', item['title']) for item in jsonc['illusts']]
        artword_url = [item['image_urls'][quality] for item in jsonc['illusts']]

        result = []
        for id_item, title_item, url_item in zip(artword_id, artword_title, artword_url):
            thread_ = threading.Thread(
                target=download(f"{title_item}_{id_item}.jpg", url_item)
            )
            thread_.start()

    if mode == "ranking":
        artwork_id = [item['illust_id'] for item in jsonc['contents']]
        artwork_title = [re.sub('[/:*?"<>|]', '-', item['title']) for item in jsonc['contents']]
        artwork_url = []

        for id_item, title_item in zip(artwork_id, artwork_title):
            logging.info("data_processing(): 正在获取排行榜作品: %s" % title_item)
            while True:
                time.sleep(0.5)
                try:
                    res = requests.get(f"https://www.pixiv.net/artworks/{id_item}", headers=header, verify=False)
                except Exception as data_processing_error:
                    logging.error("data_processing(): 获取排行榜作品详情错误,0.5秒后重试:target:%s,error:%s" % (
                        title_item, data_processing_error))
                    continue
                else:
                    # artwork_url.append(re.findall(r'"original":"(.+?)"', res.text)[0])
                    threading.Thread(
                        target=download(f"{title_item}.jpg", re.findall(r'"original":"(.+?)"', res.text)[0])
                    ).start()
                    break


def search_mode():
    search_keyword = config['search_config']['search_keyword']
    search_target = config['search_config']['search_target']
    search_sort = config['search_config']['search_sort']
    if search_target not in search_target_list:
        raise PixivCatcherError("main: 未知的搜索类型 %s" % search_target)
    if search_sort not in search_sort_list:
        raise PixivCatcherError("main: 未知的搜索顺序 %s" % search_sort)
    logging.info("main: 初始化完毕")
    logging.info("main: 当前搜索关键词: %s" % search_keyword)
    logging.info("main: 当前搜索类型: %s" % search_target)
    logging.info("main: 当前搜索顺序: %s" % search_sort)
    logging.info("main: 开始搜索")
    threading.Thread(target=data_processing("search", search(login(), search_keyword))).start()


def ranking_mode():
    ranking_mode = config['ranking_config']['ranking_mode']
    ranking_goon = config['ranking_config']['ranking_goon']
    try:
        ranking_start_page = int(config['ranking_config']['ranking_start_page'])
    except TypeError as ranking_start_page_error:
        raise PixivCatcherError("main: 类型错误,ranking_start_page应填正整数int类型 %s" % ranking_start_page_error)
    if type(ranking_goon) != bool:
        raise PixivCatcherError("main: 类型错误,ranking_goon应填bool值 %s" % ranking_goon)
    logging.info("main: 初始化完毕")
    logging.info("main: 当前排行榜模式: %s" % ranking_mode)
    logging.info("main: 当前排行榜初始页数: %s" % ranking_start_page)
    logging.info("main: 当前排行榜翻页功能: %s" % ranking_goon)
    logging.info("main: 开始获取排行榜信息")
    while True:
        try:
            threading.Thread(target=data_processing("ranking", jsonc=ranking(mode=ranking_mode, page_num=ranking_start_page))).start()
        except requests.exceptions.ConnectionError as ranking_error:
            logging.error("main: 获取排行榜信息失败,0.5秒后重试\nerror%s" % ranking_error)
            time.sleep(0.5)
            continue


if __name__ == "__main__":
    if not os.path.exists("config.json"):
        set_default_config()
        logging.info("main: 未找到配置文件,正在创建配置文件,是否按照默认配置开始爬取?(y/n)")
        if input() == "y":
            pass
        else:
            exit()
    with open("config.json") as r:
        config = json.loads(r.read())
        start_mode_list = ["search", "ranking"]
        search_target_list = ["partial_match_for_tags", "exact_match_for_tags", "title_and_caption"]
        search_sort_list = ["date_desc", "date_asc", "popular_desc"]
        ranking_mode_list = ["daily", "weekly", "monthly", "rookie"]

        start_mode = config['start_mode']
        if start_mode not in start_mode_list:
            raise PixivCatcherError("main: 未知的启动模式: %s" % start_mode)
        else:
            logging.info("main: 当前启动模式%s" % start_mode)
            logging.info("main: 正在加载配置")
            if start_mode == "search":
                search_mode()
            if start_mode == "ranking":
                ranking_mode()

        logging.info("main: 完成")
        time.sleep(2)
        quit(0)
