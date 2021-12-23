import os, sys
import json
import pandas as pd
import pg8000 as pg
import plotly.express as pe
import io, base64
from PIL import Image
from paho.mqtt import publish
from datetime import datetime
from pendulum import timezone

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


def get_wind_rose_data(conn):
    print('Getting wind rose data...')
    sql = config['sql']['daily_wind_rose']
    print('SQL: {0}'.format(sql))

    pandas_table = pd.read_sql_query(sql, conn)

    return pandas_table


def build_wind_rose_figure(pandas_data_table):
    print('Building wind rose figure...')

    wind_rose_title = config['wind_rose']['title'].format(datetime.now(timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S %Z'))

    wind_rose = pe.bar_polar(
        pandas_data_table,
        r='frequency',
        theta='direction',
        color='strength',
        labels={
            'strength': 'Wind Speed (MPH)'
        },
        height=CANVAS_HEIGHT,
        width=CANVAS_WIDTH
    )

    wind_rose.update_layout(
        # font_family=TEXT_FONT_FAMILY,
        title={
            'text': wind_rose_title,
            'x': 0.5
        },
        polar=dict(
            angularaxis=dict(
                categoryarray=['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'])
        )
    )

    return wind_rose


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
    message = "Average Wind Speed and Direction Over Previous 24 Hours as of {0}".format(datetime.now().astimezone(timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S %Z'))
    # build MQTT payload
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
        client_id='wind_rose',
        qos=0
    )


def build_daily_wind_rose():
    print('Building daily wind rose...')
    db = open_db_conn()
    data = get_wind_rose_data(db)
    fig = build_wind_rose_figure(data)
    # fig.show() # only for testing
    enc_img = encode_image(fig)
    publish_tweet(enc_img)

if __name__ == '__main__':
    build_daily_wind_rose()