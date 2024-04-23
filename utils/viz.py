import plotly.graph_objects as go
import numpy as np
import pandas as pd

from IPython.display import display, Markdown


def graphePerso(prenom, nom, data, titre, nb_bins=10_000):
    """
    Create a personalized graph showing the distribution of athlete performance
    and the athlete's position.

    Parameters
    ----------
    prenom : str
        The first name of the athlete.
    nom : str
        The last name of the athlete.
    data : pandas.DataFrame
        The DataFrame containing athlete data.
    titre : str
        The title of the graph.
    nb_bins : int, optional
        The number of bins for the histogram. Defaults to 10,000.
    """

    times_in_seconds = pd.to_datetime(data.h_duration, format='%H:%M:%S').dt.time.apply(
        lambda time: 3600*time.hour+60*time.minute+time.second)
    bins = np.linspace(times_in_seconds.iloc[0], times_in_seconds.iloc[-1], nb_bins)
    cdf = [(times_in_seconds <= bin_).sum()/len(times_in_seconds) for bin_ in bins]

    z = data.index[data['Athlète'] == (nom.upper() + " " + prenom.capitalize())]
    temps = data.loc[z[0], 'duration']
    cdf_proportion = (times_in_seconds <= temps).sum() / len(times_in_seconds)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=bins, y=cdf,
        fill='tozeroy',
        mode='lines',
        line_color='blue',
        name='Distribution des temps'
    ))

    fig.add_trace(go.Scatter(
        x=[temps, temps], y=[0, max(cdf)],
        mode='lines',
        line_color='red',
        name=nom.upper()+" "+prenom.capitalize()
    ))

    fig.add_shape(
        type="line",
        x0=bins[0],
        y0=cdf_proportion,
        x1=temps,
        y1=cdf_proportion,
        line=dict(
            color="black",
            width=1,
            dash="dashdot",
        ),
    )

    fig.add_annotation(
        x=temps,
        y=cdf_proportion,
        text=f"<b>{100*cdf_proportion:.2f}%</b>",
        font=dict(size=14),
        showarrow=True,
        arrowhead=7,
        ax=0,
        ay=-30,
    )

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
    """
    Display competition information.

    Parameters
    ----------
    header : dict
        Dictionary containing competition information.
    """

    display(Markdown(f"**Compétition:** {header['nom']}"))
    display(Markdown(f"**Lieu:** {header['lieu']}"))
    display(Markdown(f"**Date:** {header['date']}"))
    display(Markdown(f"**Dept:** {header['dept']}"))
    display(Markdown(f"**Label:** {header['label']}"))


def display_podium(data):
    """
    Display the podium visualization.

    Parameters
    ----------
    data : pandas.DataFrame
        DataFrame containing athlete data.
    """

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
