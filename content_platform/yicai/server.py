import requests
from bs4 import BeautifulSoup


def get_yicai_news():
    url = 'https://www.yicai.com/news/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        print(response.text)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        news_list = []
        for item in soup.select('.m-con .f-db'):
            title = item.get_text().strip()
            link = item['href']
            if not link.startswith('http'):
                link = 'https://www.yicai.com' + link
            news_list.append({'title': title, 'url': link})

        return news_list

    except Exception as e:
        print(f"获取新闻失败: {e}")
        return []


# 使用示例
news = get_yicai_news()
for i, item in enumerate(news[:10], 1):
    print(f"{i}. {item['title']}")
    print(f"   {item['url']}\n")