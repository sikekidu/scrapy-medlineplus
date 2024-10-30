import requests
from bs4 import BeautifulSoup
import logging
import json
import os

# Step 1: 定义基本 URL 和请求头
BASE_URL = "https://medlineplus.gov/druginformation.html"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Step 2: 设置日志记录，用于调试
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Step 3: 函数获取 Soup 对象
def get_soup(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        logging.info(f"成功获取 URL: {url}")
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        logging.error(f"获取 URL {url} 时出错: {e}")
        return None

# Step 4: 函数获取药物字母链接
def get_drug_links():
    soup = get_soup(BASE_URL)
    if not soup:
        return []

    # 找到 A-Z 和 0-9 链接部分
    content_block = soup.find('div', {'class': 'section-body'})
    if not content_block:
        logging.warning("未找到包含链接的 section-body。")
        return []

    links = content_block.find_all('a')
    drug_links = [link['href'] for link in links if link.get('href')]
    logging.info(f"找到 {len(drug_links)} 个药物分类链接。")
    return drug_links

# Step 5: 将所有链接保存到 drug_details.json 文件中
def save_links_to_json(drug_links):
    # 删除已有的 drug_details.json 文件
    if os.path.exists('drug_details.json'):
        os.remove('drug_details.json')

    # 格式化链接为完整 URL 并保存
    full_links = [f"https://medlineplus.gov/{link}" if not link.startswith("http") else link for link in drug_links]
    
    with open('drug_details.json', 'w') as file:
        file.write('[\n')
        for i, link in enumerate(full_links):
            json.dump({"link": link}, file)
            if i < len(full_links) - 1:
                file.write(',\n')
        file.write('\n]')
    logging.info("保存所有药物分类链接到 drug_details.json 文件中。")

# 主函数
def main():
    drug_links = get_drug_links()
    if not drug_links:
        logging.error("未找到任何药物链接，程序退出。")
        return

    save_links_to_json(drug_links)

if __name__ == "__main__":
    main()
