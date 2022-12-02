# Data handling
import numpy as np
import pandas as pd
from datetime import date
from datetime import timedelta
from datetime import datetime
import math
from itertools import cycle

# Data visualisation
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Dashboard modules
from dash import Dash, Input, Output, html, dcc

def spec_trend_graph_callback(app, colours):
        # Callback function to update options attribute for specificationDropDown component using the product data columns
    @app.callback(
        # Updates options attribute for the specificationDropwDown component
        Output("spec-drop-down-trend", "options"),
        Output("colour-drop-down-2", "options"),
        Input("memory", "data")
    )
    # Function to retrieve column names from the QC product data
    def spec_options(product):
        # Extract df from product and retrieve columns
        df = pd.read_json(product, orient='split')
        
        columns = [column for column in df.columns if df.dtypes[column]
                == "int64" or df.dtypes[column] == "float64"]
        
        colours = [colour for colour in df["Material Colour"].unique()]
        colours.append("All")
        
        return columns, colours
    # Callback function gets triggered whenever the date and/or specification value is changed
    @app.callback(
    # Changes figure attribute for specDistribution graph
    Output("spec-trend-graph", "figure"),
    Output("spec-trend-title", "children"),
    # Uses the value attribute from the product-drop-down element as the argument for the below function
    Input('memory', 'data'),
    Input('memory-title', 'data'),
    Input('memory-limits', 'data'),
    # The value attribute for the spec-drop-down element is the argument for the below function
    Input('spec-drop-down-trend', 'value'),
    Input('colour-drop-down-2', 'value'),
    # Start data parameter
    Input('date-selector', "start_date"),
    # End date parameter
    Input('date-selector', "end_date")
    )
    def update_spec(product, title, limits, spec, colour, start_date, end_date):
        # Extract df from product and retrieve columns
        df = pd.read_json(product, orient='split')

        # Initiate dates
        if end_date == None:
            end_date = str(datetime.today()).split(" ")[0]
        if start_date == None:
            start_date = df.iloc[:, 0][1].split("T")[0]

        df = df[start_date:end_date].loc[df[start_date:end_date][spec] > 1]
        df.iloc[:, 0] = [date.split("T")[0] for date in df.iloc[:, 0]]

        if colour != "All":
            df = df.loc[df['Material Colour'] == colour]
            
        fig = px.line(
            df, 
            x=range(len(df)),
            y=spec,
            markers=True,
            custom_data=[df.columns[0]]
        )

        fig.update_traces(
            line=dict(color=colours["marker"], width=2),
            marker=dict(
                color=colours["accent"],
                symbol="x",
                size=13
            ),
            hovertemplate='Spread: %{y} /mm <br>Date of Manufacture: %{customdata[0]}<br>'
        )

        # Check if specification has available conforming limits and add H-Lines of the corresponding values into the graph
        if spec in limits.keys():
            fig.add_hline(y=limits[spec][0], line_color="rgb(216,40,47)")
            fig.add_hline(y=limits[spec][1], line_color="rgb(210,40,47)")

        # fig.update_xaxes(showgrid=False)
        fig.update_yaxes(gridcolor=colours["border"])
        fig.update_xaxes(gridcolor=colours["border"], showgrid=False,
                            showticklabels=False, zeroline=False)
        fig.update_yaxes(title_text=f"<b>{spec}<b>")

        # Whenever callback function is called, the figure will update using these presets
        fig.update_layout(
            margin=dict(
                t=10,
                b=10,
                l=100
            ),
            legend=dict(
                yanchor="top",
                y=0.89,
                xanchor="left",
                x=0.01
            ),
            title_font_family="Abel",
            plot_bgcolor=colours["content"],
            paper_bgcolor=colours["content"],
            font_color=colours["accent"],
            font_family="Abel"
        )

        # Return plotly figure
        spec = spec.split(" ")[0]
        return fig, f"{title} {spec} Trend"