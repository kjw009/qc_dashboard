# Data handling
import numpy as np
import pandas as pd
from datetime import datetime
from itertools import cycle

# Data visualisation
import plotly.graph_objects as go

# Dashboard modules
from dash import Input, Output

def specification_distribution_callback(app, colours):
    # Callback function gets called wheever the selected product from the specification drop down menu changes. Updates the figure to the corresponding specification
    @app.callback(
        Output("spec-drop-down-dist", "options"),
        Output("colour-drop-down-1", "options"),
        Input("memory", "data"),
    )
    def update_graph_title(json):
        # Extract df from product and retrieve columns
        df = pd.read_json(json, orient='split')
        
        specs = [column for column in df.columns if df.dtypes[column]
            == "int64" or df.dtypes[column] == "float64"]
        
        colours_options = [colour for colour in df["Material Colour"].unique()]
        colours_options.append("All")
        
        return specs, colours
    
    # Callback function gets triggered whenever the date and/or specification value is changed
    @app.callback(
        # Changes figure attribute for specDistribution graph
        Output("spec-distribution", "figure"),
        Output("spec-title", "children"),
        # Uses the value attribute from the product-drop-down element as the argument for the below function
        Input('memory', 'data'),
        Input('memory-title','data'),
        # The value attribute for the spec-drop-down element is the argument for the below function
        Input('spec-drop-down-dist', 'value'),
        # Colour drop down
        Input('colour-drop-down-1',"value"),
        # Start data parameter
        Input('date-selector', "start_date"),
        # End date parameter
        Input('date-selector', "end_date")
    )
    def update_spec(product, title, spec, colour, start_date, end_date):
        # Extract df from product and retrieve columns
        df = pd.read_json(product, orient='split')
        
        columns = [column for column in df.columns if df.dtypes[column]
            == "int64" or df.dtypes[column] == "float64"]
        
        colour_options = [colour for colour in df["Material Colour"].unique()]
        colour_options.append("All")

        # Initiate dates
        if end_date == None:
            end_date = str(datetime.today()).split(" ")[0]

        if start_date == None:
            start_date = df.iloc[:, 0][1].split("T")[0]

        df = df[start_date:end_date]
        
        if colour != "All":
            df = df.loc[df['Material Colour'] == colour]
        
        spec_data = [x for x in df[spec][~np.isnan(df[spec])] if x > 1]

        fig = go.Figure(
            data=[go.Histogram(x=spec_data, marker=dict(color=colours["marker"]))])

        # fig.update_xaxes(showgrid=False)
        fig.update_yaxes(gridcolor=colours["border"])
        fig.update_yaxes(title_text=f"<b>Number of Batches<b>", zerolinecolor=colours["border"])
        fig.update_xaxes(title_text=f"<b>{spec}<b>")

        # Whenever callback function is called, the figure will update using these presets
        fig.update_layout(
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
        # Return plotly figure
        
        spec = spec.split(" ")[0]
        
        return fig, f"{title} {spec} Distribution"
