import dash_bootstrap_components as dbc
# import dash_html_components as html
from dash import html

sw_submenu = [
    html.Li(
        # use Row and Col components to position the chevrons
        dbc.Row(
            [
                dbc.Col(
                    "SkyWeather2"
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
        id="sw-submenu"
    ),
    dbc.Collapse(
        [
            dbc.NavLink(
                "Current Conditions",
                href="/"
            ),
            dbc.NavLink(
                "Host",
                href="/skyweather2/host"
            ),
            dbc.NavLink(
                "Indoor",
                href="/skyweather2/indoor"
            ),
            dbc.NavLink(
                "Outdoor",
                href="/skyweather2/outdoor"
            ),
        ],
        id="sw-submenu-collapse"
    )
]