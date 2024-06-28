import time
import requests
import urllib.parse
import fake_useragent

import pandas as pd
import tkinter as tk
from tkinter import filedialog
ua = fake_useragent.UserAgent()


class TranslateData:
    def __init__(self, chunk_size=100, separator="\n"):
        self.src_path = self.choose_file()
        self.df = pd.read_csv(self.src_path, sep=";")
        
        self.chunks_size = chunk_size
        self.iterator = 0
        self.row_counter = 0
        self.total_len = self.df.count()[0]

        self.translated_text = []
        self.separator = separator

        self.main_cycle()

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

    @property
    def chunks_count(self):
        return int(self.total_len / self.chunks_size) +1

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

    def translate(self):
        ua = fake_useragent.UserAgent()
        prompt = self.get_array_from_csv()
        
        if len(prompt) == 0:
            return "PUSTOTA"
        
        text_to_translate = f"{self.separator} ".join(prompt)
        encoded_text = urllib.parse.quote(text_to_translate)

        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'authorization': 'Bearer a_25rccaCYcBC9ARqMODx2BV2M0wNZgDCEl3jryYSgYZtF1a702PVi4sxqi2AmZWyCcw4x209VXnCYwesx',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://lingvanex.com',
            'priority': 'u=1, i',
            'referer': 'https://lingvanex.com/',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': ua.random
        }

        data = f'from=ru_RU&to=en_US&text={encoded_text}&platform=dp'

        response = requests.post('https://api-b2b.backenster.com/b1/api/v3/translate/', headers=headers, data=data)

        translated_data = response.json()['result'].split(f"{self.separator}")
        return translated_data
    
    def main_cycle(self):
        print(f"""
 ___  __    _  _______  _______  __   __  _______  __   __  ___  __   __  __   __  __   __ 
|   ||  |  | ||       ||       ||  |_|  ||   _   ||  |_|  ||   ||  |_|  ||  | |  ||  |_|  |
|   ||   |_| ||    ___||   _   ||       ||  |_|  ||       ||   ||       ||  | |  ||       |
|   ||       ||   |___ |  | |  ||       ||       ||       ||   ||       ||  |_|  ||       |
|   ||  _    ||    ___||  |_|  ||       ||       | |     | |   ||       ||       ||       |
|   || | |   ||   |    |       || ||_|| ||   _   ||   _   ||   || ||_|| ||       || ||_|| |
|___||_|  |__||___|    |_______||_|   |_||__| |__||__| |__||___||_|   |_||_______||_|   |_|
""")
        time.sleep(1)
        for i in range(self.chunks_count):
            current_pack = self.translate()
            if current_pack == "PUSTOTA":
                break
            for item in current_pack:       
                self.translated_text.append(item)
            print("Progress:", (len(self.translated_text) / self.total_len) * 100, "%")
        
        self.to_csv()
    
    def to_csv(self):
        # print(len(self.translated_text))
        self.df['translated'] = self.translated_text
        self.df.to_csv(f'{self.save_file()}', index=False, sep=";")


translator = TranslateData(chunk_size=50)