import requests
from bs4 import BeautifulSoup
import logging
import json
import os
import time

# Step 1: 定义基本 URL 和请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Step 2: 设置日志记录，用于调试
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Step 3: 从 drug_details.json 中读取所有链接
def load_links_from_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            # 修改为适配标准的 JSON 数组结构
            if isinstance(data, list):
                links = [item['link'] for item in data if 'link' in item]
                return links
            else:
                logging.error(f"Unexpected JSON format in {file_path}. Expected a list of objects.")
                return []
    except FileNotFoundError:
        logging.error(f"File {file_path} not found.")
        return []
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from {file_path}: {e}")
        return []

# Step 4: 访问链接并提取符合 https://medlineplus.gov/druginfo/meds/*.html 格式的子链接
def scrape_meds_links(links):
    meds_links = []
    for index, link in enumerate(links):
        logging.info(f"Processing link {index + 1}/{len(links)}: {link}")
        try:
            response = requests.get(link, headers=HEADERS, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找所有符合 ./meds/*.html 或 /druginfo/meds/*.html 格式的链接
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                # 处理相对路径的链接
                if href.startswith("./meds/"):
                    full_link = f"https://medlineplus.gov/druginfo{href[1:]}"  # 修改为正确的完整链接
                    if full_link not in meds_links:
                        meds_links.append(full_link)
                        logging.info(f"Found meds link: {full_link}")
                elif href.startswith("/druginfo/meds/"):
                    full_link = f"https://medlineplus.gov{href}"
                    if full_link not in meds_links:
                        meds_links.append(full_link)
                        logging.info(f"Found meds link: {full_link}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching URL {link}: {e}")
        
        # 添加延迟，避免请求过于频繁被封禁
        time.sleep(1)
    return meds_links

# Step 5: 保存爬取到的子链接到 JSON 文件
def save_meds_links_to_json(meds_links, output_file):
    with open(output_file, 'w') as file:
        json.dump(meds_links, file, indent=4)
    logging.info(f"Saved {len(meds_links)} meds links to {output_file}")

# 主函数
def main():
    input_file = 'drug_details.json'
    output_file = 'meds_links.json'
    
    # 第一步：加载现有链接
    links = load_links_from_json(input_file)
    if not links:
        logging.error("No links to process. Exiting.")
        return
    
    # 第二步：爬取符合条件的子链接
    meds_links = scrape_meds_links(links)
    
    # 第三步：保存结果到 JSON 文件
    save_meds_links_to_json(meds_links, output_file)

if __name__ == "__main__":
    main()
