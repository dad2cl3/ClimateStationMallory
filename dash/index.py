import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output, State

import json
from app import app

from layout import layout
import callbacks

# import the pages to support the callbacks
import skyweather2.current
import skyweather2.host
import skyweather2.indoor
import skyweather2.outdoor

import weathersense.airquality
import weathersense.earthquake
import weathersense.lightning
import weathersense.solarmax2

# import config file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# set the layout for the Dash app
app.layout = layout

# export server to gunicorn
server = app.server


# register callback to support page navigation
@app.callback(
    Output(
        "page-content",
        "children"
    ),
    Input(
        "url",
        "pathname"
    )
)
def render_page_content(pathname):
    # TODO: fix WeatherSense pages
    print('Rendering content for path {0}...'.format(pathname))
    # TODO: Should cache connection functions be in main.utilities?
    # open cache connection
    cache = callbacks.get_cache_connection()

    if pathname == '/':
        return skyweather2.current.build_current_page(cache)
    elif pathname == '/skyweather2/host':
        return skyweather2.host.build_host_page(cache)
    elif pathname == '/skyweather2/indoor':
        return skyweather2.indoor.build_indoor_page(cache)
    elif pathname == "/skyweather2/outdoor":
        return skyweather2.outdoor.build_outdoor_page(cache)
    elif pathname == "/weathersense/air-quality":
        return weathersense.airquality.build_airquality_page(cache)
    elif pathname == "/weathersense/earthquake":
        return weathersense.earthquake.build_earthquake_page(cache)
    elif pathname == "/weathersense/lightning":
        return weathersense.lightning.build_lightning_page(cache)
    elif pathname == "/weathersense/solarmax2":
        return weathersense.solarmax2.build_solarmax2_page(cache)

    callbacks.close_cache_connection(cache)

    # if the user tries to reach a different page, return a 404 message
    return dbc.Container(
        [
            html.H1(
                "404: Not found",
                className="text-danger"
            ),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognized...")
        ]
    )


if __name__ == "__main__":
    try:
        app.run_server(
            port=config['server']['port'],
            host=config['server']['host'],
            debug=True
        )
    except KeyboardInterrupt as ki:
        print('Closing down Dash application...')
