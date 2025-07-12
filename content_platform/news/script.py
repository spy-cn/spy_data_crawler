import difflib
import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import chromedriver_autoinstaller  # 确保导入 chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def setup_driver():
    """设置并返回Selenium WebDriver"""
    chromedriver_autoinstaller.install()  # 自动安装匹配的 ChromeDriver
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"Error setting up driver: {e}")
        raise


def fetch_news(driver, url, selector):
    driver.get(url)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    news_items = driver.find_elements(By.CSS_SELECTOR, f'{selector} li')
    news_data = []
    for item in news_items:
        category = item.find_element(By.CSS_SELECTOR, 'a.c').text
        title = item.find_element(By.CSS_SELECTOR, 'a.t').text
        link = item.find_element(By.CSS_SELECTOR, 'a.t').get_attribute('href')
        time_str = item.find_element(By.CSS_SELECTOR, 'i').text
        time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        news_data.append({'category': category, 'title': title, 'link': link, 'time': time})
    return news_data


def fetch_all_news():
    driver = setup_driver()
    url = 'https://www.ithome.com/list/'
    news_data = fetch_news(driver, url, 'ul.datel')
    driver.quit()
    return news_data


def ensure_dir_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def write_news_file(filename, date_str):
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# 今日新闻 - {date_str}\n")


def is_similar(entry1, entry2, threshold=0.9):
    ratio = difflib.SequenceMatcher(None, entry1, entry2).ratio()
    ratio_rounded = round(ratio, 4)  # 保留两位小数
    if 0.99 > ratio_rounded >= threshold:
        print(f"正在检测：{entry1}")
        print(f"相似度: {ratio_rounded}，检测到相似新闻")
    return ratio_rounded > threshold


def save_news_to_markdown(now, new_news):
    year_month = now.strftime("%Y-%m")
    folder_path = f"news_archive/{year_month}"  # 文件夹路径
    ensure_dir_exists(folder_path)
    month_news_filename = f"{folder_path}/00.md"
    today_news_filename = f"{folder_path}/{now.strftime('%d')}.md"
    write_news_file(today_news_filename, now.strftime('%Y年%m月%d日'))
    # 读取或初始化本月新闻文件
    if os.path.exists(month_news_filename):
        with open(month_news_filename, 'r', encoding='utf-8') as f:
            existing_month_news = f.read()
    else:
        existing_month_news = "# 本月新闻\n"
        with open(month_news_filename, 'w', encoding='utf-8') as f:
            f.write(existing_month_news)
    news_set = set(existing_month_news.splitlines())
    news_written_count = 0

    for news in new_news:
        markdown_entry = f"- [{news['title']}]({news['link']})\n"
        news_time = news['time']
        news_folder_path = f"news_archive/{news_time.strftime('%Y-%m')}"
        news_filename = f"{news_folder_path}/{news_time.strftime('%d')}.md"
        # 如果新闻文件夹不存在，则创建
        ensure_dir_exists(news_folder_path)
        # 如果新闻文件不存在，创建文件并写入标题
        write_news_file(news_filename, news_time.strftime('%Y年%m月%d日'))
        # 检查新闻条目是否重复
        is_new_entry = all(not is_similar(markdown_entry, existing_entry) for existing_entry in news_set)
        if is_new_entry:
            news_set.add(markdown_entry)
            news_written_count += 1
            # 写入本月新闻文件
            with open(month_news_filename, 'a', encoding='utf-8') as month_file:
                month_file.write(markdown_entry)
            # 写入对应日期的新闻文件
            with open(news_filename, 'a', encoding='utf-8') as day_file:
                day_file.write(markdown_entry)
    if news_written_count > 0:
        print(f"新闻保存成功，本次更新了 {news_written_count} 条新闻。")
    else:
        print("没有新的新闻需要更新。")


def switch_to_parent_if_src():
    """检查当前目录的最后一级是否是src，如果是，则切换到上一级目录"""
    current_dir = os.getcwd()
    base_name = os.path.basename(current_dir)

    if base_name == 'src':
        parent_dir = os.path.dirname(current_dir)
        os.chdir(parent_dir)
        print(f'切换到上一级目录: {parent_dir}')


def main():
    start_time = time.time()
    switch_to_parent_if_src()
    tz = ZoneInfo('Asia/Shanghai')
    now = datetime.now(tz)
    print("当前时间：", now.strftime("%Y-%m-%d %H:%M:%S %Z"))  # 打印当前的日期和时间以及时区信息
    # 调用函数爬取所有新闻榜单
    print("开始爬取所有新闻...")
    try:
        new_news = fetch_all_news()
        print("新闻爬取完成，共爬取到 {} 条新闻。".format(len(new_news)))
        # 保存新闻到Markdown文件
        save_news_to_markdown(now, new_news)
    except Exception as e:
        print(f"An error occurred: {e}")
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"写入新闻完成，总耗时: {elapsed_time:.2f} 秒")


if __name__ == '__main__':
    main()