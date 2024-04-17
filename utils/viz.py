import plotly.graph_objects as go
import numpy as np
import pandas as pd
import utils.stat as stat

from IPython.display import display, Markdown


def graphePerso(prenom, nom, data, titre):
    densite = stat.dens(data['duration'], bins=stat.idealBins(len(data['duration'])))
    fcubic = stat.lissage(densite, sep=True, beginend=(data['duration'].min(),
                          data['duration'].max()))
    z = data.index[data['Athlète'] == (nom.upper() + " " + prenom.capitalize())]
    temps = data.loc[z[0], 'duration']
    x = np.linspace(data['duration'].min(), data['duration'].max(), int(1e5))

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


def display_podium(data):
    data.h_duration = pd.to_datetime(data.h_duration, format='%H:%M:%S').dt.time
    podium = data.sort_values(by='h_duration').iloc[[2, 0, 1]]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=[1, 3, 2],
        x=podium['Athlète'],
        orientation='v',
        marker=dict(
            color=['#614e1a', '#a57c00', '#c7d1da'],  # Couleur du podium (bronze, gold, silver)
            line=dict(color='black', width=1)  # Couleur de la bordure
        )
    ))

    for i, annotation_text in enumerate(['🥉', '🥇', '🥈']):
        fig.add_annotation(
            x=podium.iloc[i]['Athlète'],
            y=[1.2, 3.2, 2.2][i],
            text=annotation_text,
            showarrow=False,
            font=dict(size=70)
        )

    fig.update_layout(
        title="Podium",
        yaxis_title="Durée",
        yaxis=dict(
            tickvals=[1, 2, 3],
            ticktext=podium['h_duration'].sort_values(ascending=False)
        ),
        xaxis=dict(
            tickfont=dict(size=16)
        )
    )
    fig.show()
