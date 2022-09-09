from time import time, localtime
import cityinfo
import config
from requests import get, post
from datetime import datetime, date


def get_access_token():
    # appId
    app_id = config.app_id
    # appSecret
    app_secret = config.app_secret
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    access_token = get(post_url).json()['access_token']
    # print(access_token)
    return access_token


def get_weather(province, city):
    # 城市id
    city_id = cityinfo.cityInfo[province][city]["AREAID"]
    # city_id = 101280101
    # 毫秒级时间戳
    t = (int(round(time() * 1000)))
    headers = {
        "Referer": "http://www.weather.com.cn/weather1d/{}.shtml".format(city_id),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    url = "http://d1.weather.com.cn/dingzhi/{}.html?_={}".format(city_id, t)
    response = get(url, headers=headers)
    response.encoding = "utf-8"
    response_data = response.text.split(";")[0].split("=")[-1]
    response_json = eval(response_data)
    print(response_json)
    weatherinfo = response_json["weatherinfo"]
    # 天气
    weather = weatherinfo["weather"]
    # 最高气温
    temp = weatherinfo["temp"]
    # 最低气温
    tempn = weatherinfo["tempn"]
    return weather, temp, tempn

def get_one():

    url = "http://www.wufazhuce.com/"
    response = get(url)
    response.encoding = "utf-8"
    response_data = response.text.split("fp-one-cita-wrapper")[1].split("fp-one-cita")[1].split(">")[2].split("<")[0]
    print(response_data)
    return response_data


def send_message(to_user, access_token, city_name, weather, max_temperature, min_temperature):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    week_list = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]
    year = localtime().tm_year
    month = localtime().tm_mon
    day = localtime().tm_mday
    today = datetime.date(datetime(year=year, month=month, day=day))
    week = week_list[today.isoweekday()]
    # 获取在一起的日子的日期格式
    love_year = int(config.love_date.split("-")[0])
    love_month = int(config.love_date.split("-")[1])
    love_day = int(config.love_date.split("-")[2])
    love_date = date(love_year, love_month, love_day)
    # 获取在一起的日期差
    love_days = str(today.__sub__(love_date)).split(" ")[0]
    # 获取生日的月和日
    birthday_month = int(config.birthday.split("-")[1])
    birthday_day = int(config.birthday.split("-")[2])
    # 今年生日
    year_date = date(year, birthday_month, birthday_day)
    # 计算生日年份，如果还没过，按当年减，如果过了需要+1
    if today > year_date:
        birth_date = date((year + 1), birthday_month, birthday_day)
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    elif today == year_date:
        birth_day = 0
    else:
        birth_date = year_date
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    data = {
        "touser": to_user,
        "template_id": config.template_id,
        "url": "http://weixin.qq.com/download",
        "topcolor": "#FF0000",
        "data": {
            "date": {
                "value": "{} {}".format(today, week),
                "color": "#00FFFF"
            },
            "city": {
                "value": city_name,
                "color": "#808A87"
            },
            "weather": {
                "value": weather,
                "color": "#ED9121"
            },
            "min_temperature": {
                "value": min_temperature,
                "color": "#00FF00"
            },
            "max_temperature": {
                "value": max_temperature,
                "color": "#FF6100"
            },
            "love_day": {
                "value": love_days,
                "color": "#87CEEB"
            },
            "birthday": {
                "value": birth_day,
                "color": "#FF8000"
            },
            "one" : {
                "value": get_one(),
                "color": "#808A87"
            }

        }
    }
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    print(headers)
    print(data)
    response = post(url, headers=headers, json=data)
    print(response.text)


if __name__ == '__main__':
    # 获取accessToken
    accessToken = get_access_token()
    # 接收的用户
    # user = config.user
    # 传入省份和市获取天气信息
    province, city = config.province, config.city
    weather, max_temperature, min_temperature = get_weather(province, city)

    # 接收的用户
    user_ids = config.users.split(",")

    # 公众号推送消息
    for user_id in user_ids:
        print('正在发送给 %s' % (user_id))
        send_message(user_id, accessToken, city, weather, max_temperature, min_temperature)