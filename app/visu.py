import pandas as pd
import matplotlib.pyplot as plt

figsize = (8, 4)
color = "darkslateblue"


def plot_distribution(df, column):
    """
    Plot a histogram for a specific column in the dataframe
    """
    plt.figure(figsize=figsize)
    df[column].hist(bins=30, color=color)
    plt.title(f"Distribution of {column}")
    plt.show()


def plot_category_distribution(df, column):
    """
    Plot a bar chart for a categorical column in the dataframe
    """
    plt.figure(figsize=figsize)
    df[column].value_counts().plot(kind="bar", color=color)
    plt.title(f"Distribution of {column}")
    plt.show()


def plot_time_gap(df):
    """
    Plot a line chart for time gap
    """
    plt.figure(figsize=figsize)
    df["time_gap"].value_counts().sort_index().plot(color=color)
    plt.title("Time Gap")
    plt.show()


def plot_duration(df):
    """
    Plot a line chart for duration
    """
    plt.figure(figsize=figsize)
    df["duration"].plot(color=color)
    plt.title("Duration")
    plt.show()
