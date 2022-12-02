# Dashboard modules
from dash import html, dcc

# Functional component with an optional drop down element argument
def graph_element(header_id, graph_id, spec_drop_down=None, colour_drop_down=None, background_color=None):
    return html.Div(
        className="GraphDiv",
        style={
            "backgroundColor": background_color
        },
        children=html.Div(
            className="Graph",
            children=[
                html.H2(
                    id=header_id,
                    className="GraphTitle",
                    style={
                        "backgroundColor":background_color,
                    },
                ),
                dcc.Graph(
                    id=graph_id
                ),
                spec_drop_down,
                colour_drop_down
            ]
        )
    )
    
# Tile functional component to display single value stats
def stat_tile_element(id_stat, title, background_colour=None, border_colour=None, text_colour=None):
    return html.Div(
        className="Tile",
        style = {
            "color":text_colour
        },
        children=[
            html.Div(
                className="StyledDataCard",
                style = {
                    "borderColor": border_colour,
                    "color" : text_colour,
                    "backgroundColor" : background_colour 
                },
                children=[
                    html.Div(
                        className="HandleWrapper",
                        children=[
                            html.Div(
                                className="DataCardContent",
                                children=[
                                    html.Div(
                                        id=id_stat,
                                        className="Statistic"
                                    ),
                                    html.P(
                                        className="TileTitle",
                                        children=title
                                    ),
                                ]
                            ),
                            html.Div(
                                className="Handle",
                                style={
                                    "backgroundColor":text_colour
                                }
                            )
                        ]
                    )
                ]
            )
        ]
    )

