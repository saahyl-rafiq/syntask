# syntask
This Scrapy 2.10.1 spider is designed to scrape product data, question and answers from www.target.com.

## Description
1. This spider collects data from the website for the following fields url , tcin , upc , price_amount , currency , description , specs , ingredients , bullets , features , questions. 
2. The data for specs is populated with what is on the webpage and is same as features data.
3. Raw data from response is cleaned of html tags in the item Pipeline.
4. Parsing response data is supported by the utilities module. 
5. The final output is stored in the file name passed at the terminal (in this example target_product.json).
6. Logging is enabled throughout the module and logs are written to LOG_FILE_NAME in settings.
7. Request header is taken from REQ_HEADER in settings.
8. This spider is tested on Windows OS.

## Prerequisites

1. Create virtual env
  ```bash
  python -m venv /path/to/new/virtual/environment
  ```
2. Activate virtual env
  ```bash
  /path/to/new/virtual/environment/Scripts/activate
  ```
3. Install requirements
  ```bash
  pip install -r requirements.txt
  ```

## Execution

To run the spider and append scraped results to json file, use the following command:
```bash
scrapy crawl target_com -a url=https://www.target.com/p/-/A-79344798 -o target_product.json
```

## Author
Saahyl Sheikh - saahylrafiq@gmail.com