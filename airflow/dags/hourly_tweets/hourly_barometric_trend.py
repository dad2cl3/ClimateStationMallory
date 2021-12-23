import base64, io, json
import pandas as pd
import pg8000 as pg
# import sklearn.linear_model
from PIL import Image
# import numpy, sklearn
import scipy.stats
import plotly.express as px
import plotly.graph_objs as go
from paho.mqtt import publish
import os, sys

# define constants
TEXT_FONT_FAMILY = 'Roboto'

sys.path.append(os.path.dirname(__file__))

# print(sys.path) # debug

with open(os.path.dirname(os.path.abspath(__file__)) + '/' + 'config.json', 'r') as config_file:
    config = json.load(config_file)


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


def get_barometric_trend_data(conn):
    print('Getting barometric trend...')
    # cur = conn.cursor()
    sql = config['sql']['barometric_trend']
    # print('SQL: {0}'.format(sql)) # debug

    pandas_table = pd.read_sql_query(sql, conn, index_col='reading_id', parse_dates='reading_ts')

    # print(data)

    return pandas_table


def build_graph_figure(pandas_data_table):
    print('Building barometric trend figure...')

    # print(pandas_data_table) # debug

    # x = numpy.array(pandas_data_table['reading_unix_ts']).reshape((-1, 1))
    #
    # x_label = numpy.array(pandas_data_table['reading_ts'])
    # x_label_min = x_label.min()
    # print(type(x_label_min))
    #
    # x_label_max = x_label.max()
    # print('X Axis Range: {0} - {1}'.format(x_label_min, x_label_max))
    # # print(x_label) # debug
    #
    # y = numpy.array(pandas_data_table['barometric_pressure'])
    # y_axis_buffer = 2
    # y_min = round(y.min()) - y_axis_buffer
    # y_max = round(y.max()) + y_axis_buffer
    # print('Y Axis Range: {0} - {1}'.format(y_min, y_max))
    #
    # model = sklearn.linear_model.LinearRegression().fit(x, y)
    # y_pred = model.predict(x)
    #
    # fig = go.Figure(
    #     data=[
    #         go.Scatter(
    #             # x=x_label,
    #             # x=x,
    #             y=y,
    #             mode='markers',
    #             marker=dict(
    #               size=1
    #             ),
    #             # name='Barometric Pressure'
    #             showlegend=False
    #         ),
    #         go.Scatter(
    #             # x=x_label,
    #             # x=x,
    #             y=y_pred,
    #             mode='lines',
    #             line=dict(
    #                 width=1
    #             ),
    #             # name='Linear Regression'
    #             showlegend=False
    #         )
    #     ]
    # )

    # fig.update_xaxes(
        # range=[x_label_min, x_label_max],
        # ticklabelmode='period',
        # tickformat='%I:%M'
    # )

    # fig.update_layout(
    #     yaxis_range=[y_min, y_max]
    # )

    # print(type(pandas_data_table['reading_unix_ts'])) # debug

    pandas_data_table.sort_values('reading_id')

    x = pandas_data_table['reading_ts']
    # x_min = x.min()
    # x_max = x.max()
    # print('X Axis Range: {0} - {1}'.format(x_min, x_max))

    y = pandas_data_table['barometric_pressure']
    y_axis_buffer = 2
    y_min = y.min() - y_axis_buffer
    y_max = y.max() + y_axis_buffer

    fig = px.scatter(
        pandas_data_table,
        # x='reading_unix_ts',
        x='reading_ts',
        y='barometric_pressure',
        # range_x=[x_min, x_max],
        range_y=[y_min, y_max],
        # trendline='ols',
        # trendline_color_override='red',
        title='Barometric Pressure Trend Over Previous Three Hours in Wesley Chapel, NC',
        labels={
            # 'reading_unix_ts': '<b><i>Time</i></b>',
            'reading_ts': '<b><i>Time</i></b>',
            'barometric_pressure': '<b><i>Barometric Pressure (hPa)</i></b>'
        },
        height=675,
        width=1200
    )

    fig.update_traces(
        marker=dict(
            size=2
        )
    )

    # trend = px.get_trendline_results(fig)
    # slope = trend.px_fit_results.iloc[0].params[1] * 60 * 60
    # print(slope) # debug


    lr = scipy.stats.linregress (
        x=pandas_data_table['reading_unix_ts'],
        y=pandas_data_table['barometric_pressure']
    )

    print(lr) # debug
    lr_slope = lr[0]
    lr_inter = lr[1]

    trend = lr_slope * 60 * 60

    print('Slope {0}'.format(lr_slope))
    print('Intercept Value {0}'.format(lr_inter))
    print('Trend {0}'.format(trend))

    pandas_data_table['lr_value'] = pandas_data_table['reading_unix_ts'] * lr_slope + lr_inter

    # print(pandas_data_table) # debug

    fig.add_trace(
        go.Scatter(
            x=pandas_data_table['reading_ts'],
            y=pandas_data_table['lr_value'],
            mode='lines',
            showlegend=False
        )
    )

    # fig.update_xaxes(
    #     tickformat='%H\n%M'
    # )

    fig.update_layout(
        title={
            'x': 0.5
        },
        font_family=TEXT_FONT_FAMILY,
        title_font_size=24
    )
    #
    fig.add_annotation(
        xref='paper',
        yref='paper',
        x=0.5,
        y=1,
        text='<b>Barometric Trend:</b> <i>{0:.2f} hPa/hr</i>'.format(trend),
        showarrow=False
    )

    # fig.write_image('barometric_trend.jpg') # debug
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
    message = 'Barometric Pressure Trend over Previous Three Hours in Wesley Chapel, NC'

    tweet = {
        'message': message,
        'hash_tags': config['tweet']['pandas_tags'],
        'media': image
    }

    publish.single(
        topic=config['mqtt']['topic'],
        payload=json.dumps(tweet),
        hostname=config['mqtt']['host'],
        port=1883,
        client_id='barometric_trend',
        qos=0
    )


def build_barometric_trend():
    print('Building barometric trend...')
    # open database connection
    db = open_db_conn()

    # get barometric trend
    barometric_trend = get_barometric_trend_data(db)

    # close database connection
    close_db_conn(db)

    # build graph figure
    image_jpg = build_graph_figure(barometric_trend)

    # encode image
    encoded_image = encode_image(image_jpg)

    publish_tweet(encoded_image)

    return 'success'


if __name__ == '__main__':
    build_barometric_trend()
