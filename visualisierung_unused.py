import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go

def start_visualisierung(data, fremd, heim):

    app = dash.Dash(__name__)

    # Erstelle individuellen Hovertext pro Zelle
    hovertext = [
        [
            f"Zeile: {fremd[i]}<br>Spalte: {heim[j]}<br>Wert: {data[i, j]}"
            for j in range(data.shape[1])
        ]
        for i in range(data.shape[0])
    ]

    # Heatmap mit eigenem Hovertext
    fig = go.Figure(
        data=go.Heatmap(
            z=data,
            text=hovertext,            #  eigener Text für jede Zelle
            hoverinfo="text",          #  zeigt nur diesen Text an
            colorscale=[[0, "white"], [1, "blue"]],
        )
    )

    #  Layout mit fixer Info-Box
    app.layout = html.Div([
        html.Div([
            dcc.Graph(id="matrix", figure=fig, style={"height": "90vh", "width": "100%"}),
            html.Div(
                id="hover-info",
                style={
                    "position": "absolute",
                    "top": "10px",
                    "right": "20px",
                    "background": "rgba(255,255,255,0.8)",
                    "padding": "8px 12px",
                    "borderRadius": "8px",
                    "boxShadow": "0 0 5px rgba(0,0,0,0.2)",
                    "fontFamily": "sans-serif",
                },
            ),
        ], style={"position": "relative"}),
    ])

    #  Callback für zusätzliche Anzeige oben rechts
    @app.callback(
        Output("hover-info", "children"),
        Input("matrix", "hoverData")
    )
    def update_hover(hoverData):
        if hoverData:
            i = hoverData["points"][0]["y"]
            j = hoverData["points"][0]["x"]
            wert = data[i, j]
            return f"Zeile: {i} | Spalte: {j} | Wert: {wert}"
        return "Bewege die Maus über eine Zelle"

    app.run(debug=True)
