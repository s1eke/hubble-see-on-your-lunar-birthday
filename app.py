# app.py
import random
from flask import Flask, render_template,flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from utils import DateCollection, create_gregorian_birthday, get_hubblesitelist
from zhdate import ZhDate


app = Flask(__name__)
app.config['SECRET_KEY'] = 'YOUR_SECRET_KEY'

bootstrap = Bootstrap(app)
moment = Moment(app)

class BirthdayForm(FlaskForm):
    birthday = StringField(
        f'你的农历生日是？(仅支持{datetime.now().date()}这种格式的日期方式)', validators=[DataRequired()])
    submit = SubmitField('提交')


def parse_date(date_string, format_str):
    try:
        return datetime.strptime(date_string, format_str)
    except ValueError:
        return None

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    form = BirthdayForm()
    parameter = DateCollection()
    if form.validate_on_submit():
        parsed_date = parse_date(form.birthday.data, '%Y-%m-%d')
        if parsed_date:
            parameter.birthday = parsed_date
            gregorian_birthday = create_gregorian_birthday(parameter.birthday)

            hubblesite = get_hubblesitelist("hubblesite.csv")
            ret = [i for i in hubblesite.date_list if i in gregorian_birthday.date_list]
            if ret:
                i = random.choice(ret)
                image_index = i.strftime("%Y-%m-%d").lower()
                parameter.file = hubblesite.date_dict[image_index]
                parameter.date = i.strftime("%Y年%m月%d日").lower()
                parameter.image = hubblesite.name_dict[image_index]
                parameter.age = i.year - ZhDate(parameter.birthday.year, parameter.birthday.month, parameter.birthday.day).to_datetime().year
        else:
            flash("无效的日期格式，请使用YYYY-MM-DD格式")

    return render_template('calendar.html', form=form, parameter=parameter)

if __name__ == '__main__':
    app.run(debug=True)
