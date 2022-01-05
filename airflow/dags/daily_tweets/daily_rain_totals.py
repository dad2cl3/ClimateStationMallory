import drawSvg as draw
import json
import pg8000 as pg
from paho.mqtt import publish
import base64
import io
import os, sys
import pandas as pd
import plotly.express as pe
# import plotly.graph_objects as go
from PIL import Image
from datetime import datetime
# from pytz import timezone
from pendulum import now, timezone
from calendar import monthrange


sys.path.append(os.path.dirname(__file__))

with open(os.path.dirname(os.path.abspath(__file__)) + '/' + 'config.json', 'r') as config_file:
    config = json.load(config_file)


# define constants
CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 675

TEXT_FONT_FAMILY = 'Roboto'


def open_db_conn():
    conn = pg.connect(
        host=config['database']['host'],
        port=config['database']['port'],
        user=config['database']['user'],
        password=config['database']['password'],
        database=config['database']['db']
    )

    return conn


def close_db_conn(conn):
    conn.close()


def get_current_month_days():
    current_date = now('US/Eastern')
    print(current_date)
    current_year = current_date.year
    print(current_year)
    current_month = current_date.month
    print(current_month)
    days = monthrange(current_year, current_month)[1]

    return days


def get_daily_rain_totals(conn):
    print('Getting daily rain totals...')
    # cur = conn.cursor()
    sql = config['sql']['daily_rain_totals']
    print('SQL: {0}'.format(sql))

    pandas_table = pd.read_sql_query(sql, conn)

    # get days in month
    # days = get_current_month_days()

    # last_day = int(pandas_table['day'].max())
    # print(last_day)

    # for day in range(last_day + 1, days + 1):
         #pandas_table = pandas_table.append({'day': day, 'daily_total': 0}, ignore_index=True)

    # print(pandas_table)

    return pandas_table


def build_graph_figure(pandas_data_table):
    print('Building graph figure...')

    last_day = int(pandas_data_table['day'].max())
    x = list(range(1, last_day + 1))
    print(x)

    fig = pe.bar(
        pandas_data_table,
        x='day',
        y='daily_total',
        color='daily_total',
        color_continuous_scale=pe.colors.sequential.Viridis,
        hover_data=['day', 'daily_total'],
        labels={'day': 'Day', 'daily_total': 'Cumulative Rain (in)'},
        height=CANVAS_HEIGHT,
        width=CANVAS_WIDTH
    )

    fig.update_layout(
        title={
            'text': config['rain']['current_month_title'].format(datetime.now().astimezone(timezone('US/Eastern')).strftime('%B %Y')),
            'x': 0.5
        },
        xaxis=dict(
            dtick=1
        )
    )

    # fig.write_image('daily_rain_totals.jpg')

    return fig


def encode_image(graph_figure):
    print('Encoding graph figure...')

    img_bytes = graph_figure.to_image(format='jpg')
    pil_img = Image.open(io.BytesIO(img_bytes))

    with io.BytesIO() as file_like_img:
        pil_img.save(file_like_img, 'JPEG')
        img_data = file_like_img.getvalue()

    encoded_image = base64.b64encode(img_data)
    encoded_image = encoded_image.decode('utf8')

    return encoded_image


def publish_tweet(image):
    print('Publishing tweet to MQTT...')
    message = 'Cumulative Daily Rainfall for {0} in Wesley Chapel, NC'.format(datetime.now().astimezone(timezone('US/Eastern')).strftime('%B, %Y'))

    tweet = {
        # 'message': config['tweet']['message'],
        'message': message,
        'hash_tags': config['tweet']['hash_tags'],
        'media': image
    }

    publish.single(
        topic=config['mqtt']['topic'],
        payload=json.dumps(tweet),
        hostname=config['mqtt']['host'],
        port=1883,
        client_id='current_conditions',
        qos=0
    )


def build_daily_rain_totals():
    print('Building tweet of daily rain totals for current month...')
    # open database connection
    db = open_db_conn()

    # get number days current month
    today = pd.Timestamp.now(tz='US/Eastern')
    num_days = today.days_in_month

    days = []

    for i in range(1, num_days + 1):
        days.append(i)
    days_df = pd.DataFrame(data=days, columns=['day'])

    # get current month daily rain totals
    daily_rain_totals = get_daily_rain_totals(db)
    merged_daily_rain_totals = days_df.combine_first(daily_rain_totals).fillna(0)

    # close database connection
    close_db_conn(db)

    # build graph figure
    # image_jpg = build_graph_figure(daily_rain_totals)
    image_jpg = build_graph_figure(merged_daily_rain_totals)
    # image_jpg.show() # debug

    # encode image
    encoded_image = encode_image(image_jpg)

    publish_tweet(encoded_image)

    return 'success'


if __name__ == '__main__':
    build_daily_rain_totals()