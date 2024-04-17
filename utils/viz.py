import plotly.graph_objects as go
import numpy as np
import pandas as pd
import utils.stat as stat

from IPython.display import display, Markdown

def graphePerso(prenom, nom, data, titre):
    densite=stat.dens(data['duration'], bins = stat.idealBins(len(data['duration'])))
    fcubic=stat.lissage(densite, sep = True,beginend = (data['duration'].min(),data['duration'].max()))
    z=data.index[data.Athlète==(nom.upper()+" "+prenom.capitalize())]
    temps = data.loc[z[0],'duration']
    x= np.linspace(data['duration'].min(),data['duration'].max(), int(1e5))

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x, y=fcubic(x),
        fill='tozeroy',
        mode='lines', 
        line_color='blue',
        name='densité lissée & interpolée'
    ))

    fig.add_trace(go.Scatter(
        x=[temps, temps], y=[0, max(fcubic(x))],
        mode='lines',
        line_color='red',
        name=nom.upper()+" "+prenom.capitalize()
    ))

    fig.update_layout(
        title=titre,
        xaxis_title="Durée pour franchir la ligne d'arrivée",
        yaxis_title="Densité des athlètes",
        legend_title="Légende",
        autosize=False,
        width=800,
        height=450,
    )

    fig.show()

def display_header(header):
    display(Markdown(f"**Compétition:** {header['nom']}"))
    display(Markdown(f"**Lieu:** {header['lieu']}"))
    display(Markdown(f"**Date:** {header['date']}"))
    display(Markdown(f"**Dept:** {header['dept']}"))
    display(Markdown(f"**Label:** {header['label']}"))