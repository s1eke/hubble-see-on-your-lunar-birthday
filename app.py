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


class collection():
    def __init__(self):
        self.list = []
        self.date_dict = {}
        self.name_dict = {}
        self.str = None
        self.birthday = None
        self.image = None
        self.date = None
        self.file = None
        self.age = None


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
    birthday, hubblesite, parameter = collection(), collection(), collection()
    form = NameForm()
    if form.validate_on_submit():
        parameter.birthday = datetime.strptime(form.birthday.data, '%Y-%m-%d')
        print(datetime.strptime(form.birthday.data, '%Y-%m-%d'))
        birthday = create_gregorian_birthday(parameter.birthday)

        hubblesite = get_hubblesitelist(
            "hubblesite.csv")
        ret = [i for i in hubblesite.list if i in birthday.list]
        if ret:
            i = random.choice(ret)
            print(parameter.birthday)
            image_index = i.strftime("%Y-%m-%d").lower()
            parameter.file = hubblesite.date_dict[image_index]
            parameter.date = i.strftime("%Y年%m月%d日").lower()
            parameter.image = hubblesite.name_dict[image_index]
            parameter.age = i.year-ZhDate(parameter.birthday.year, parameter.birthday.month,
                                          parameter.birthday.day).to_datetime().year

    return render_template('calendar.html', form=form, parameter=parameter)


def create_gregorian_birthday(birthday):
    lunar_birthday, gregorian_birthday = collection(), collection()
    for i in range(birthday.year, datetime.now().year+1):
        lunar_birthday.str = f"{i}-{birthday.month}-{birthday.day}"
        lunar_birthday.list.append(
            datetime.strptime(lunar_birthday.str, '%Y-%m-%d'))
    for j in lunar_birthday.list:
        gregorian_birthday.str = ZhDate(j.year, j.month, j.day).to_datetime()
        gregorian_birthday.list.append(gregorian_birthday.str)
    return gregorian_birthday


def get_hubblesitelist(file_name):
    df = pd.read_csv(file_name).values.tolist()
    hubblesite = collection()
    for i in df:
        primitive_str = ",".join(map(str, i))
        primitive_list = primitive_str.split(',')
        image_date_str = f"{primitive_list[2]}-{primitive_list[1]}-{primitive_list[0]}"
        image_date = datetime.strptime(image_date_str, "%Y-%b-%d")
        hubblesite.list.append(image_date)
        image_name_date = image_date.strftime("%Y-%m-%d").lower()
        image_name = primitive_list[3].strip().replace(",", "-").replace(" ", "-").replace(".", "-").replace(
            "+", "-").replace("'", "-").replace("/", "-").replace("(", "").replace(")", "").lower()
        hubblesite.date_dict[image_name_date] = f"{image_name_date}-{image_name}.jpg"
        hubblesite_image_name = primitive_list[3].strip()
        hubblesite.name_dict[image_name_date] = hubblesite_image_name
    return hubblesite
