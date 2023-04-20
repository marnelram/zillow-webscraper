# Seattle-Apartment-Price-Model
Models the price of apartments in and around the Seattle area on features such as distance from downtown, in-unit washer and dryer, transportation score, etc. 

## Getting Started
To use this project, you will need:
```shell
pip install scrapy
pip install ...
```
[list of prerequisites, such as Python 3, the BeautifulSoup library, etc.].

To start the webscraping process, run the scrape.py script. This script will [what the script does, such as visiting the website, selecting certain elements, etc.].

## Configuration
The config.py file contains [what the configuration file contains, such as website URL, search parameters, etc.]. You can modify this file to adjust the [what you can adjust, such as the search parameters] to suit your needs.

## Output
The output of the webscraping process is stored in [what file format you are storing the data in, such as CSV or JSON], in the data directory.

## Workflow
The model is made with 3 pipeline steps:
-scrape data from [zillow](https://www.zillow.com) on different **apartment characteristics**
-clean the data gathered
-perform a multivariable linear regression

## Acknowledgments
[If you used any external resources or libraries, you can acknowledge them here.]
