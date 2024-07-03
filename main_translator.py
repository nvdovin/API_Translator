import re
import time
import requests
import urllib.parse
import fake_useragent

import pandas as pd
import tkinter as tk
from tkinter import filedialog
ua = fake_useragent.UserAgent()


class TranslateData:
    def __init__(self, chunk_size: int=100, separator: str="\n", max_words_len: int=100, delay: float=0):
        print("""
 ___  __    _  _______  _______  __   __  _______  __   __  ___  __   __  __   __  __   __ 
|   ||  |  | ||       ||       ||  |_|  ||   _   ||  |_|  ||   ||  |_|  ||  | |  ||  |_|  |
|   ||   |_| ||    ___||   _   ||       ||  |_|  ||       ||   ||       ||  | |  ||       |
|   ||       ||   |___ |  | |  ||       ||       ||       ||   ||       ||  |_|  ||       |
|   ||  _    ||    ___||  |_|  ||       ||       | |     | |   ||       ||       ||       |
|   || | |   ||   |    |       || ||_|| ||   _   ||   _   ||   || ||_|| ||       || ||_|| |
|___||_|  |__||___|    |_______||_|   |_||__| |__||__| |__||___||_|   |_||_______||_|   |_|
""")
        time.sleep(1)
        self.src_path = self.choose_file()
        self.df = pd.read_csv(self.src_path, sep=";")
        
        self.total_len = self.df.count()[0]
        self.chunks_size = chunk_size
        self.chunks_count = int(self.total_len / self.chunks_size) + 1
        self.iterator = 0
        self.row_counter = 0
        self.max_words_len = max_words_len
        self.delay = delay

        self.translated_text = []
        self.separator = separator

        self.main_cycle()

    def choose_file(self):
        """Выбор файла для перевода"""
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

    @staticmethod
    def del_backslash_r_and_n(element):
        """Удаляет все переносы каретки на новую строку, кроме тех, что стоят в самом конце"""
        return re.sub(r'(?:(?<!$)[\r\n]+|(?<!$)(?<=\r\n)[\r\n]+)', '', element)
    
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

    @staticmethod
    def is_too_big_endpoint(word, max_len=100):
        """Если длина слова больше заданного значения, то ограничивает его до max_len и добавляет троеточие"""
        if len(word) > max_len:
            shorted_word = word[:max_len - 3]
            return shorted_word + "..."
        else:
            return word

    def get_array_from_csv(self) -> list:
        """Забирает очередной пакет слов из DataFrame, предобрабатывает и передает в массив. Предобработка состоит из:
        * Удаляет все переносы каретки на новую строку, кроме тех, что стоят в самом конце
        * Ограничивает длину слова до max_len и добавляет троеточие"""
        
        temp_words_array = []
        next_stop = self.iterator + self.chunks_size

        for word_row in range(self.iterator, next_stop):
            if self.iterator >= self.total_len:
                print("Out from getting of array")
                return temp_words_array
            current_word = str(self.df.iloc[word_row, 0]).replace('"', "")
            temp_words_array.append(self.del_backslash_r_and_n(self.is_too_big_endpoint(current_word, self.max_words_len)))
            self.iterator += 1
            self.row_counter += 1

            if self.iterator == next_stop or self.row_counter == self.total_len:
                return temp_words_array #* Массив

    def translate(self) -> list:
        """Переводит текущий пакет слов. На выходе получает массив из переведенных слов."""
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

        if response.status_code != 200:
            print(f"Error {response.status_code}")
            translated_data = []
            for i in range(self.chunks_size):
                translated_data.append("[?] Translation error") #* Возвращаем пустой массив
        else:
            translated_data = response.json()['result'].split(f"{self.separator}")

        if len(prompt) != len(translated_data):
            print(len(prompt), "/", len(translated_data))
            for empty_part in range(0, abs(len(prompt) - len(translated_data))):
                translated_data.append("[?] Translation error") #* Добавляем пустые части, если их не хватает

        return translated_data
    
    def main_cycle(self):
        """Главный цикл работы скрипта"""
        for i in range(self.chunks_count):
            current_pack = self.translate()
            if current_pack == "PUSTOTA":
                break
            for item in current_pack:       
                self.translated_text.append(item)
            print("Progress:", round((len(self.translated_text) / self.total_len) * 100, 3), "%")
            time.sleep(self.delay)
        self.to_csv()

    def to_csv(self):
        """Сохранение в csv готового файла"""

        arrays_difference = self.total_len - len(self.translated_text)
        if arrays_difference > 0:
            for i in range(0, arrays_difference):
                self.translated_text.append("[?] Translation error") #* Добавляем пустые части, если их не хватает
                print(f"[INFO] Founded {i+1} mistakes")

        self.df['translated'] = self.translated_text
        self.df.to_csv(f'{self.save_file()}', index=False, sep="\n")


translator = TranslateData(chunk_size=50, max_words_len=50)