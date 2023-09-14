import scrapy
import json
from syntask.logger import get_logger
from syntask.utilities import ParsingUtils
from syntask.items import SyntaskItem
from syntask.settings import REQ_HEADER


class TargetSpider(scrapy.Spider):
    """ Scrapy spider child class. """
    
    name = "target"
    allowed_domains = ["target.com"]
    logger = get_logger()
    utils = ParsingUtils(logger = logger)
    START_PAGE = 0
    QUEST_URL = "https://r2d2.target.com/ggc/Q&A/v1/question-answer?key=9f36aeafbe60771e321a7cc95a78140772ab3e96&page={}&questionedId={}&type=product&size=10&sortBy=MOST_ANSWERS"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [kwargs.get('url')]

    def parse(self, response):
        """ 
        Parse product data from spider response.\
        
        Args:
            response (scrapy.Response): The Response object from start_url request.

        Yields:
            scrapy.Request : A scrapy request to get additional data.
        """
        
        self.logger.info("Product response object send for parsing")
        response_json = self.utils.extract_json_response(response)

        try:
            product_json = response_json['__PRELOADED_QUERIES__']['queries'][0][1]['product']
        except KeyError:
            for qlist in response_json['__PRELOADED_QUERIES__']['queries']:
                if "product" in qlist[1]:
                    product_json = qlist[1]["product"]["children"][0]
                    break
                product_json = {}

        item = SyntaskItem()
        try:
            item['url'] = product_json['item']['enrichment']['buy_url']
            item['tcin'] = product_json['tcin'] 
            item['upc'] = product_json['item']['primary_barcode']
            item['price_amount'] = product_json['price']['reg_retail'] if 'regular_price' in product_json['price'] else product_json['price']['current_retail']
            item['currency'] = self.utils.get_short_currency(product_json['price']['formatted_current_price'])
            try:
                item['description'] = response_json['__PRELOADED_QUERIES__']['queries'][1][1]['data']['metadata']['seo_data']['seo_description']
            except KeyError:
                item['description'] = response_json['__PRELOADED_QUERIES__']['queries'][1][1]['metadata']['seo_data']['seo_description']
            item['specs'] = product_json['item']['product_description']['bullet_descriptions']
            item['ingredients'] = product_json['item']['enrichment'].get('nutrition_facts',{}).get('ingredients',None)
            item['bullets'] = "".join(product_json['item']['product_description']['soft_bullets']['bullets'])
            item['features'] = product_json['item']['product_description']['bullet_descriptions']
        except KeyError:
                self.logger.error("error extracting product data", exc_info=True)
        
        yield scrapy.Request(url = self.QUEST_URL.format(self.START_PAGE, item['tcin']), 
                             headers = REQ_HEADER, callback = self.parse_qna, 
                             dont_filter=True, cb_kwargs={"item": item})


    def parse_qna(self, response, item):
        """
        Parse the Q&A data from a scrapy response.

        Args:
            response (scrapy.Response): The response containing Q&A data in JSON format.
            item (scrapy.Item): The item being processed to which Q&A data will be added.

        Yields:
            scrapy.Request or scrapy.Item: Yields either a new request to fetch the next page of Q&A data or
            the item with parsed Q&A information.
        """

        try:
            qna_json = response.json()
        except json.JSONDecodeError:
            self.logger.error("error loading qna JSON response", exc_info=True)
        
        questions = qna_json['results']
        if 'questions' not in item.keys():
            item['questions'] = []
        

        for question in questions:
            try:
                quest_item = {}
                quest_item["question_id"] = question["id"]
                quest_item["submission_date"] = self.utils.format_date(question["submitted_at"])
                quest_item["question_summary"] = question["text"]
                quest_item["user_nickname"] = question["author"].get("nickname")
                quest_item["answers"] = [] #if "answers" not in quest_item
                
                answers = question['answers']
                for answer in answers:
                    answer_item = {}
                    answer_item["answer_id"] = answer["id"]
                    answer_item["answer_summary"] = answer["text"]
                    answer_item["submission_date"] = self.utils.format_date(answer["submitted_at"])
                    answer_item["user_nickname"] = answer["author"].get("nickname")
                    quest_item["answers"].append(answer_item)
            except KeyError:
                self.logger.error("error extracting qna data for url: %s" % item.get("url"), exc_info=True)
            item['questions'].append(quest_item)
        
        if not qna_json["last_page"]:
            next_page = qna_json["page"] + 1
            yield scrapy.Request(url = self.QUEST_URL.format(next_page, item['tcin']), 
                             headers = REQ_HEADER, callback = self.parse_qna, 
                             dont_filter=True, cb_kwargs={"item": item})
        else:
            yield item

