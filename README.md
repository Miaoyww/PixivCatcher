#PixivCatcher

这是基于 [Pixivpy3](https://github.com/upbit/pixivpy) 的一个pixiv图片批量爬虫工具


## 功能
|     功能      | 是否实现 |
|:-----------:|------|
| 爬取排行榜进行图片下载 | √    |
|  通过关键词搜索图片  | √    |
|  使用多线程下载图片  | √    |

## 如何使用?
1.使用`pip`安装必要支持库:

    pip install requests

2.将本仓库内的代码`clone`到本地
    
    git clone https://github.com/Miaoywww/PixivCatcher.git

3.在终端启动main.py

## 配置文件

在每次启动时,程序会检测是否含有config.json文件,如果没有,将视为首次启动并将创建一个内容如下的json文件

    {
        "ranking_config":{
            "ranking_goon":false,
            "ranking_mode":"daily",
            "ranking_start_page":1
        },
        "search_config":{
            "search_keyword":"Hutao",
            "search_sort":"date_desc",
            "search_target":"partial_match_for_tags"
        },
        "start_mode":"ranking"
    }

|       名称       |                                                          说明                                                           |
|:--------------:|:---------------------------------------------------------------------------------------------------------------------:|
|   start_mode   |                                             是下载图片的方式,有search和ranking两个模式                                              |
| search_config  |                                            如果在start_mode选择了search,那么会加载此配置                                            |
| ranking_config |                                           如果在start_mode选择了rankinng,那么会加载此配置                                           |
| search_keyword |                                                         搜索关键词                                                         |
| search_target  | 搜素类型<br/>  partial_match_for_tags  - 标签部分一致<br/>exact_match_for_tags    - 标签完全一致<br/> title_and_caption       - 标题说明文 |
|  search_sort   |                排序方法<br/> date_desc - 按最新排序<br/> date_asc - 按旧排序<br/> popular_desc - 按热度排序(需要pixiv高级会员)                |
|  ranking_mode  |                      排行榜模式<br/> daily - 日榜<br/> weekly - 周榜<br/> monthly - 月榜<br/> rookie - 新人榜                       |
|  ranking_goon  |                 是否继续获取此排行榜的下一页<br/> 设定为True时会以ranking_page为初始页数自动翻页<br/> False时只会获取ranking_page那一页的内容                 |
|  ranking_page  |                                              排行榜页数,仅在启动时作为初始页数,内容必须为正整数                                               |


**声明: 本程序仅供参考与学习，禁止用于非法用途**

