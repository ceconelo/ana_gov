
from .settings import ABSOLUTE_PATH
from unidecode import unidecode
import re

'''
    This script is responsible for taking the AnaItem object and saving it as .csv
    Note: Fill the (ABSOLUTE_PATH) variable located in the settings.py file
    
'''


class AnaPipeline:
    def process_item(self, item, spider):
        return item['content_table'].to_csv(
            f'{ABSOLUTE_PATH}/{re.sub(r"[*]", "", unidecode(item["reservoir_name"]))}.csv',
            sep=',',
            index=False,
            encoding='utf-8-sig')
