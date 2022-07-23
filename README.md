<div align="center">

# PixivCatcher

一个基于 [Pixivpy3](https://github.com/upbit/pixivpy) 的一个pixiv图片批量爬虫工具

![Alt](https://repobeats.axiom.co/api/embed/366a6420179235e0a60cbdf923a1a731c57e5764.svg "Repobeats analytics image")

</div>

## 功能

|     功能      | 是否实现 |
|:-----------:|------|
| 爬取排行榜进行图片下载 | √    |
|  通过关键词搜索图片  | √    |
|  使用多线程下载图片  | √    |

## 如何使用?

1.使用`pip`安装必要支持库:

    pip install requests
    pip install pixivpy3

2.将本仓库内的代码`clone`到本地

    git clone https://github.com/Miaoywww/PixivCatcher.git

3.在终端启动main.py

## 配置文件

在每次启动时,程序会检测是否含有config.json文件,如果没有,将视为首次启动并将创建一个内容如下的json文件

    {
        "ranking_config":{
            "ranking_mode":"day"
        },
        "search_config":{
            "search_keyword":"Pardofelis    ",
            "search_sort":"date_desc",
            "search_target":"partial_match_for_tags"
        },
        "start_mode":"ranking"
    }

|       名称       |                                                                       说明                                                                       |
|:--------------:|:----------------------------------------------------------------------------------------------------------------------------------------------:|
|   start_mode   |                                                              有search和ranking两个模式                                                               |
| search_config  |                                                        如果在start_mode选择了search,那么会加载此配置                                                         |
| ranking_config |                                                       如果在start_mode选择了rankinng,那么会加载此配置                                                        |
| search_keyword |                                                                     搜索关键词                                                                      |
| search_target  |                  搜素类型<br/>  partial_match_for_tags - 标签部分一致<br/>exact_match_for_tags - 标签完全一致<br/> title_and_caption - 标题说明文                   |
|  search_sort   |                            排序方法<br/> date_desc - 按最新排序<br/> date_asc - 按旧排序<br/> popular_desc - 按热度排序(需要pixiv高级会员)                             |
|  ranking_mode  |   排行榜模式<br/> day, week, month, day_male, day_female, week_original, week_rookie, day_r18, day_male_r18, day_female_r18, week_r18, week_r18g    |

<div align="center">

>**声明: 本程序仅供参考与学习，禁止用于非法用途**

</div>