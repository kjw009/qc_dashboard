# File sharing
from sys import displayhook

# Data handling
import numpy as np
import pandas as pd
from datetime import timedelta
from datetime import datetime
import math
from itertools import cycle

# Data visualisation
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Dashboard modules
from dash import Input, Output

def colour_rate_callback(app, colours):
    # Callback function gets called whenever the product drop down value changes
    @app.callback(
        # Change figure attribute in weekly-right-first-time graph component
        Output("colour-graph", "figure"),
        Output("colour-graph-title", "children"),
        Output("colour-failure-graph", "style"),
        # Uses the value attribute from the product-drop-down component as the argument for the below function
        Input('memory', 'data'),
        Input("memory-title", "data"),
        # Start data parameter
        Input('date-selector', "start_date"),
        # End date parameter
        Input('date-selector', "end_date")
    )
    def update_colour_rate(json, title, start_date, end_date):
        # Process corresponding product QC data
        df = pd.read_json(json, orient='split')
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        palette = cycle(
            ['#d95f02', '#1b9e77', '#7570b3', '#e7298a', '#66a61e','#e6ab02','#a6761d', "#232323"])

        # Initiate start date
        if start_date == None:
            start_date = df.iloc[:, 0][1].split("T")[0]
        else:
            start_date = start_date

        for colour in df["Material Colour"].unique():
            # Initiate end date
            if end_date == None:
                curr_date = str(datetime.today()).split(" ")[0]
            else:
                curr_date = end_date

            pass_rates = []
            batches = []
            weeks = []

            while curr_date > start_date:
                curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
                monday_date = curr_date_dt - \
                    timedelta(days=curr_date_dt.weekday())

                df_sliced = df[str(monday_date): str(curr_date)]

                try:
                    pass_rate = df_sliced.groupby('Material Colour')['Colour'].value_counts(
                        normalize=True, dropna=False)[colour][np.nan] * 100
                except KeyError:
                    if len(df_sliced.loc[df_sliced['Material Colour'] == colour]) > 0:
                        pass_rate = 0
                    else:
                        pass_rate = np.nan

                # Only append data that is available
                if not math.isnan(pass_rate):
                    pass_rates.append(pass_rate)
                    weeks.append(monday_date)
                    batches.append(
                        len(df_sliced.loc[df_sliced['Material Colour'] == colour]))

                curr_date = str(monday_date - timedelta(days=1)).split(" ")[0]

            curr_colour = next(palette)

            fig.add_trace(go.Bar(x=weeks, y=batches,
                            name=colour + " Batches", marker_color=curr_colour), secondary_y=False)
            fig.add_trace(go.Scatter(x=weeks, y=pass_rates, name=colour + " RFT",
                                        line=dict(color=curr_colour, width=2,), marker=dict(size=10), mode='lines+markers', connectgaps=True), secondary_y=True)

        fig.data = fig.data[::-1]

        # fig.update_xaxes(showgrid=False)
        fig.update_yaxes(gridcolor=colours["border"], zerolinecolor=colours["border"])
        fig.update_yaxes(title_text="<b>Colour Pass Rate (%)<b>",
                            secondary_y=True, showgrid=False, range=[0, 105])
        fig.update_yaxes(
            title_text="<b>Number of Batch Produced<b>", secondary_y=False)

        # Whenever callback function is called, the figure will update using these presets
        fig.update_layout(
            barmode='stack',
            margin=dict(
                t=30,
                b=30,
                    r=30
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

        if len(df['Material Colour'].unique()) == 1:
            return fig, f"{title} Colour Pass Rate", {"display": "none"}
        return fig, f"{title} Colour Pass Rate", {}