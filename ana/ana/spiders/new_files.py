import scrapy
import pandas as pd
from tqdm import tqdm
from ..items import AnaItem
from .reservoir_util import Reservoirs
import pickle

GREEN = '\033[92m[+]\033[0m'
YELLOW = '\033[33m[+]\033[0m'

'''
    Script responsible for checking and downloading new reservoirs.
    First we get the reservoirs list on the website and we save this list.
    We check the files that have already been saved and create a list with these names.
    We check both lists and create a new one containing only the new identified reservoirs, if this is true.
    Otherwise, we use the full list. This means no files were found on the local machine.
'''


class NewFilesSpider(scrapy.Spider):
    # Spiser name
    name = 'new_files'

    urls = ['https://www.ana.gov.br/sar0/MedicaoSin']
    reservoir_dict = dict()
    dict_reservoir_reverse = dict()
    # definition of the historical period
    start = '01/04/2022'
    end = '05/04/2022'

    # List coming from main.py
    def __init__(self, list_names_reservoirs=None, **kwargs):
        super().__init__(**kwargs)
        self.list_names_reservoirs = list_names_reservoirs

    # The first request on website defined on urls variable
    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url)

    # Callback of start_requests
    def parse(self, response, **kwargs):
        print(f" {GREEN} Looking for new files.")
        # Saving a dictionaries with all the reservoirs found on the website
        all_reservoirs = Reservoirs.get_all_reservoris(response)
        reservoirs = Reservoirs(all_reservoirs, response)
        self.reservoir_dict = reservoirs.dict_reservoirs()
        pickle.dump(self.reservoir_dict, open(f'ana/datasets/reservoirs_list.sav', 'wb'))
        # Checking if the past list is empty
        # If yes, the logic is to take all the reservoirs
        if self.list_names_reservoirs is not None:
            print('list_names_reservoirs is not None')
            reservoirs = Reservoirs(self.list_names_reservoirs, response)
            self.reservoir_dict = reservoirs.dict_reservoirs()
        # Checking if there is already a local file referring to the reservoir
        self.reservoir_dict = Reservoirs.reservoirs_to_search(self.reservoir_dict)
        # If the files already exist locally this dict returns empty.
        if len(self.reservoir_dict) > 0:
            # request for the data of each reservoir on the dict
            for k_reservoir in tqdm(self.reservoir_dict, desc='Reservoirs:'):
                print(k_reservoir)
                yield scrapy.Request(
                    f'https://www.ana.gov.br/sar0/MedicaoSin?dropDownListReservatorios={self.reservoir_dict[k_reservoir]}'
                    f'&dataInicial={self.start}&dataFinal={self.end}&button=Buscar#',
                    callback=self.parse_reservoir)
        else:
            print(f" {YELLOW} There are no new files to download")

    # Callback of Request
    def parse_reservoir(self, response):
        # Get the content passed by the request
        content = pd.read_html(response.text, decimal=',', thousands='.')[0]
        print('Got content...')
        # If the last line is incomplete drop it
        content = content[content.iloc[:, 3].str.isnumeric()]
        print('Content filtered')
        #failed_banks[failed_banks['Closing Date'].dt.year == 2017]
        # Reverting the Reservoir dict (key <-> value)
        for key_rev, value_rev in self.reservoir_dict.items():
            self.dict_reservoir_reverse[value_rev] = key_rev
        reservoir_code = str(response.url).split('=')[1].split('&')[0]
        reservoir_name = self.dict_reservoir_reverse[reservoir_code]
        # checking if there are records in the dataframe
        if len(content) > 0:
            # object that stores the dataframe
            item = AnaItem()
            item['reservoir_name'] = reservoir_name
            item['content_table'] = content
            print(f'{GREEN} Reservoir: {reservoir_name} have {len(content)} records.')
            # The pipelines.py script file is responsible for handling the object item
            yield item
        else:
            print(f'{YELLOW} Reservoir: {reservoir_name} records not found.')
