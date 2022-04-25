import scrapy
from ..items import AnaItem
import pandas as pd
import pickle
from datetime import datetime, timedelta
import os
from tqdm import tqdm

GREEN = '\033[92m[+]\033[0m'
YELLOW = '\033[33m[+]\033[0m'


'''
    This script is responsible for updating existing files on your local machine.
    It checks if there are files in the project's <datasets> folder, if there is, it 
    takes the date on the last update, takes today's date and checks if there are 
    new records in that period.
'''


class UpdadeRecordsSpider(scrapy.Spider):
    # Spiser name
    name = 'update_records'
    urls = ['https://www.ana.gov.br/sar0/MedicaoSin']
    reservoir_dict = None

    # The first request on website defined on urls variable
    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url)

    # Callback of start_requests
    def parse(self, response, **kwargs):
        # Get dict of revervoirs saved on pickle file
        # This file is created by new_files spider
        self.reservoir_dict = pickle.load(open(f'ana/datasets/reservoirs_list.sav', 'rb'))
        # Get files salved on local machine
        files = [f for f in os.listdir('ana/datasets') if '.csv' in f]
        # If exists files on local update them
        to_update = {name[:-4]: self.reservoir_dict[name[:-4]] for name in files}
        print(f" {GREEN} Looking for new records.")
        if to_update:
            for reservoir in tqdm(to_update, 'Files found:'):
                reservoir_code = to_update[reservoir]
                df_last = pd.read_csv(fr'ana/datasets/{reservoir}.csv')
                last_day = pd.to_datetime(df_last['Data da Medição'].iloc[-1], format="%d/%m/%Y")
                start = (last_day + timedelta(1)).strftime('%d/%m/%Y')
                end = (datetime.today() - timedelta(1)).strftime('%d/%m/%Y')
                # Requistion passing new period
                # start = Date of last record identified on file + one day and
                # end = today - one day
                yield scrapy.Request(
                    f'https://www.ana.gov.br/sar0/MedicaoSin?dropDownListReservatorios={reservoir_code}'
                    f'&dataInicial={start}&dataFinal={end}&button=Buscar#', callback=self.parse_reservoirs)

    # Callback of request
    def parse_reservoirs(self, response):
        # Get the content passed by the request
        df_new = pd.read_html(response.text, decimal=',', thousands='.')[0]
        # Reverting the Reservoir dict (key <-> value)
        dict_reservoir_reverse = dict()
        for key_rev, value_rev in self.reservoir_dict.items():
            dict_reservoir_reverse[value_rev] = key_rev
        reservoir_code = str(response.url).split('=')[1].split('&')[0]
        reservoir_name = dict_reservoir_reverse[reservoir_code]
        # checking if there are records in the dataframe
        if len(df_new) > 0:
            df_last = pd.read_csv(f'ana/datasets/{reservoir_name}.csv')
            print(f'{GREEN} {reservoir_name}: {len(df_new)} new records was found.')
            # Concating new records
            df_updated = pd.concat([df_last, df_new], ignore_index=True)
            # object that stores the dataframe
            item = AnaItem()
            item['content_table'] = df_updated
            item['reservoir_name'] = reservoir_name
            # The pipelines.py script file is responsible for handling the object item
            yield item
        else:
            print(f" {YELLOW} {reservoir_name}: No new records found.")

