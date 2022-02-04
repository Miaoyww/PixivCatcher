import requests

html_header = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://www.pixiv.net/',
    'Accept-Language': 'zh-cn'
    # 'Authorization': 'Bearer 68125668_6BNfT2cmswtv8PdHvfds2o8gjAvmRlNJ'
}
url = "https://app-api.pixiv.net/v1/search/illust"
param = {
    'word': "HuTao",
    'search_target': "partial_match_for_tags",
    'sort': "date_desc",
    'filter': "for_android"
}
while True:
    try:
        res = requests.request('POST', url, params=param, headers=html_header, verify=False)
    except Exception as errors:
        print(f"出现了错误{errors}")
        continue
    else:
        with open("a.json", "wb") as w:
            w.write(res.content)
        break
