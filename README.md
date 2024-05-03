# ResultAthle
<p align="center"><img src="src/logo.png"></p>

[![ci](https://github.com/Kirscher/ResultAthle/actions/workflows/prod.yml/badge.svg)](https://github.com/Kirscher/ResultAthle/actions/workflows/prod.yml)
[![documentation](https://github.com/Kirscher/ResultAthle/actions/workflows/documentation.yml/badge.svg)](https://github.com/Kirscher/ResultAthle/actions/workflows/documentation.yml)

ResultAthle is a project aimed at making statistical tools more accessible at the amateur level in athletics. It addresses the challenges of data manipulation and the lack of accessible descriptive statistics at the club, race, or individual level.

## Table of Contents

- [ResultAthle](#resultathle)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Python package](#python-package)
    - [HTML dashboard with Quarto](#html-dashboard-with-quarto)
  - [Features Under Development](#features-under-development)
  - [Contributing](#contributing)
  - [License](#license)

## Installation

To install the necessary dependencies, run the following command:

```sh
pip install -r requirements.txt
```

## Usage

### Python package

To retrieve the '.csv' file containing the list of results from a running competition on the bases.athle results site, you can use the 'scraping.py' module:

```python
from utils.scraping import get_results
header, data = get_results(url, nb_pages)
```

Where 'url' is the [bases.athle](https://bases.athle.fr/) URL of the competition to scrape and 'nb_pages' is the number of result pages you want to scrape.

### HTML dashboard with Quarto

Quarto is to be downloaded here: [Quarto URL](https://quarto.org/docs/get-started/).

To convert the main.ipynb to HTML, run:

```sh
quarto render .\main.ipynb --to html
```

To preview the HTML in localhost, run:

```sh
quarto preview .\main.ipynb
```

To host the HTML, run:

```sh
quarto preview main.ipynb --port 5000 --host 0.0.0.0 --execute
```


## Features Under Development

We are continuously working to improve ResultAthle and add new features. Here are some of the features that are currently under development:

- **WebApp:** we are developing a web application version of ResultAthle. This webapp will provide users with the flexibility to access and analyze race results from [bases.athle](https://bases.athle.fr/).

- **Advanced Scraping Functions:** We are in the process of enhancing our web scraping capabilities to provide a more robust and sophisticated data extraction process. This will allow us to gather more detailed and comprehensive data from athletics competitions.

- **Visualization:** We are working on new visualization features that will allow users to better understand and interpret the running performance. This includes various types of charts and graphs.

- **Performance Analysis:** We are developing new features for analyzing athletic performance. This will include statistical analysis and machine learning algorithms to identify patterns and trends in the data.

Stay tuned for these exciting new features!

## License

ResultAthle is licensed under the MIT License. This means you are free to use, modify, and distribute the project, as long as you include the original copyright and license notice in any copy of the software/source.

For more information on the MIT License, see the [LICENSE](LICENSE) file in this repository or visit [MIT License](https://opensource.org/licenses/MIT).
