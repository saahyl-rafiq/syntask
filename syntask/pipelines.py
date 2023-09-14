# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import re
from itemadapter import ItemAdapter


class SyntaskPipeline:
    """Scrapy Pipeline for data cleaning"""

    @staticmethod
    def remove_html_tags(feature_list):
        """
        Remove html tags from list data.
        Args:
            feature_list (list): A list of text data.

        Returns:
            list: list data cleared of html tags.
        """
        return [re.sub(r'<[^>]+>', '', feature).strip() for feature in feature_list] 
        
    def process_item(self, item, spider):
        """ 
        Process the scraped item by cleaning the data.

        Args:
        item (dict): The scraped item to process.
        spider (scrapy.Spider): The spider that scraped the item.

        Returns:
            dict: The processed item cleaned.
        """

        item['specs'] = self.remove_html_tags(item.get("specs",[]))
        item["features"] = self.remove_html_tags(item.get("features",[]))
        return item
    

    
