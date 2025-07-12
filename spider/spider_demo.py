import requests
from bs4 import BeautifulSoup


def simple_crawler(url, max_pages=5):
    """
    简单的网页爬虫
    :param url: 起始URL
    :param max_pages: 最大爬取页面数
    """
    pages_visited = 0
    links_to_visit = [url]
    visited_links = set()

    while links_to_visit and pages_visited < max_pages:
        current_url = links_to_visit.pop(0)

        # 跳过已访问的链接
        if current_url in visited_links:
            continue

        try:
            # 发送HTTP请求
            response = requests.get(current_url, timeout=5)
            response.raise_for_status()  # 检查请求是否成功

            # 解析HTML内容
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取页面标题
            title = soup.title.string if soup.title else "无标题"
            print(f"访问页面: {current_url}")
            print(f"页面标题: {title}\n")

            # 提取页面中的所有链接
            for link in soup.find_all('a', href=True):
                href = link['href']
                # 处理相对URL
                if href.startswith('/'):
                    href = requests.compat.urljoin(current_url, href)
                # 只处理HTTP/HTTPS链接
                if href.startswith(('http://', 'https://')):
                    if href not in visited_links:
                        links_to_visit.append(href)

            visited_links.add(current_url)
            pages_visited += 1

        except requests.exceptions.RequestException as e:
            print(f"访问 {current_url} 时出错: {e}")

    print(f"\n爬取完成，共访问了 {pages_visited} 个页面")


# 使用示例
if __name__ == "__main__":
    start_url = "https://www.91porn.com/index.php"  # 替换为你想爬取的网站
    simple_crawler(start_url)