# Data handling
import pandas as pd
from datetime import datetime

# Data visualisation
import plotly.express as px
import plotly.graph_objects as go

# Dashboard modules
from dash import Input, Output


def failure_pie_chart_callback(app, colours):
    # Callback function gets triggered whenever the date is changed
    @app.callback(
        Output("pie-chart", "figure"),
        Output("pie-title", "children"),
        Output("colour-drop-down-3", "options"),
        Input("memory", "data"),
        Input("memory-title", "data"),
        Input("colour-drop-down-3", "value"),
        # Start data parameter
        Input('date-selector', "start_date"),
        # End date parameter
        Input('date-selector', "end_date")
    )
    def update_pie_chart(json, product, colour, start_date, end_date):
        df = pd.read_json(json, orient='split')
        
        colours_options = [colour for colour in df["Material Colour"].unique()]
        colours_options.append("All")

        # Initiate dates
        if end_date == None:
            end_date = str(datetime.today()).split(" ")[0]
        if start_date == None:
            start_date = df.iloc[:, 0][1].split("T")[0]

        df = df[start_date:end_date]
        
        if colour != "All":
            df = df.loc[df['Material Colour'] == colour]

        colours = ['#d95f02', '#1b9e77', '#7570b3', '#e7298a', '#66a61e','#e6ab02','#a6761d', "#232323"]

        if len(df['Failure code'].unique()) > 1:
            
            failure_code_no = {}
            
            for value in df["Failure code"].unique():
                if value != None:
                    no = len(df.loc[df["Failure code"] == value])
                    if len(value.split(",")) > 1:
                        for code in value.split(","):
                            failure_code_no[code.upper()] = no + failure_code_no.get(code.upper(), 0)
                    else:
                        failure_code_no[value.upper()] = no + failure_code_no.get(value.upper(), 0)
                            
            
            labels = [key for key in failure_code_no.keys()]
            values = [failure_code_no[label] for label in labels]

            for code in labels:
                values.append(len(df.loc[df['Failure code'] == code]))

            fig = go.Figure(data=[go.Pie(labels=[label.upper()
                            for label in labels], values=values)])

            fig.update_traces(textposition='inside', textinfo='percent+label+value',
                            marker=dict(colors=colours, line=dict(color='rgb(75,75,75)', width=1)))

            # Whenever callback function is called, the figure will update using these presets
            fig.update_layout(
                margin=dict(
                    t=20,
                    b=20,
                    r=20,
                    l=20
                ),
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                ),
                title_font_family="Abel",
                plot_bgcolor="#F2E9DD",
                paper_bgcolor="#F2E9DD",
                font_color="#493D32",
                font_family="Abel"
            )

            return fig, f"{product} Failure Codes ", colours_options
        else:
            fig = px.scatter_3d().add_annotation(text="No Failures to Report",
                                                showarrow=False, font={"size": 34})

            fig.update_yaxes(showgrid=False, showticklabels=False, visible=False)
            fig.update_xaxes(showgrid=False, showticklabels=False, visible=False)

            # Whenever callback function is called, the figure will update using these presets
            fig.update_layout(
                margin=dict(
                    t=20,
                    b=20,
                    r=20,
                    l=20
                ),
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                ),
                title_font_family="Abel",
                plot_bgcolor="#F2E9DD",
                paper_bgcolor="#F2E9DD",
                font_color="#493D32",
                font_family="Abel"
            )
            
            return fig, f"{product} Failure Codes ", colours_options