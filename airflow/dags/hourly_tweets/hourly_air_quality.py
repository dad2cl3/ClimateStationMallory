import drawSvg as draw
import os, sys
import pg8000 as pg

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

from math import cos, radians, sin
from datetime import timedelta

from PIL import Image

import base64, io, json
from paho.mqtt import publish

sys.path.append(os.path.dirname(__file__))

# print(sys.path) # debug

with open(os.path.dirname(os.path.abspath(__file__)) + '/' + 'config.json', 'r') as config_file:
    config = json.load(config_file)


# define constants
CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 675

TEXT_FONT_FAMILY = 'Roboto'

# radius constants
ARC_RADIUS = 250
OUTER_TICK_RADIUS = ARC_RADIUS - 10
INNER_TICK_RADIUS = OUTER_TICK_RADIUS - 10
TICK_LABEL_RADIUS = INNER_TICK_RADIUS - 20
NEEDLE_RADIUS = TICK_LABEL_RADIUS - 20

# gauge constants
# GAUGE_CENTER_X = 0
GAUGE_CENTER_X = (CANVAS_WIDTH / 4) * -1
GAUGE_CENTER_Y = -50
GAUGE_STROKE_WIDTH = 8
GAUGE_ANCHOR_RADIUS = 10
GAUGE_ARC_LENGTH = 280
GAUGE_ARC_START = 230
GAUGE_ARC_END = (360 - GAUGE_ARC_LENGTH) + GAUGE_ARC_START
GAUGE_MIN = 0
GAUGE_MAX = 400

NEEDLE_STROKE_WIDTH = 5
TICK_STROKE_WIDTH = 2

# gauge
# major ticks
major_ticks = [0, 50, 100, 150, 200, 300, 400]
range_colors = ['green', 'yellow', 'orange', 'red', 'purple', 'maroon']

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


def get_current_aqi(conn):
    cur = conn.cursor()
    sql = config['sql']['hourly_air_quality']

    cur.execute(sql)
    data = cur.fetchall()

    # print(data[0][0]) # debug

    return data[0][0]


def get_current_aqi_data(conn):
    df = pd.read_sql(
        sql=config['sql']['hourly_air_quality'],
        con=conn,
        parse_dates=['reading_ts']
    )

    df['reading_ts'] = pd.to_datetime(df['reading_ts'])
    df.index = pd.DatetimeIndex(df['reading_ts'])
    df.sort_index(inplace=True)

    df['avg_aqi'] = df['aqi'].rolling('24H').mean()
    ts_max = df['reading_ts'].max()
    final_df = df[df['reading_ts'] > ts_max - timedelta(hours=24)]

    return final_df


def add_gauge_arcs(drawing):
    print('Adding colored gauge arcs...')
    for i in range(len(major_ticks) - 1):
        gauge_arc_start_ratio = major_ticks[i]/GAUGE_MAX
        gauge_arc_start_angle = GAUGE_ARC_START - (GAUGE_ARC_LENGTH * gauge_arc_start_ratio)

        gauge_arc_end_ratio = major_ticks[i + 1]/GAUGE_MAX
        gauge_arc_end_angle = GAUGE_ARC_START - (GAUGE_ARC_LENGTH * gauge_arc_end_ratio)

        arc = draw.Arc(
            cx=GAUGE_CENTER_X,
            cy=GAUGE_CENTER_Y,
            r=ARC_RADIUS,
            startDeg=gauge_arc_start_angle,
            endDeg=gauge_arc_end_angle,
            stroke=range_colors[i],
            stroke_width=GAUGE_STROKE_WIDTH,
            fill='none',
            cw=True
        )

        drawing.append(arc)


def add_major_ticks(drawing):
    print('Adding major ticks...')
    for major_tick in major_ticks:
        gauge_arc_ratio = major_tick/GAUGE_MAX
        gauge_arc_angle = GAUGE_ARC_START - (GAUGE_ARC_LENGTH * gauge_arc_ratio)
        # print('Gauge arc angle: {0}'.format(gauge_arc_angle)) # debug

        # calculate tick line start and end points
        tick_start_x = OUTER_TICK_RADIUS * cos(radians(gauge_arc_angle))
        tick_start_y = OUTER_TICK_RADIUS * sin(radians(gauge_arc_angle))
        tick_end_x = INNER_TICK_RADIUS * cos(radians(gauge_arc_angle))
        tick_end_y = INNER_TICK_RADIUS * sin(radians(gauge_arc_angle))

        sx = tick_start_x + GAUGE_CENTER_X
        sy = tick_start_y + GAUGE_CENTER_Y
        ex = tick_end_x + GAUGE_CENTER_X
        ey = tick_end_y + GAUGE_CENTER_Y

        tick_line = draw.Line(
            sx=sx,
            sy=sy,
            ex=ex,
            ey=ey,
            stroke='black',
            stroke_width=TICK_STROKE_WIDTH
        )

        drawing.append(tick_line)

        # calculate tick label position
        text_x = TICK_LABEL_RADIUS * cos(radians(gauge_arc_angle))
        text_y = TICK_LABEL_RADIUS * sin(radians(gauge_arc_angle))

        # print('({0}, {1})'.format(text_x, text_y)) # debug

        tick_label = draw.Text(
            x=text_x + GAUGE_CENTER_X,
            y=text_y + GAUGE_CENTER_Y,
            text=str(major_tick),
            color='black',
            fontSize=24,
            center=True,
            font_family=TEXT_FONT_FAMILY
        )

        drawing.append(tick_label)


def add_gauge_needle(aqi, drawing):
    # draw gauge anchor
    circle = draw.Circle(
        cx=GAUGE_CENTER_X,
        cy=GAUGE_CENTER_Y,
        r=GAUGE_ANCHOR_RADIUS,
        fill='black'
    )

    drawing.append(circle)

    gauge_aqi_ratio = int(aqi) / GAUGE_MAX
    gauge_aqi_angle = GAUGE_ARC_START - (GAUGE_ARC_LENGTH * gauge_aqi_ratio)

    needle_end_x = NEEDLE_RADIUS * cos(radians(gauge_aqi_angle))
    needle_end_y = NEEDLE_RADIUS * sin(radians(gauge_aqi_angle))
    # add needle
    line = draw.Line(
        sx=GAUGE_CENTER_X,
        sy=GAUGE_CENTER_Y,
        ex=needle_end_x + GAUGE_CENTER_X,
        ey=needle_end_y + GAUGE_CENTER_Y,
        stroke='black',
        stroke_width=NEEDLE_STROKE_WIDTH
    )

    drawing.append(line)


def add_aqi_value(aqi, drawing):
    print('Adding AQI value...')

    if aqi > 0 and aqi <= 50:
        aqi_color = 'green'
    elif aqi > 50 and aqi <= 100:
        aqi_color = 'yellow'
    elif aqi > 100 and aqi <= 150:
        aqi_color = 'orange'
    elif aqi > 150 and aqi <= 200:
        aqi_color = 'red'
    elif aqi > 200 and aqi <= 300:
        aqi_color = 'purple'
    elif aqi > 300:
        aqi_color = 'maroon'

    text = draw.Text(
        x=GAUGE_CENTER_X,
        y=-175 + GAUGE_CENTER_Y,
        text=str(aqi),
        fill=aqi_color,
        fontSize=100,
        center=True,
        font_family=TEXT_FONT_FAMILY
    )

    drawing.append(text)


def add_titles_text(drawing):
    # add title
    text = draw.Text(
        x=0,
        y=(CANVAS_HEIGHT / 2) * 0.90,
        center=True,
        text='Current Air Quality Index',
        stroke='black',
        stroke_width=0.25,
        fontSize=36,
        font_family=TEXT_FONT_FAMILY
    )

    drawing.append(text)

    # add secondary title
    text = draw.Text(
        x=0,
        y=(CANVAS_HEIGHT / 2) * 0.80,
        center=True,
        text='Wesley Chapel, NC',
        stroke='black',
        stroke_width=0.25,
        fontSize=24,
        font_family=TEXT_FONT_FAMILY
    )

    drawing.append(text)

    # link to AQI FAQ
    text = draw.Text(
        x=GAUGE_CENTER_X,
        y=-(CANVAS_HEIGHT / 2 - 30),
        text='https://www.airnow.gov/aqi/aqi-basics/',
        fontSize=16,
        center=True,
        font_family=TEXT_FONT_FAMILY
    )

    drawing.append(text)


def add_figure(curr_aqi_data, drawing):
    # optimize y axis boundaries
    y_axis_buffer = 2
    y_min = curr_aqi_data['aqi'].min() - y_axis_buffer
    y_max = curr_aqi_data['aqi'].max() + y_axis_buffer
    # print(y_min, y_max) # debug

    # build figure
    FIGURE_HEIGHT = 516 # convert to calculation
    FIGURE_WIDTH = CANVAS_WIDTH / 2

    fig = px.scatter(
        curr_aqi_data,
        x='reading_ts',
        y='aqi',
        # range_x=[x_min, x_max],
        range_y=[y_min, y_max],
        title='Air Quality Index Previous 24 Hours',
        labels={
            # 'reading_unix_ts': '<b><i>Time</i></b>',
            'reading_ts': '<b><i>Time</i></b>',
            'aqi': '<b><i>Air Quality Index</i></b>'
        },

        height=FIGURE_HEIGHT,
        width=FIGURE_WIDTH
    )

    fig.update_traces(
        marker=dict(
            size=4
        )
    )

    fig.update_layout(
        title={
            'x': 0.5
        },
        font_family=TEXT_FONT_FAMILY,
        title_font_size=24
    )

    fig.update_xaxes(title_font=dict(family=TEXT_FONT_FAMILY))
    fig.update_yaxes(title_font=dict(family=TEXT_FONT_FAMILY))

    fig.add_trace(
        go.Scatter(
            x=curr_aqi_data['reading_ts'],
            y=curr_aqi_data['avg_aqi'],
            mode='lines',
            showlegend=False
        )
    )

    fig.update_xaxes(title_font=dict(family=TEXT_FONT_FAMILY))
    fig.update_yaxes(title_font=dict(family=TEXT_FONT_FAMILY))

    # convert figure to image
    img_bytes = fig.to_image(format='jpg', scale=2)
    pil_img = Image.open(io.BytesIO(img_bytes))

    with io.BytesIO() as file_like_img:
        pil_img.save(file_like_img, 'JPEG')
        img_data = file_like_img.getvalue()

    # convert image to SVG image
    svg_img = draw.Image(
        x=0,
        y=-266, # this needs to be converted to a calculation
        width=FIGURE_WIDTH,
        height=FIGURE_HEIGHT,
        data=img_data,
        embed=True,
        mimeType='image/jpeg'
    )
    # add image to SVG
    drawing.append(svg_img)

    drawing.savePng('air_quality.png')

    return drawing


def encode_image(image_svg):
    with io.BytesIO() as file_like_img:
        image_svg.rasterize(file_like_img)
        img_data = file_like_img.getvalue()

    enc_img = base64.b64encode(img_data)
    enc_img = enc_img.decode('utf8')

    return enc_img


def publish_tweet(image):
    print('Publishing tweet to MQTT...')
    message = 'Current Air Quality Index in Wesley Chapel, NC'

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


def build_svg(aqi_value, aqi_data):
    # create drawing
    d = draw.Drawing(
        width=CANVAS_WIDTH,
        height=CANVAS_HEIGHT,
        origin='center'
    )
    # add background
    box = draw.Rectangle(
        x=-(CANVAS_WIDTH / 2),
        y=-(CANVAS_HEIGHT / 2),
        width=CANVAS_WIDTH,
        height=CANVAS_HEIGHT,
        stroke='black',
        fill='white'
    )

    d.append(box)

    add_gauge_arcs(d)
    add_major_ticks(d)
    add_gauge_needle(aqi_value, d)
    add_aqi_value(aqi_value, d)
    add_titles_text(d)
    add_figure(aqi_data, d)

    return d


def build_current_aqi():
    print('Building tweet of current AQI...')
    # open database connection
    db = open_db_conn()

    ## get current AQI
    # current_aqi = int(get_current_aqi(db))
    # print('Current AQI = {0}'.format(current_aqi))
    # get current AQI data
    curr_aqi_data = get_current_aqi_data(db)

    current_aqi = curr_aqi_data['aqi'].iloc[-1]

    # close database connection
    close_db_conn(db)

    # build SVG
    # image_svg = build_svg(current_aqi)
    image_svg = build_svg(current_aqi, curr_aqi_data)
    image_svg.saveSvg('air_quality.svg')

    # encode image
    enc_img = encode_image(image_svg)
    # publish tweet
    publish_tweet(enc_img)


if __name__ == '__main__':
    build_current_aqi()