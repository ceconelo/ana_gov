import scrapy
import pandas as pd
import pickle
import os
from unidecode import unidecode
from tqdm import tqdm
from ..items import AnaItem

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
    urls = ['https://www.ana.gov.br/sar0/Medicao']
    reservoir_dict = dict()
    dict_reservoir_reverse = dict()
    file_only_names = []
    # definition of the historical period
    start = '01/01/1995'
    end = '01/03/2022'

    # The first request on website defined on urls variable
    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url)

    # Callback of start_requests
    def parse(self, response, **kwargs):
        # Get list of revervoirs in website
        for reservoir in response.xpath('//select[@name="dropDownListReservatorios"]//option')[1:]:
            key = unidecode(str(reservoir.xpath('.//text()').get()).replace(' ', '').strip())
            value = reservoir.xpath('.//@value').get()
            self.reservoir_dict[key] = value
        # Saving the dict that have the list of revervoirs
        pickle.dump(self.reservoir_dict, open(f'ana/datasets/reservoirs_list.sav', 'wb'))
        # Get files salved on local machine
        files = [f for f in os.listdir('ana/datasets') if '.csv' in f]
        # If exists files on local update them
        if files:
            # Getting the name of the files.
            for file in files:
                splited_file = file.split('.')
                self.file_only_names.append(splited_file[0])
            # Verifing if exists new reservoirs on list of reservoirs
            to_compare_reservoir = {fon: self.reservoir_dict[fon] for fon in self.file_only_names}
            reservoirs_to_search = {fnr: self.reservoir_dict[fnr] for fnr in
                                    set(self.reservoir_dict).difference(to_compare_reservoir)}
            # If true, let's rebuild the list of reservoirs
            if len(reservoirs_to_search) > 0:
                self.reservoir_dict = reservoirs_to_search
        # request for the data of each reservoir on the list
        for k_reservoir in tqdm(self.reservoir_dict, desc='Searching Reservoirs:'):
            yield scrapy.Request(
                f'https://www.ana.gov.br/sar0/Medicao?dropDownListReservatorios={self.reservoir_dict[k_reservoir]}'
                f'&dataInicial={self.start}&dataFinal={self.end}&button=Buscar#',
                callback=self.parse_reservoir)

    # Callback of Request
    def parse_reservoir(self, response):
        # Get the content passed by the request
        content = pd.read_html(response.text, decimal=',', thousands='.')[0]
        # Reverting the Reservoir List (key <-> value)
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
            print(f'Accessing: {response.url}.')
            print(f'Reservoir: {reservoir_name}')
            print(f'Total: {len(content)} records.')
            print('---------------------------------------')
            # The pipelines.py script file is responsible for handling the object item
            yield item
        else:
            print(f'Accessing: {response.url}.')
            print(f'Reservoir: {reservoir_name}.')
            print(f'Total: Records not found.')
            print('---------------------------------------')
