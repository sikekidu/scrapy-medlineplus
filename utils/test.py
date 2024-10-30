import requests
from bs4 import BeautifulSoup
import logging
import json
from mongodb_connection import MongoClient
import os

# Step 1: 设定基本设置
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

# Step 4: 连接 MongoDB 数据库
def get_mongo_client():
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
            mongo_url = config.get('mongo_url')
            if not mongo_url:
                raise ValueError("The config file does not contain 'mongo_url'")
            client = MongoClient(mongo_url)
            logging.info("成功连接到 MongoDB。")
            return client
    except Exception as e:
        logging.error(f"MongoDB 连接失败: {e}")
        return None

client = get_mongo_client()
if client:
    db = client['medlineplus']
    drug_collection = db['drug_details']
else:
    logging.error("无法连接到 MongoDB，程序退出。")
    exit()

# Step 5: 读取 meds_links.json 中的链接
def get_links_from_json():
    try:
        # 使用相对路径或绝对路径
        file_path = os.path.join(os.path.dirname(__file__), 'meds_links.json')
        with open(file_path, 'r') as file:
            data = json.load(file)
            # 确保数据是一个列表，并且列表中的每个元素是字符串
            if not isinstance(data, list) or not all(isinstance(link, str) for link in data):
                logging.error("meds_links.json 文件的内容不是有效的列表格式。")
                return []
            logging.info(f"成功读取 {len(data)} 个链接。")
            return data
    except FileNotFoundError:
        logging.error("meds_links.json 文件不存在。")
        return []
    except json.JSONDecodeError as e:
        logging.error(f"JSON 解析错误: {e}")
        return []

# Step 6: 爬取药物详细信息
def scrape_drug_details(url):
    soup = get_soup(url)
    if not soup:
        return None
    
    drug_info = {}
    drug_info['url'] = url
    
    # 获取药品名称
    title_tag = soup.find('h1')
    drug_info['name'] = title_tag.get_text(strip=True) if title_tag else "Unknown"
    
    # 使用 h2 和 h3 标签及其相关内容来获取详细信息
    details = []
    for tag in soup.find_all(['h2', 'h3']):
        section = {}
        section['heading'] = tag.get_text(strip=True)
        section_body = tag.find_next(lambda x: x and x.name == 'div' and 'section-body' in x.get('class', []))
        if section_body:
            section['content'] = section_body.get_text(strip=True)
        else:
            section['content'] = "No detailed information available"
        details.append(section)
    
    drug_info['details'] = details
    logging.info(f"爬取药物信息: {url}")
    return drug_info

# Step 7: 把药物信息存入 MongoDB
def save_to_mongodb(drug_info):
    if not drug_info:
        return
    try:
        # 使用 upsert=True 来插入或更新文档
        drug_collection.update_one(
            {'url': drug_info['url']},
            {'$set': drug_info},
            upsert=True
        )
        logging.info(f"成功将药物信息更新或存入 MongoDB: {drug_info['url']}")
    except Exception as e:
        logging.error(f"存入 MongoDB 失败: {e}")

# 主函数
def main():
    if os.getenv('DEBUG', 'False').lower() in ('true', '1', 't'):
        # 调试模式下清空集合
        try:
            result = drug_collection.delete_many({})
            logging.info(f"已清除 {result.deleted_count} 个文档，用于调试。")
        except Exception as e:
            logging.error(f"清空集合失败: {e}")

    links = get_links_from_json()
    if not links:
        logging.error("未找到任何药物链接，程序退出。")
        return

    for link in links:
        drug_info = scrape_drug_details(link)
        save_to_mongodb(drug_info)

if __name__ == "__main__":
    main()
