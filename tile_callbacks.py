# File sharing
from sys import displayhook

# Data handling
import numpy as np
import pandas as pd
from datetime import date
from datetime import timedelta
from datetime import datetime
import math
from itertools import cycle

# Data visualisation
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Dashboard modules
from dash import Input, Output, html

def tile_callbacks(app, colours):
    # Callback to update RFT when product selected changes
    @app.callback(
        # Changes the children attribute from the rftStat component
        Output("rftStat", "children"),
        # The value attribute from the product-drop-down component is the arguement for the below function
        Input('memory', 'data'),
        # Start data parameter
        Input('date-selector', "start_date"),
        # End date parameter
        Input('date-selector', "end_date")
    )
    # Function to extract the RFT from the product
    def update_rft(product, start_date, end_date):
        # Extract df from selected product data and retrieve rft
        df = pd.read_json(product, orient='split')

        # Initiate dates
        if end_date == None:
            end_date = str(datetime.today()).split(" ")[0]
        if start_date == None:
            start_date = df.iloc[:, 0][1].split("T")[0]

        df = df[start_date:end_date]

        try:
            rft = str(round((df['Result'].value_counts(
                normalize=True)['Pass']*100), 1)) + "%"
        except KeyError:
            if len(df) > 0:
                rft = 0
            else:
                rft = np.nan

        return rft

    # Callback to update the RFT for this week
    @app.callback(
        # Changes the children attribute from the rftStat component
        Output("rftWeek", "children"),
        # The value attribute from the product-drop-down component is the arguement for the below function
        Input('memory', 'data')
    )
    # Function to extract the RFT from the product
    def update_rft(product):
        # Extract df from selected product data and retrieve rft
        df = pd.read_json(product, orient='split')
        df = df[str(date.today() - timedelta(days=date.today().weekday()))            :str(date.today())]

        try:
            rft = round((df['Result'].value_counts(
                normalize=True)['Pass']*100), 1)
        except KeyError:
            if len(df) > 0:
                rft = 0
            else:
                rft = np.nan

        if math.isnan(rft):
            return "No Data"
        return str(rft) + "%"

    # Call back to update RFT for this month
    @app.callback(
        # Changes the children attribute from the rftStat component
        Output("rftMonth", "children"),
        # The value attribute from the product-drop-down component is the arguement for the below function
        Input('memory', 'data')
    )
    # Function to extract the RFT from the product
    def update_rft(product):
        # Extract df from selected product data and retrieve rft
        df = pd.read_json(product, orient='split')
        df = df[str(date.today() - timedelta(days=date.today().day)):str(date.today())]

        try:
            rft = round((df['Result'].value_counts(
                normalize=True)['Pass']*100), 1)
        except KeyError:
            if len(df) > 0:
                rft = 0
            else:
                rft = np.nan

        if math.isnan(rft):
            return "No Data"
        return str(rft) + "%"


    @app.callback(
        # Changes the children attribute from the rftStat component
        Output("multi-rft", "children"),
        # The value attribute from the product-drop-down component is the arguement for the below function
        Input('memory', 'data'),
            # Start data parameter
        Input('date-selector', "start_date"),
        # End date parameter
        Input('date-selector', "end_date")
    )
    # Function to extract the RFT from the product
    def update_rft(product, start_date, end_date):
        # Extract df from selected product data and retrieve rft
        df = pd.read_json(product, orient='split')
        
        # Initiate dates
        if end_date == None:
            end_date = str(datetime.today()).split(" ")[0]
        if start_date == None:
            start_date = df.iloc[:, 0][1].split("T")[0]

        df = df[start_date:end_date]

        elements = []

        for colour in df["Material Colour"].unique():
            rft = round(df.groupby("Material Colour")[
                "Result"].value_counts(normalize=True)[colour]["Pass"], 3) * 100
            element = html.Div(children=[html.Div(
                className="Statistic",
                children=f"{str(rft)}%"
            ),
                html.P(
                className="TileTitle",
                children=f"{colour} RFT"
            )]
            )

            elements.append(element)

        return html.Div(
            className="MultiStatTile",
            style={
                "color" : colours["text"]
            },
            children=[
                html.Div(
                    className="StyledDataCard",
                    style={
                        "borderColor": colours["border"],
                        "color" : colours["text"],
                        "backgroundColor" : colours["content"]
                    },
                    children=[
                        html.Div(
                            className="HandleWrapper",
                            children=[
                                html.Div(
                                    id="MultiRft",
                                    className="DataCardContent",
                                    children=elements
                                ),
                                html.Div(
                                    className="Handle",
                                    style={
                                        "backgroundColor":colours["text"]
                                    }
                                )
                            ]
                        )
                    ]
                )
            ]
        )


    @app.callback(
        # Changes the children attribute from the rftStat component
        Output("multi-rft-week", "children"),
        # The value attribute from the product-drop-down component is the arguement for the below function
        Input('memory', 'data')
    )
    # Function to extract the RFT from the product
    def update_rft(product):
        # Extract df from selected product data and retrieve rft
        df = pd.read_json(product, orient='split')
        df = df[str(date.today() - timedelta(days=date.today().weekday()))            :str(date.today())]

        elements = []

        for colour in df["Material Colour"].unique():
            try:
                rft = round(df.groupby("Material Colour")[
                    "Result"].value_counts(normalize=True)[colour]["Pass"], 3) * 100
            except KeyError:
                rft = 0

            element = html.Div(children=[html.Div(
                className="Statistic",
                children=f"{str(rft)}%"
            ),
                html.P(
                className="TileTitle",
                children=f"This Week {colour} RFT"
            )]
            )

            elements.append(element)

        return html.Div(
            className="MultiStatTile",
            style={
                "color" : colours["text"]
            },
            children=[
                html.Div(
                    className="StyledDataCard",
                    style={
                        "borderColor": colours["border"],
                        "color" : colours["text"],
                        "backgroundColor" : colours["content"]
                    },
                    children=[
                        html.Div(
                            className="HandleWrapper",
                            children=[
                                html.Div(
                                    id="MultiRft",
                                    className="DataCardContent",
                                    children=elements
                                ),
                                html.Div(
                                    className="Handle",
                                    style={
                                        "backgroundColor":colours["text"]
                                    }
                                )
                            ]
                        )
                    ]
                )
            ]
        )


    @app.callback(
        # Changes the children attribute from the rftStat component
        Output("multi-rft-month", "children"),
        # The value attribute from the product-drop-down component is the arguement for the below function
        Input('memory', 'data')
    )
    # Function to extract the RFT from the product
    def update_rft(product):
        # Extract df from selected product data and retrieve rft
        df = pd.read_json(product, orient='split')
        df = df[str(date.today() - timedelta(days=date.today().day))            :str(date.today())]

        elements = []

        for colour in df["Material Colour"].unique():
            try:
                rft = round(df.groupby("Material Colour")[
                    "Result"].value_counts(normalize=True)[colour]["Pass"], 3) * 100
            except:
                rft = 0

            element = html.Div(children=[html.Div(
                className="Statistic",
                children=f"{str(rft)}%"
            ),
                html.P(
                className="TileTitle",
                children=f"This Month {colour} RFT"
            )]
            )

            elements.append(element)

        return html.Div(
            className="MultiStatTile",
            style={
                "color" : colours["text"]
            },
            children=[
                html.Div(
                    className="StyledDataCard",
                    style={
                        "borderColor": colours["border"],
                        "color" : colours["text"],
                        "backgroundColor" : colours["content"]
                    },
                    children=[
                        html.Div(
                            className="HandleWrapper",
                            children=[
                                html.Div(
                                    id="MultiRft",
                                    className="DataCardContent",
                                    children=elements
                                ),
                                html.Div(
                                    className="Handle",
                                    style={
                                        "backgroundColor":colours["text"]
                                    }
                                )
                            ]
                        )
                    ]
                )
            ]
        )

    @app.callback(
        Output("multi-stat-div", "style"),
        Output("colour-drop-down-1", "style"),
        Output("colour-drop-down-2", "style"),
        Output("colour-drop-down-3", "style"),
        Input("memory", "data")
    )
    def display_multi_rft(product):
        df = pd.read_json(product, orient='split')

        if len(df['Material Colour'].unique()) == 1:
            return {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}
        return {}, {}, {}, {}


