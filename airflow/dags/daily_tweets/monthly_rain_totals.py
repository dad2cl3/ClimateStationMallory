import drawSvg as draw
import json
import pg8000 as pg
from paho.mqtt import publish
import base64
import io
import os, sys
import pandas as pd
# import plotly.express as pe
import plotly.graph_objects as go
from PIL import Image
from datetime import datetime
# from pytz import timezone
from pendulum import timezone

sys.path.append(os.path.dirname(__file__))

with open(os.path.dirname(os.path.abspath(__file__)) + '/' + 'config.json', 'r') as config_file:
    config = json.load(config_file)


# define constants
CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 675

TEXT_FONT_FAMILY = 'Roboto'

CALENDAR_MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov' 'Dec']


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


def get_monthly_rain_totals(conn):
    print('Getting monthly rain totals...')
    # cur = conn.cursor()
    sql = config['sql']['monthly_rain_totals']
    print('SQL: {0}'.format(sql))

    pandas_table = pd.read_sql_query(sql, conn)

    # print(data)

    return pandas_table


def build_graph_figure(pandas_data_table):
    print('Building graph figure...')
    df_x = pandas_data_table['str_month'].array
    df_y = pandas_data_table['month_total'].array

    fig = go.Figure(
        data=[go.Bar(
            x=df_x,
            y=df_y,
            text=df_x,
            # width=0.25
        )]

    )

    fig.update_layout(
        font_family=TEXT_FONT_FAMILY,
        title={
            'text': config['rain']['current_annual_title'].format(
                datetime.now(timezone('US/Eastern')).strftime('%Y')),
            'x': 0.5
        },
        xaxis={
            'title': 'Month'
        },
        yaxis={
            'title': 'Cumulative Rain (in)'
        },
        width=1200,
        height=675
    )

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
    message = 'Cumulative Monthly Rainfall for {0} in Wesley Chapel, NC'.format(datetime.now().astimezone(timezone('US/Eastern')).strftime('%Y'))
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


def build_monthly_rain_totals():
    print('Building tweet of monthly rain totals for current month...')
    # open database connection
    db = open_db_conn()

    # get current month daily rain totals
    monthly_rain_totals = get_monthly_rain_totals(db)

    # close database connection
    close_db_conn(db)

    # build graph figure
    image_jpg = build_graph_figure(monthly_rain_totals)
    image_jpg.show()
    # encode image
    # encoded_image = encode_image(image_jpg)

    # publish_tweet(encoded_image)

    return 'success'


if __name__ == '__main__':
    build_monthly_rain_totals()