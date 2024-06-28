import random
import fake_useragent
import pandas as pd

import re
import json
import requests
import time

import tkinter as tk
from tkinter import filedialog

class DeepTranslator:
    def __init__(self, chunk_size=16, separator=";", prev_words_count=4, next_words_count=1) -> None:
        self.prev_words_count = prev_words_count
        self.next_words_count = next_words_count

        self.cookies = {
            'userCountry': 'RU',
            'dapUid': '7aaa8b21-9db0-43f9-81ca-03e49708a788',
            'privacySettings': '%7B%22v%22%3A%221%22%2C%22t%22%3A1719446400%2C%22m%22%3A%22LAX_AUTO%22%2C%22consent%22%3A%5B%22NECESSARY%22%2C%22PERFORMANCE%22%2C%22COMFORT%22%2C%22MARKETING%22%5D%7D',
            'LMTBID': 'v2|90d17b61-3b12-4add-a7b5-349a2ec1e025|543101c4481975a2e7b02957ea67d43b',
            'INGRESSCOOKIE': 'b533493fd238b170ffb5de48c546c3ac|a6d4ac311669391fc997a6a267dc91c0',
            'releaseGroups': '6402.DWFA-716.2.3_8783.DF-3926.1.1_11456.AAEXP-9760.1.1_11462.AAEXP-9766.1.1_2413.DWFA-524.2.4_4854.DM-1255.2.5_5719.DWFA-761.2.2_10795.CEX-106.2.1_11448.AAEXP-9752.1.1_11465.AAEXP-9769.1.1_4650.AP-312.2.8_8564.SEO-656.2.2_10449.DF-3959.1.1_10380.DF-3973.2.2_11444.AAEXP-9748.1.1_11446.AAEXP-9750.1.1_11454.AAEXP-9758.1.1_6727.B2B-777.2.2_7759.DWFA-814.2.2_9855.WTT-1235.2.4_11441.AAEXP-9745.2.1_11443.AAEXP-9747.2.1_11461.AAEXP-9765.1.1_1483.DM-821.2.2_6732.DF-3818.2.4_11437.AAEXP-9741.2.1_4321.B2B-679.2.2_4853.DF-3503.1.1_11442.AAEXP-9746.1.1_11447.AAEXP-9751.2.1_220.DF-1925.1.9_2656.DM-1177.2.2_2962.DF-3552.2.6_10382.DF-3962.1.2_10551.DAL-1134.2.1_10794.DF-3869.2.1_11439.AAEXP-9743.2.1_2455.DPAY-2828.2.2_5376.WDW-360.1.2_8776.DM-1442.2.2_8392.DWFA-813.2.2_9546.TC-1165.2.4_11449.AAEXP-9753.1.1_11455.AAEXP-9759.1.1_11550.SEO-706.1.1_4121.WDW-356.2.5_7616.DWFA-777.2.2_8253.DWFA-625.2.2_7617.DWFA-774.2.2_3283.DWFA-661.2.2_4478.SI-606.2.3_7584.TACO-60.2.2_9824.AP-523.1.2_10379.DF-3874.2.2_11438.AAEXP-9742.2.1_11445.AAEXP-9749.1.1_11458.AAEXP-9762.1.1_3961.B2B-663.2.3_4322.DWFA-689.2.2_8393.DPAY-3431.2.2_11459.AAEXP-9763.1.1_11463.AAEXP-9767.1.1_1583.DM-807.2.5_2373.DM-1113.2.4_9683.SEO-747.2.2_5560.DWFA-638.2.2_11451.AAEXP-9755.1.1_11466.AAEXP-9770.1.1_2055.DM-814.2.3_8391.DM-1630.2.2_8635.DM-1158.2.3_7794.B2B-950.2.4_8041.DM-1581.2.2_11464.AAEXP-9768.1.1_11547.DF-3929.2.1_3939.B2B-596.1.1_5562.DWFA-732.2.2_5707.TACO-104.2.2_10753.TACO-145.1.2_11450.AAEXP-9754.1.1_11453.AAEXP-9757.1.1_11460.AAEXP-9764.1.1_7758.B2B-949.2.3_8287.TC-1035.2.5_10381.DF-3974.2.2_11457.AAEXP-9761.1.1_3613.WDW-267.2.2_10550.DWFA-884.2.2_11452.AAEXP-9756.1.1_11440.AAEXP-9744.1.1_975.DM-609.2.3_6359.DM-1411.2.10_10238.MTD-392.2.2',
            'dapVn': '2',
            'dapSid': '%7B%22sid%22%3A%2289c65d03-81d9-4d50-9f7b-9030447df6d0%22%2C%22lastUpdate%22%3A1719550942%7D',
        }
        self.params = {
            'method': 'LMT_handle_jobs',
        }
        
        self.src_path = self.choose_file()
        self.df = pd.read_csv(self.src_path, sep=";")

        self.chunks_size = chunk_size
        self.iterator = 0
        self.row_counter = 0
        self.total_len = self.df.count()[0]

        self.translated_text = []
        self.separator = separator

        self.current_words_pack = ""

        self.main_cycle()

    @staticmethod
    def del_backshah_r_and_n(element):
        return re.sub(r'(?:(?<!$)[\r\n]+|(?<!$)(?<=\r\n)[\r\n]+)', '', element)


    def form_json_data(self, current_array: list):
        i = 0
        jobs_array = []
        for element in current_array:
            current_dictionary = {
                'kind': 'default',
                'sentences': [
                    {
                        'text': self.del_backshah_r_and_n(str(element)).replace('"', "`"),
                        'id': i + 1,
                        'prefix': '',
                    },
                ],
                'raw_en_context_before': [self.get_previous_element(current_array, i, iteration) for iteration in range(self.prev_words_count, -1, -1)],
                'raw_en_context_after': [self.get_next_element(current_array, i, iteration) for iteration in range(self.next_words_count)],
                'preferred_num_beams': 1,
            }
            jobs_array.append(current_dictionary)
            i += 1
        return jobs_array

    def translate(self, iteration: int):
        ua = fake_useragent.UserAgent()
        current_pack = self.get_array_from_csv()

        if len(current_pack) == 0:
            return False

        headers = {
            'accept': '*/*',
            'accept-language': 'ru,en;q=0.9',
            'content-type': 'application/json',
            # 'cookie': 'userCountry=RU; dapUid=7aaa8b21-9db0-43f9-81ca-03e49708a788; privacySettings=%7B%22v%22%3A%221%22%2C%22t%22%3A1719446400%2C%22m%22%3A%22LAX_AUTO%22%2C%22consent%22%3A%5B%22NECESSARY%22%2C%22PERFORMANCE%22%2C%22COMFORT%22%2C%22MARKETING%22%5D%7D; LMTBID=v2|90d17b61-3b12-4add-a7b5-349a2ec1e025|543101c4481975a2e7b02957ea67d43b; INGRESSCOOKIE=b533493fd238b170ffb5de48c546c3ac|a6d4ac311669391fc997a6a267dc91c0; releaseGroups=6402.DWFA-716.2.3_8783.DF-3926.1.1_11456.AAEXP-9760.1.1_11462.AAEXP-9766.1.1_2413.DWFA-524.2.4_4854.DM-1255.2.5_5719.DWFA-761.2.2_10795.CEX-106.2.1_11448.AAEXP-9752.1.1_11465.AAEXP-9769.1.1_4650.AP-312.2.8_8564.SEO-656.2.2_10449.DF-3959.1.1_10380.DF-3973.2.2_11444.AAEXP-9748.1.1_11446.AAEXP-9750.1.1_11454.AAEXP-9758.1.1_6727.B2B-777.2.2_7759.DWFA-814.2.2_9855.WTT-1235.2.4_11441.AAEXP-9745.2.1_11443.AAEXP-9747.2.1_11461.AAEXP-9765.1.1_1483.DM-821.2.2_6732.DF-3818.2.4_11437.AAEXP-9741.2.1_4321.B2B-679.2.2_4853.DF-3503.1.1_11442.AAEXP-9746.1.1_11447.AAEXP-9751.2.1_220.DF-1925.1.9_2656.DM-1177.2.2_2962.DF-3552.2.6_10382.DF-3962.1.2_10551.DAL-1134.2.1_10794.DF-3869.2.1_11439.AAEXP-9743.2.1_2455.DPAY-2828.2.2_5376.WDW-360.1.2_8776.DM-1442.2.2_8392.DWFA-813.2.2_9546.TC-1165.2.4_11449.AAEXP-9753.1.1_11455.AAEXP-9759.1.1_11550.SEO-706.1.1_4121.WDW-356.2.5_7616.DWFA-777.2.2_8253.DWFA-625.2.2_7617.DWFA-774.2.2_3283.DWFA-661.2.2_4478.SI-606.2.3_7584.TACO-60.2.2_9824.AP-523.1.2_10379.DF-3874.2.2_11438.AAEXP-9742.2.1_11445.AAEXP-9749.1.1_11458.AAEXP-9762.1.1_3961.B2B-663.2.3_4322.DWFA-689.2.2_8393.DPAY-3431.2.2_11459.AAEXP-9763.1.1_11463.AAEXP-9767.1.1_1583.DM-807.2.5_2373.DM-1113.2.4_9683.SEO-747.2.2_5560.DWFA-638.2.2_11451.AAEXP-9755.1.1_11466.AAEXP-9770.1.1_2055.DM-814.2.3_8391.DM-1630.2.2_8635.DM-1158.2.3_7794.B2B-950.2.4_8041.DM-1581.2.2_11464.AAEXP-9768.1.1_11547.DF-3929.2.1_3939.B2B-596.1.1_5562.DWFA-732.2.2_5707.TACO-104.2.2_10753.TACO-145.1.2_11450.AAEXP-9754.1.1_11453.AAEXP-9757.1.1_11460.AAEXP-9764.1.1_7758.B2B-949.2.3_8287.TC-1035.2.5_10381.DF-3974.2.2_11457.AAEXP-9761.1.1_3613.WDW-267.2.2_10550.DWFA-884.2.2_11452.AAEXP-9756.1.1_11440.AAEXP-9744.1.1_975.DM-609.2.3_6359.DM-1411.2.10_10238.MTD-392.2.2; dapVn=2; dapSid=%7B%22sid%22%3A%2289c65d03-81d9-4d50-9f7b-9030447df6d0%22%2C%22lastUpdate%22%3A1719550942%7D',
            'origin': 'https://www.deepl.com',
            'priority': 'u=1, i',
            'referer': 'https://www.deepl.com/',
            'sec-ch-ua': '"Chromium";v="124", "YaBrowser";v="24.6", "Not-A.Brand";v="99", "Yowser";v="2.5"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': ua.random,
        }

        json_data = {
            'jsonrpc': '2.0',
            'method': 'LMT_handle_jobs',
            'params': {
                'jobs': self.form_json_data(current_array=current_pack),
                'lang': {
                    'target_lang': 'EN',
                    'preference': {
                        'weight': {},
                        'default': 'default',
                    },
                    'source_lang_computed': 'RU',
                },
                'priority': 1,
                'commonJobParams': {
                    'regionalVariant': 'en-US',
                    'mode': 'translate',
                    'browserType': 1,
                    'textType': 'plaintext',
                },
                'timestamp': 1719550942330 + iteration * 100,
            },
            'id': 40710008 + iteration,
        }
        
        response = requests.post('https://www2.deepl.com/jsonrpc', params=self.params, cookies=self.cookies, headers=headers, json=json_data)
        print(response.json())
        self.write_translated_words(response.json())
        
        return True

    def write_translated_words(self, json_response: json):
        for element in json_response['result']['translations']:
            self.translated_text.append(str(element['beams'][0]['sentences'][0]['text']))

    def choose_file(self):
        root = tk.Tk()
        root.withdraw()  # hide the root window

        file_path = filedialog.askopenfilename(
            title="Выберите файл",
            initialdir="/",  # начальный каталог
            filetypes=(("Все файлы", "*.*"),)  # типы файлов
        )
        if file_path:
            return file_path
        else:
            return None

    def save_file(self):
        root = tk.Tk()
        root.withdraw()  # hide the root window

        file_path = filedialog.asksaveasfilename(
            title="Выберите путь и имя для сохранения файла",
            initialdir="/",  # начальный каталог
            filetypes=(("CSV files", "*.csv"),),  # типы файлов
            defaultextension=".csv"  # расширение файла по умолчанию
        )

        if file_path:
            return file_path
        else:
            return None

    def get_array_from_csv(self) -> list:
        temp_words_array = []

        next_stop = self.iterator + self.chunks_size
        for word_row in range(self.iterator, next_stop):
            if self.iterator >= self.total_len:
                print("Out from getting of array")
                return temp_words_array

            temp_words_array.append(str(self.df.iloc[word_row, 0]).replace('"', "`"))
            self.iterator += 1
            self.row_counter += 1

            if self.iterator == next_stop or self.row_counter == self.total_len:
                return temp_words_array #* Массив

    @staticmethod
    def get_previous_element(current_array: list, current_iteration: int, how_far: int):
        condition = current_iteration - how_far
        if condition <= 0:
            return ''
        else:
            return current_array[current_iteration - how_far]

    @staticmethod
    def get_next_element(current_array: list, current_iteration: int, how_far: int):
        condition = current_iteration + how_far
        arrays_iterator = len(current_array) - 1
        if condition > arrays_iterator:
            return ''
        elif condition == arrays_iterator:
            return current_array[arrays_iterator]
        else:
            return current_array[current_iteration + how_far]

    @property
    def chunks_count(self):
        return int(self.total_len / self.chunks_size) + 1

    def main_cycle(self):
        print("#######################   NEW ITERATION  #######################")
        for i in range(self.chunks_count):
            self.translate(iteration=i)
            time.sleep(random.uniform(1, 5))
            print("Progress:", (len(self.translated_text) / self.total_len) * 100, "%")
        
        self.to_csv()
    
    def to_csv(self):
        # print(len(self.translated_text))
        self.df['translated'] = self.translated_text
        self.df.to_csv(f'{self.save_file()}', index=False, sep=";")


dt = DeepTranslator(chunk_size=15, separator="\n")