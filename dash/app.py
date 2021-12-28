import dash
import dash_bootstrap_components as dbc
# from dash import html

# link FontAwesome to gt chevron icons
FA = "https://use.fontawesome.com/releases/v5.8.1/css/all.css"

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.MATERIA, FA],
    # meta_tags=[
    #     {
    #         'name': 'viewport',
    #         'content': 'width=device-width, initial-scale=1'
    #         # 'content': 'width-device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5'
    #     }
    # ],
    suppress_callback_exceptions=True
)

app.title = 'Climate Station Mallory'
