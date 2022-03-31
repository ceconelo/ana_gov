import scrapy
from ..items import AnaItem
import pandas as pd
import pickle
from datetime import datetime, timedelta
import os
from tqdm import tqdm

'''
    This script is responsible for updating existing files on your local machine.
    It checks if there are files in the project's <datasets> folder, if there is, it 
    takes the date on the last update, takes today's date and checks if there are 
    new records in that period.
'''


class UpdadeRecordsSpider(scrapy.Spider):
    # Spiser name
    name = 'updade_records'
    urls = ['https://www.ana.gov.br/sar0/Medicao']
    df_last = None
    reservoir_dict = None

    # The first request on website defined on urls variable
    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url)

    # Callback of start_requests
    def parse(self, response, **kwargs):
        # Get list of revervoirs saved on pickle file
        # This file is created by new_files spider
        self.reservoir_dict = pickle.load(open(f'ana/datasets/reservoirs_list.sav', 'rb'))
        # Get files salved on local machine
        files = [f for f in os.listdir('ana/datasets') if '.csv' in f]
        # If exists files on local update them
        if files:
            for file in tqdm(files, 'Files found:'):
                splited_file = file.split('.')
                reservoir_code = self.reservoir_dict[splited_file[0]]
                df_last = pd.read_csv(fr'ana/datasets/{file}')
                last_day = pd.to_datetime(df_last['Data da Medição'].iloc[-1], format="%d/%m/%Y")
                start = (last_day + timedelta(1)).strftime('%d/%m/%Y')
                end = datetime.today().strftime('%d/%m/%Y')
                self.df_last = df_last
                # Requistion passing new period
                # start = Date of last record identified on file + one day and
                # end = today
                yield scrapy.Request(
                    f'https://www.ana.gov.br/sar0/Medicao?dropDownListReservatorios={reservoir_code}'
                    f'&dataInicial={start}&dataFinal={end}&button=Buscar#', callback=self.parse_reservoirs)

    # Callback of request
    def parse_reservoirs(self, response):
        # Get the content passed by the request
        df_new = pd.read_html(response.text, decimal=',', thousands='.')[0]
        # Reverting the Reservoir List (key <-> value)
        dict_reservoir_reverse = dict()
        for key_rev, value_rev in self.reservoir_dict.items():
            dict_reservoir_reverse[value_rev] = key_rev
        reservoir_code = str(response.url).split('=')[1].split('&')[0]
        reservoir_name = dict_reservoir_reverse[reservoir_code]
        # checking if there are records in the dataframe
        if len(df_new) > 0:
            print(f'Accessing: {response.url}.')
            print(f'Reservoir: {reservoir_name}')
            print(f'{len(df_new)} new records was found.')
            print('---------------------------------------')
            # Concating new records
            df_updated = pd.concat([self.df_last, df_new], ignore_index=True)
            # object that stores the dataframe
            item = AnaItem()
            item['content_table'] = df_updated
            item['reservoir_name'] = reservoir_name
            # The pipelines.py script file is responsible for handling the object item
            yield item
        else:
            print(f'Accessing: {response.url}.')
            print(f'Reservoir: {reservoir_name}')
            print(f'No new records found.')
            print('---------------------------------------')
