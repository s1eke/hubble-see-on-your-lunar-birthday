



# utils.py
import pandas as pd
from datetime import datetime
from zhdate import ZhDate

class DateCollection:
    def __init__(self):
        self.date_list = []
        self.date_dict = {}
        self.name_dict = {}

def create_gregorian_birthday(birthday):
    lunar_birthday, gregorian_birthday = DateCollection(), DateCollection()
    for i in range(birthday.year, datetime.now().year + 1):
        lunar_birthday.str = f"{i}-{birthday.month}-{birthday.day}"
        lunar_birthday.date_list.append(
            datetime.strptime(lunar_birthday.str, '%Y-%m-%d'))
    for j in lunar_birthday.date_list:
        gregorian_birthday.str = ZhDate(j.year, j.month, j.day).to_datetime()
        gregorian_birthday.date_list.append(gregorian_birthday.str)
    return gregorian_birthday

def get_hubblesitelist(file_name):
    df = pd.read_csv(file_name).values.tolist()
    hubblesite = DateCollection()
    for i in df:
        primitive_str = ",".join(map(str, i))
        primitive_list = primitive_str.split(',')
        image_date_str = f"{primitive_list[2]}-{primitive_list[1]}-{primitive_list[0]}"
        image_date = datetime.strptime(image_date_str, "%Y-%b-%d")
        hubblesite.date_list.append(image_date)
        image_name_date = image_date.strftime("%Y-%m-%d").lower()
        image_name = primitive_list[3].strip().replace(",", "-").replace(" ", "-").replace(".", "-").replace(
            "+", "-").replace("'", "-").replace("/", "-").replace("(", "").replace(")", "").lower()
        hubblesite.date_dict[image_name_date] = f"{image_name_date}-{image_name}.jpg"
        hubblesite_image_name = primitive_list[3].strip()
        hubblesite.name_dict[image_name_date] = hubblesite_image_name
    return hubblesite
