import dash_bootstrap_components as dbc
# import dash_html_components as html
from dash import html

sidebar_header = dbc.Row(
    [
        dbc.Col(
            html.H4("Mallory", className="display-4")
        ),
        dbc.Col(
            [
                html.Button(
                    html.Span(
                        className="navbar-toggler-icon"
                    ),
                    className="navbar-toggler",
                    style={
                        "color": "rgba(0, 0, 0, 0.5)",
                        "border-color": "rgba(0, 0, 0, 0.1)"
                    },
                    id="navbar-toggle"
                ),
                html.Button(
                    html.Span(
                        className="navbar-toggler-icon"
                    ),
                    className="navbar-toggler",
                    style={
                        "color": "rgba(0, 0, 0, 0.5)",
                        "border-color": "rgba(0, 0, 0, 0.1)"
                    },
                    id="sidebar-toggle"
                )
            ],
            width="auto",
            align="center"
        )
    ]
)