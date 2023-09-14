import re
import json
from datetime import datetime

class ParsingUtils:
    """ Utility class to support spider data processing """

    def __init__(self, *args, **kwargs):
        self.logger = kwargs.get("logger")

    def extract_json_response(self, response):
        """
        Returns response as JSON.
        Args:
            response (scrapy.Response): The spider response object.

        Returns:
            JSON: The spider respponse converted to valid JSON object.
        
        Raises:
            json.JSONDecodeError or Exception: if unexpected data in response.
        """

        try:
            search_obj = re.search(
                r'''\'__TGT_DATA__\': \{ configurable: false, enumerable: true, value: deepFreeze\(JSON.parse\(\"(.+)\"\)\)''',
                response.text)
            if search_obj:
                try:
                    self.logger.info("Converting product text response to JSON")
                    json_response = json.loads(search_obj.group(1).encode('utf-8').decode('unicode_escape'))
                    return json_response
                except json.JSONDecodeError:
                    self.logger.error("error converting response to JSON", exc_info=True)
                    raise
            else:
                self.logger.info("Search pattern not found!")
        except Exception:
            self.logger.error("Error searching regex pattern", exc_info=True)
            raise
        return
    
    def get_short_currency(self, price):
        """
        Get currency short form for currency symbol.
        Args:
            price(str): The amount with currency symbol.

        Returns:
            str: The short form string for currency symbol.
        """

        CUR_MAPPING = {
            "$": "USD",
            "ƒ": "Cent"
        }
        return CUR_MAPPING.get(re.search(r'(^\D+)', price).group(1))
    
    def format_date(self, datetime_str):
        """
        Convert datatime to specific format.
        Args:
            datetime_str(str): The datetime string.

        Returns:
            str: Date formatted to YYYY-MM-DD.
        """

        try:
            date_str = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%SZ")
            return date_str.strftime("%Y-%m-%d")
        except ValueError:
            return datetime_str[:10]
    

            


