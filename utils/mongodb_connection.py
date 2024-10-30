import json
from pymongo import MongoClient

def main():
    try:
        # 读取配置文件
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
            
        # 从配置文件中获取 MongoDB URL
        mongo_url = config.get('mongo_url')
        if not mongo_url:
            raise ValueError("The config file does not contain 'mongo_url'")
        
        # 使用读取的 MongoDB URL 进行连接
        client = MongoClient(mongo_url)
        
        # 测试连接
        db = client.admin
        # 打印连接成功的信息
        print("Successfully connected to MongoDB.")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

if __name__ == "__main__":
    main()

