import os
import pandas as pd
import requests
from datetime import datetime
from PIL import Image


def requestURL(url, body=None, n=5):
    # 尝试n回访问url
    if n <= 1:
        print(f"访问{url}失败")
        raise ConnectionError
    try:
        e = requests.get(url, body, stream=True)
    except Exception as e:
        print("连接重试")
        n -= 1
        requestURL(url, body, n)
    return e


data = pd.read_csv('hubblesite.csv').values.tolist()
os.makedirs('static/images', exist_ok=True)
for i in data:
    primitive_str = ",".join(map(str, i))
    primitive_list = primitive_str.split(',')
    image_date_str = f"{primitive_list[2]}-{primitive_list[1]}-{primitive_list[0]}"
    image_date = datetime.strptime(image_date_str, "%Y-%b-%d")
    image_url_date = image_date.strftime("%B-%-d-2019").lower()
    image_name_date = image_date.strftime("%Y-%m-%d").lower()
    image_name = primitive_list[3].strip().replace(",", "-").replace(" ", "-").replace(".", "-").replace(
        "+", "-").replace("'", "-").replace("/", "-").replace("(", "").replace(")", "").lower()
    image_url = f"https://imagine.gsfc.nasa.gov/hst_bday/images/{image_url_date}-{image_name}"

    r = requestURL(f"{image_url}.jpg")
    if "text/html" in r.headers['Content-Type']:
        r = requestURL(f"{image_url}.png")
        Image.open(r.raw).convert('RGB').save(
            f"static/images/{image_name_date}-{image_name}.jpg")
    else:
        Image.open(r.raw).save(
            f"static/images/{image_name_date}-{image_name}.jpg")
    if "text/html" in r.headers['Content-Type']:
        print(f"{image_url}\t无法使用")
