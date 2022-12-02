# File sharing
import os
from sys import displayhook

# Data handling
import pandas as pd
from datetime import date
from datetime import datetime

# Dashboard modules
from dash import Dash, Input, Output, html, dcc

# Imports from other files
from data_pipeline import process_product_data
from my_dash_components import graph_element, stat_tile_element
from callbacks.rft_callback import rft_callback
from callbacks.colour_rate_callback import colour_rate_callback
from callbacks.tile_callbacks import tile_callbacks
from callbacks.specification_distribution_callback import specification_distribution_callback
from callbacks.failure_pie_chart_callback import failure_pie_chart_callback
from callbacks.spec_trend_graph_callback import spec_trend_graph_callback

# Disable warnings
import warnings
warnings.filterwarnings('ignore')

# Declare list of products
qc_excels = os.listdir(
    "G:\Quality Control\Quality Management System\QC Docs\QC\QC Check Sheets\QC Completed Check Sheets\Products")
products = [" ".join(product.split(" ")[:2]) for product in qc_excels]

# Dict for indicate product to file. Key : Product => Value : Filename
product_file_dict = {}
for file_index, product in enumerate(products):
    product_file_dict[product] = qc_excels[file_index]

# Colours
colours = {
    "content": "#F2E9DD",
    "background": "#E8DAC5",
    "border": "#d3bd98",
    "text": "#493D32",
    "accent": "#232323",
    "marker": "#d95f02"
}

# Dash components
# SVG Sika Logo
sika_logo = html.Img(
    id="sika-logo",
    src="assets\Logo_Sika_Ag.svg.png"
)

# Dropdown to select product QC data
product_dropdown = dcc.Dropdown(
    options=products,
    value=products[0],
    id="product-drop-down",
)

# Date picker range component
date_selector = dcc.DatePickerRange(
    id="date-selector",
    start_date_placeholder_text="Start Period",
    end_date_placeholder_text=str(date.today()),
    calendar_orientation='vertical',
)

snapshot_date = html.P(
    id="snapshot-date"
)

# Specification drop down
spec_drop_down_dist = dcc.Dropdown(
    id="spec-drop-down-dist",
    className="SpecDropDown",
    value="Spread /mm",
)

# Specification drop down
spec_drop_down_trend = dcc.Dropdown(
    id="spec-drop-down-trend",
    className="SpecDropDown",
    value="Spread /mm",
)

# Drop Down for Colours
spec_dist_colour_drop_down = dcc.Dropdown(
    id="colour-drop-down-1",
    className="SpecDropDown",
    value="All"
)

spec_trend_colour_drop_down = dcc.Dropdown(
    id="colour-drop-down-2",
    className="SpecDropDown",
    value="All"
)

pie_colour_drop_down = dcc.Dropdown(
    id="colour-drop-down-3",
    className="SpecDropDown",
    value="All"
)

# Graph elements
rft_graph = graph_element("rft-title", "weekly-right-first-time")
spec_dist_graph = graph_element(
    "spec-title", "spec-distribution", spec_drop_down_dist, spec_dist_colour_drop_down)
failure_code_pie = graph_element("pie-title", "pie-chart", pie_colour_drop_down)
spec_trend_graph = graph_element(
    "spec-trend-title", "spec-trend-graph", spec_drop_down_trend, spec_trend_colour_drop_down)
colour_failure_rate_graph = graph_element("colour-graph-title", "colour-graph")

# Initialise dashboard
app = Dash(__name__)

# Main Html Div. Children will its CSS properties such as background color.
app.layout = html.Div(
    id="layout",
    style={
        "backgroundColor": colours["background"],
        "color": colours["text"]
    },
    children=[
        # DCC memory store element to store corresponding product dataframes, product title and the conforming limits for the selected product
        dcc.Store(id='memory'),
        dcc.Store(id='memory-title'),
        dcc.Store(id="memory-limits"),
        # DCC interval component to refresh data every 30 seconds
        dcc.Interval(
            id="interval-component",
            interval=30000,
            n_intervals=0
        ),
        # Header
        html.H1(
            id="header",
            style={
                "backgroundColor": colours["content"]
            },
            children=[
                sika_logo,
                "Wishaw QC Dashboard",
                product_dropdown,
                date_selector,
                snapshot_date
            ],
        ),
        # Div to hold dash components
        html.Div(
            id="content",
            children=[
                html.Div(
                    id="tile-div",
                    children=[
                        html.Div(
                            id="single-stat-div",
                            children=[
                                stat_tile_element
                                (
                                    "rftStat",
                                    "Right First Time",
                                    colours["content"],
                                    colours["border"],
                                    colours["text"]
                                ),
                                stat_tile_element
                                (
                                    "rftWeek",
                                    "This Week RFT",
                                    colours["content"],
                                    colours["border"],
                                    colours["text"]
                                ),
                                stat_tile_element
                                (
                                    "rftMonth",
                                    "This Month RFT",
                                    colours["content"],
                                    colours["border"],
                                    colours["text"]
                                )]),
                        html.Div(
                            id="multi-stat-div",
                            children=[
                                html.Div(
                                    id="multi-rft"
                                ),
                                html.Div(
                                    id="multi-rft-week"
                                ),
                                html.Div(
                                    id="multi-rft-month"
                                )
                            ]
                        ),
                        failure_code_pie,
                        spec_trend_graph
                    ]
                ),
                html.Div(
                    id="graphs-div",
                    children=[
                        rft_graph,
                        spec_dist_graph,
                        html.Div(
                            id="colour-failure-graph",
                            children=[colour_failure_rate_graph]
                        )
                    ],
                )
            ]
        )
    ])

# Callback function that is triggered when the selected product from the drop down component is changed. Updates the data of all dcc.Store components
@app.callback(
    # dcc.Store to keep df of product in memory
    Output("memory", "data"),
    # dcc.Store to keep name of product in memory
    Output("memory-title", "data"),
    # dcc.Store to keep conforming limits of product in memory
    Output("memory-limits", "data"),
    # Changes the snapshot date of data
    Output("snapshot-date", "children"),
    Input("product-drop-down", "value"),
    # Call functions whenever the number of intervals is incremented
    Input("interval-component", "n_intervals")
)
# Function to retrieve and return data from selected product and
def memory_output(product, n_intervals):
    # Extract df from product file
    df, limits = process_product_data(product_file_dict[product])
    # Return
    return df.to_json(date_format='iso', orient='split'), product, limits, f"QC Snapshot Date : {datetime.today()}"

# Display start date and end date if no dates were initially selected
@app.callback(
    # Update start and end date attributes
    Output("date-selector", "start_date_placeholder_text"),
    Input("memory", "data")
)
def display_start_date(json):
    df = pd.read_json(json, orient='split')
    # Return
    return df.iloc[:, 0][1].split("T")[0]

# Graph callbacks
rft_callback(app, colours)
colour_rate_callback(app, colours)
specification_distribution_callback(app, colours)
failure_pie_chart_callback(app, colours)
spec_trend_graph_callback(app, colours)

# Tile callbacks
tile_callbacks(app, colours)

# Run server
if __name__ == '__main__':
    print("\nRunning dashboard server...")
    app.run_server(debug=True)
