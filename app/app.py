from flask import Flask, render_template, request, send_file
from scraping import scrape

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape_results():
    url = request.form['url']
    results = scrape(url)
    if results is None:
        return render_template('index.html', error_message="Error occurred while scraping. Please check the URL and try again.")
    else:
        return render_template('results.html', results=results.to_dict('records'))

@app.route('/download')
def download():
    # Placeholder code to generate CSV file from results data
    # Replace this with your actual CSV generation logic
    # For demonstration purposes, it just returns a dummy CSV file
    dummy_csv_data = "Column1,Column2\nValue1,Value2\nValue3,Value4"
    return send_file(
        dummy_csv_data,
        mimetype='text/csv',
        attachment_filename='results.csv',
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(debug=True)
