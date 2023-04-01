import os
import pandas as pd
import requests
import re
from datetime import datetime
from PIL import Image
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# 服务器上的图片 url 中的年份实际上是数据更新年份
IMAGE_YEAR = "2019"

def request_url(url, n=3):
    if n <= 1:
        print(f"访问{url}失败")
        raise ConnectionError

    try:
        resp = requests.get(url, stream=True)
        resp.raise_for_status()
    except Exception as e:
        print("连接重试")
        n -= 1
        return request_url(url, n)

    return resp

def clean_image_name(image_name):
    return re.sub(r"[ ,.+/'()]", lambda m: '' if m.group() == '(' or m.group() == ')' else '-', image_name.strip()).lower()

def download_image(image_url, ext, save_path):
    try:
        r = request_url(f"{image_url}{ext}")
        if "text/html" not in r.headers['Content-Type']:
            img = Image.open(r.raw).convert('RGB')
            img.save(save_path)
            return True
    except ConnectionError:
        pass

    return False

def process_image_data(image_data):
    day, month, year = image_data[0], image_data[1], image_data[2]
    image_date = datetime.strptime(f"{day}-{month}-{year}", "%d-%b-%Y")
    image_name = image_data[3].strip()
    cleaned_image_name = clean_image_name(image_name)

    image_date_str = image_date.strftime(f"%Y-%m-%d").lower()
    image_url_date = image_date.strftime(f"%B-%-d-{IMAGE_YEAR}").lower()
    image_url = f"https://imagine.gsfc.nasa.gov/hst_bday/images/{image_url_date}-{cleaned_image_name}"
    save_path = f"static/images/{image_date_str}-{cleaned_image_name}.jpg"

    if download_image(image_url, '.jpg', save_path):
        print(f"{image_name} 成功下载 (JPG)")
    elif download_image(image_url, '.png', save_path):
        print(f"{image_name} 成功下载 (PNG)")
    else:
        print(f"{image_name} 无法使用")

data = pd.read_csv('hubblesite.csv').values.tolist()
Path('static/images').mkdir(parents=True, exist_ok=True)

# 设置最大线程数
MAX_THREADS = 5

# 创建线程池
with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    # 使用 map 方法自动分配任务和收集结果
    list(executor.map(process_image_data, data))