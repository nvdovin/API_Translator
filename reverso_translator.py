import requests


import random
import fake_useragent
import pandas as pd

import re
import json
import requests
import time

import tkinter as tk
from tkinter import filedialog

ua = fake_useragent.UserAgent()

class DeepTranslator:
    def __init__(self, chunk_size=16, separator="\n") -> None:
        
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
    def del_backslash_r_and_n(element):
        return re.sub(r'(?:(?<!$)[\r\n]+|(?<!$)(?<=\r\n)[\r\n]+)', '', element)

    def translate(self):
        current_pack = self.get_array_from_csv()

        if len(current_pack) == 0:
            return "PUSTOTA"

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://www.reverso.net',
            'priority': 'u=1, i',
            'referer': 'https://www.reverso.net/',
            'sec-ch-ua': '"Chromium";v="124", "YaBrowser";v="24.6", "Not-A.Brand";v="99", "Yowser";v="2.5"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': ua.random,
            'x-reverso-origin': 'translation.web',
        }

        json_data = {
            'format': 'text',
            'from': 'rus',
            'to': 'eng',
            'input':'\n'.join(self.get_array_from_csv()) ,
            'options': {
                'sentenceSplitter': True,
                'origin': 'translation.web',
                'contextResults': True,
                'languageDetection': True,
            },
        }

        response = requests.post('https://api.reverso.net/translate/v1/translation', headers=headers, json=json_data)
        
        translated_words =  response.json()["translation"]
        return translated_words

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

        next_stop = self.row_counter + self.chunks_size
        for word_row in range(self.row_counter, next_stop):
            if self.row_counter >= self.total_len:
                print("Out from getting of array")
                return temp_words_array

            temp_words_array.append(str(self.df.iloc[word_row, 0]).replace('"', "`"))
            self.row_counter += 1

            if self.row_counter == next_stop or self.row_counter == self.total_len:
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
            current_words_pack = self.translate()
            if current_words_pack == "PUSTOTA":
                break
            else:
                for item in current_words_pack:
                    self.translated_text.append(item)
            print("Progress:", (len(self.translated_text) / self.total_len) * 100, "%")
            time.sleep(1)
        self.to_csv()
    
    def to_csv(self):
        # print(len(self.translated_text))
        self.df['translated'] = self.translated_text
        self.df.to_csv(f'{self.save_file()}', index=False, sep=";")


dt = DeepTranslator(chunk_size=50, separator="\n")
