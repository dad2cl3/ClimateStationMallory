import json

from dash import dcc
from dash import html

from main.sidebar import sidebar


def build_memory_stores():
    print('Building memory stores...')

    memory_stores = []

    # for topic in CACHE_TOPICS:
    for topic in config['cache']['topics']:
        memory_store = dcc.Store(
            id=topic,
            storage_type='memory'
        )

        memory_stores.append(memory_store)

    return memory_stores


# load config
with open('config.json', 'r') as config_file:
    config = json.load(config_file)


# build memory stores for getting data from cache
memory_stores = build_memory_stores()

# build the main layout
# content = dbc.Spinner(
#     id='mallory-spinner',
#     children=[
#         html.Div(id="page-content")
#     ],
#     color='primary',
#     type='grow',
#     size='lg',
#     fullscreen=True,
#     spinner_style={
#         'margin': '0',
#         'padding': '0'
#     }
# )

content = html.Div(id='page-content')

# content = dbc.Container(
#     id='page-content',
#     fluid=True
# )

layout_children = [
    dcc.Location(
        id='url'
    ),
    # cache refresh interval for in-memory stores
    dcc.Interval(
        id='minute-interval-component',
        interval=(120 * 1000),
        n_intervals=0
    ),
    # forecast refresh interval
    dcc.Interval(
        id='fifteen-minute-interval-component',
        interval=(15 * 60 * 1000),
        n_intervals=0
    )
]

# add memory stores to layout
for memory_store in memory_stores:
    layout_children.append(memory_store)

# add sidebar and content to layout
layout_children.append(sidebar)
layout_children.append(content)

layout = html.Div(
    children=layout_children
)
