# -*- coding: utf-8 -*-
from pixivpy3 import *
import multiprocessing as mp
import urllib3
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
HEADER = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://www.pixiv.net/',
    'Accept-Language': 'zh_cn'
}
api: AppPixivAPI
config: dict
illust_list = {
    "max_illust": 0,
    "loaded_illusts": 0,
    "finshed_illusts": 0,
}
exit_flag = False


class PixivCatcherError(Exception):
    pass


def download(name, url):
    if not os.path.exists("./image"):
        os.mkdir("./image")
    strs = r"[\/\\\:\*\?\"\<\>\|]"
    name = name + ".png"
    name = re.sub(strs, "_", name)
    if not os.path.exists("./image/" + name):
        while True:
            try:
                res = requests.get(url, headers=HEADER, verify=False)
                with open("image/" + name, 'wb+') as w:
                    w.write(res.content)
                return name
            except KeyboardInterrupt:
                logging.info("download: 终止程序")
                sys.exit(0)
            except Exception as download_error:
                logging.error(f"download: 即将重新下载%s,因为%s" % (name, download_error))
                continue
            finally:
                if not os.path.exists("image/" + name):
                    logging.error("download: 即将重新下载%s,因为文件不存在" % name)
                    continue
                else:
                    return name
    else:
        return name


def set_default_config():
    default_config = {
        "start_mode": "ranking",
        "search_config": {
            "search_keyword": "Pardofeils",
            "search_target": "partial_match_for_tags",
            "search_sort": "date_desc"
        },
        "ranking_config": {
            "ranking_mode": "daily"
        }
    }
    with open("config.json", "w") as w:
        w.write(json.dumps(default_config, sort_keys=True, indent=4, separators=(',', ':')))


def download_callback_func(obj):
    logging.info("download: 下载成功: %s" % obj)
    illust_list['finshed_illusts'] += 1
    if illust_list['finshed_illusts'] >= illust_list['max_illust']:
        logging.info("download: 下载完成")
        logging.info("download: 共下载%s张图片" % illust_list['finshed_illusts'])
        logging.info("程序结束")
        global exit_flag
        exit_flag = True
        sys.exit(0)


def login(refresh_token="0zeYA-PllRYp1tfrsq_w3vHGU1rPy237JMf5oDt73c4"):
    while True:
        try:
            logging.error("login: 正在尝试登录")
            global api
            api = AppPixivAPI()
            api.auth(refresh_token=refresh_token)
        except PixivError as login_error:
            logging.error("login: 登录出错,0.5秒后重试:%s" % login_error)
            time.sleep(0.5)
            continue
        except KeyboardInterrupt:
            logging.info("login: 终止程序")
            sys.exit(0)
        else:
            logging.info("login: 登录成功")
            break


def search_result(_keyword, _sort="popular_desc", _search_target="partial_match_for_tags"):
    logging.info("search_result: 开始搜索")
    while True:
        try:
            result = api.search_illust(_keyword, search_target=_search_target, sort=_sort)
        except Exception as search_error:
            logging.error("search_result: 搜索出错,0.5秒后重试: %s" % search_error)
        else:
            logging.info("search_result: 搜索成功")
            return result


def data_processing(mode, jsonc: json = None, quality="large"):
    if mode == "search":
        illust_list['max_illust'] = len(jsonc["illusts"])
        quality_list = ["square_medium", "medium", "large"]
        if quality not in quality_list:
            raise PixivCatcherError("data_processing: 未包括%s此图片质量" % quality)
        artword_id = [item['id'] for item in jsonc['illusts']]
        artword_title = [re.sub('[/:*?"<>|]', '-', item['title']) for item in jsonc['illusts']]
        artword_url = [item['image_urls'][quality] for item in jsonc['illusts']]
        if not illust_list["loaded_illusts"] >= illust_list["max_illust"]:
            for id_item, title_item, url_item in zip(artword_id, artword_title, artword_url):
                logging.info("download: 开始下载 %s" % title_item)
                pool.apply_async(
                    download,
                    (f"{title_item}_{id_item}", url_item),
                    callback=download_callback_func
                )
                illust_list['loaded_illusts'] += 1

    if mode == "ranking":
        while True:
            try:
                temp_result = api.illust_ranking(config["ranking_config"]["ranking_mode"])
            except PixivError:
                logging.error("data_processing: 排行榜获取失败,0.5秒后重试")
                time.sleep(0.5)
                continue
            else:
                logging.info("data_processing: 排行榜获取成功")
                json_result = temp_result
                break
        illust_list['max_illust'] = len(json_result["illusts"])
        if not illust_list["loaded_illusts"] >= illust_list["max_illust"]:
            for illult in json_result["illusts"]:
                logging.info("download: 开始下载 %s" % illult["title"])
                pool.apply_async(
                    download,
                    (illult["title"], illult["image_urls"][quality]),
                    callback=download_callback_func
                )
                illust_list['loaded_illusts'] += 1
        else:
            pass


def search():
    search_keyword = config['search_config']['search_keyword']
    search_target = config['search_config']['search_target']
    search_sort = config['search_config']['search_sort']
    logging.info("search: 初始化完毕")
    logging.info("search: 当前搜索关键词: %s" % search_keyword)
    logging.info("search: 当前搜索类型: %s" % search_target)
    logging.info("search: 当前搜索顺序: %s" % search_sort)
    logging.info("search: 开始搜索")
    data_processing("search", search_result(search_keyword))


def ranking():
    ranking_mode = config['ranking_config']['ranking_mode']
    logging.info("ranking: 初始化完毕")
    logging.info("ranking: 当前排行榜模式: %s" % ranking_mode)
    logging.info("ranking: 开始获取排行榜信息")
    data_processing("ranking")


def main():
    if not os.path.exists("config.json"):
        set_default_config()
        logging.info("main: 未找到配置文件,正在创建配置文件,使用默认配置?(y/n)")
        if input() == "y":
            pass
        else:
            exit()
    with open("config.json") as r:
        global config
        config = json.loads(r.read())
        start_mode = config['start_mode']
        logging.info("main: 当前启动模式%s" % start_mode)
        logging.info("main: 正在加载配置")
        login()
        if start_mode == "search":
            search()
        if start_mode == "ranking":
            ranking()


if __name__ == "__main__":
    pool = mp.Pool(5)
    main()
    while not exit_flag:
        time.sleep(1)
