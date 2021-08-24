import datetime
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from zhdate import ZhDate
import pandas as pd
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'YOUR_SECRET_KEY'

bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(FlaskForm):
    birthday = StringField(
        f'你的农历生日是？(仅支持{datetime.now().date()}这种格式的日期方式)', validators=[DataRequired()])
    submit = SubmitField('提交')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    birthday, image_name, image_date, image_file_name = None, None, None, None
    age = None
    birthday_list = []
    hubblesite_list = []
    hubblesite_dict = {}
    form = NameForm()
    if form.validate_on_submit():
        birthday = datetime.strptime(form.birthday.data, '%Y-%m-%d')
        birthday_list = create_gregorian_birthday(birthday)
        hubblesite_list, hubblesite_dict, name_dict = get_hubblesitelist(
            "hubblesite.csv")
        ret = [i for i in hubblesite_list if i in birthday_list]
        if ret:
            i = random.choice(ret)
            image_index = i.strftime("%Y-%m-%d").lower()
            image_file_name = hubblesite_dict[image_index]
            image_date = i.strftime("%Y年%m月%d日").lower()
            image_name = name_dict[image_index]
            age = i.year-ZhDate(birthday.year, birthday.month,
                                birthday.day).to_datetime().year

    return render_template('calendar.html', form=form, age=age, image_date=image_date, image_name=image_name, image_file_name=image_file_name)


def create_gregorian_birthday(birthday):
    lunar_birthday_list = []
    gregorian_birthday_list = []
    for i in range(birthday.year, datetime.now().year+1):
        lunar_birthday = f"{i}-{birthday.month}-{birthday.day}"
        lunar_birthday_list.append(
            datetime.strptime(lunar_birthday, '%Y-%m-%d'))
    for j in lunar_birthday_list:
        gregorian_birthday = ZhDate(j.year, j.month, j.day).to_datetime()
        gregorian_birthday_list.append(gregorian_birthday)
    return gregorian_birthday_list


def check_date(hubblesitelist, birthdaylist):
    ret = [i for i in hubblesitelist if i in birthdaylist]
    return ret


def get_hubblesitelist(file_name):
    df = pd.read_csv(file_name).values.tolist()
    hubblesitelist = []
    hubblesitedict = {}
    hubblesite_name_dict = {}
    for i in df:
        primitive_str = "".join(i)
        primitive_list = primitive_str.split('\t')
        image_date_str = f"{primitive_list[2]}-{primitive_list[1]}-{primitive_list[0]}"
        image_date = datetime.strptime(image_date_str, "%Y-%b-%d")
        hubblesitelist.append(image_date)
        image_name_date = image_date.strftime("%Y-%m-%d").lower()
        image_name = primitive_list[3].strip().replace("\t", "-").replace(" ", "-").replace(".", "-").replace(
            "+", "-").replace("'", "-").replace("/", "-").replace("(", "").replace(")", "").lower()
        hubblesitedict[image_name_date] = f"{image_name_date}-{image_name}.jpg"
        hubblesite_image_name = primitive_list[3].strip()
        hubblesite_name_dict[image_name_date] = hubblesite_image_name
    return hubblesitelist, hubblesitedict, hubblesite_name_dict
