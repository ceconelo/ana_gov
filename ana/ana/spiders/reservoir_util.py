import os


class Reservoirs:
    def __init__(self, list_names_reservoirs, response):
        self.list_names_reservoirs = list(list_names_reservoirs)
        self.reservoirs_dict = dict()
        self.response = response

    # This method will get the local files and compare with the dictionary that is being passed
    # And from that, it will return a new dictionary containing the name of the files that do not yet exist.
    @staticmethod
    def reservoirs_to_search(reservoir_dict):
        file_only_names = []
        to_compare_reservoir = dict()
        r_to_c = dict()
        # Get files salved on local machine
        files = [f for f in os.listdir('ana/datasets') if '.csv' in f]
        # If exists files on local update them
        if files:
            # Getting the name of the files.
            for file in files:
                file_only_names.append(file[:-4])
            if reservoir_dict is not None:
                for reservoir in reservoir_dict:
                    for fon in file_only_names:
                        if fon == reservoir:
                            to_compare_reservoir[fon] = reservoir_dict[fon]
                r_to_c = {fnr: reservoir_dict[fnr] for fnr in
                          set(reservoir_dict).difference(to_compare_reservoir)}
                return r_to_c
        return reservoir_dict

    # This method takes the name of all reservoirs on the website
    @staticmethod
    def get_all_reservoris(response):
        # Get list of revervoirs in website
        all_reservoirs = []
        for reservoir in response.xpath('//select[@name="dropDownListReservatorios"]//option')[1:]:
            all_reservoirs.append(str(reservoir.xpath('.//text()').get()).strip())
        return all_reservoirs

    # Transforms the list of reservoir names into a key:value dictionary
    # reservoir : cod_reservoir
    def dict_reservoirs(self):
        for reservoir in self.list_names_reservoirs:
            key = str(reservoir).upper()
            value = self.get_code(reservoir)
            self.reservoirs_dict[key] = value
        return self.reservoirs_dict

    def get_code(self, reservoir):
        return self.response.xpath(f'.//option[contains(text(),"{str(reservoir).upper()}")]/@value').get()
