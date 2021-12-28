import dash_bootstrap_components as dbc
# import dash_html_components as html
from dash import html

from main.sidebar_header import sidebar_header
# from main.default_submenu import default_submenu
from main.sw_submenu import sw_submenu
from main.ws_submenu import ws_submenu

sidebar = html.Div(
    [
        sidebar_header,
        dbc.Collapse(
            dbc.Nav(
                # default_submenu + sw_submenu + ws_submenu,
                sw_submenu + ws_submenu,
                vertical=True
            ),
            id="collapse"
        )
    ],
    id="sidebar",
    className="collapsed"
)