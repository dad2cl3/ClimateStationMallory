import dash_bootstrap_components as dbc
#  import dash_html_components as html
from dash import html

ws_submenu = [
    html.Li(
        # use Row and Col components to position the chevrons
        dbc.Row(
            [
                dbc.Col(
                    "WeatherSense"
                ),
                dbc.Col(
                    html.I(
                        className="fas fa-chevron-right mr-3"
                    ),
                    width="auto"
                )
            ],
            className="my-1"
        ),
        style={
            "cursor": "pointer"
        },
        id="ws-submenu"
    ),
    dbc.Collapse(
        [
            dbc.NavLink(
                "Air Quality",
                href="/weathersense/airquality"
            ),
            dbc.NavLink(
                "Earthquake",
                href="/weathersense/earthquake"
            ),
            dbc.NavLink(
                "Lightning",
                href="/weathersense/lightning"
            ),
            dbc.NavLink(
                "SolarMAX2",
                href="/weathersense/solarmax2"
            )
        ],
        id="ws-submenu-collapse"
    )
]