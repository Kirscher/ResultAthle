from flask import Flask, render_template, request, send_file
from scraping import scrape
import matplotlib.pyplot as plt
import visu
import os

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/scrape", methods=["POST"])
def scrape_results():
    url = request.form["url"]
    header, results = scrape(url)
    if results is None:
        return render_template(
            "index.html",
            error_message="Error occurred while scraping. Please check the URL and try again.",
        )
    else:
        # Get the absolute path of the directory where app.py is located
        dir_path = os.path.dirname(os.path.realpath(__file__))

        # Generate plots
        visu.plot_distribution(results, "Naissance")
        plt.savefig(os.path.join(dir_path, "static", "Naissance.png"))
        visu.plot_category_distribution(results, "Catégorie")
        plt.savefig(os.path.join(dir_path, "static", "Catégorie.png"))
        visu.plot_time_gap(results)
        plt.savefig(os.path.join(dir_path, "static", "time_gap.png"))
        visu.plot_duration(results)
        plt.savefig(os.path.join(dir_path, "static", "duration.png"))

        return render_template(
            "results.html", results=results.to_dict("records"), header=header
        )


@app.route("/download")
def download():
    # Placeholder code to generate CSV file from results data
    # Replace this with your actual CSV generation logic
    # For demonstration purposes, it just returns a dummy CSV file
    dummy_csv_data = "Column1,Column2\nValue1,Value2\nValue3,Value4"
    return send_file(
        dummy_csv_data,
        mimetype="text/csv",
        download_name="results.csv",
        as_attachment=True,
    )


if __name__ == "__main__":
    app.run(debug=True)
