import matplotlib.pyplot as plt

FIGSIZE = (8, 4)
COLOR = "darkslateblue"


def plot_distribution(df, column):
    """
    Plot a histogram for a specific column in the dataframe.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the data.
    column : str
        The name of the column to plot.
    """

    plt.figure(figsize=FIGSIZE)
    df[column].hist(bins=30, color=COLOR)
    plt.title(f"Distribution of {column}")
    plt.show()


def plot_category_distribution(df, column):
    """
    Plot a bar chart for a categorical column in the dataframe.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the data.
    column : str
        The name of the categorical column to plot.
    """

    plt.figure(figsize=FIGSIZE)
    df[column].value_counts().plot(kind="bar", color=COLOR)
    plt.title(f"Distribution of {column}")
    plt.show()


def plot_time_gap(df):
    """
    Plot a line chart for time gap.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the data.
    """

    plt.figure(figsize=FIGSIZE)
    df["time_gap"].value_counts().sort_index().plot(color=COLOR)
    plt.title("Time Gap")
    plt.show()


def plot_duration(df):
    """
    Plot a line chart for duration.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the data.
    """

    plt.figure(figsize=FIGSIZE)
    df["duration"].plot(color=COLOR)
    plt.title("Duration")
    plt.show()
