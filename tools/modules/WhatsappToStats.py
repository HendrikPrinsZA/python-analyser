import re
from xmlrpc.client import Boolean
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import *
import datetime as dt # To-do: convert to datetime
from matplotlib.ticker import MaxNLocator
from seaborn import *
from wordcloud import WordCloud,STOPWORDS
from nltk import *
from modules.helpers import *

from modules.helpers import save_list_as_json

LINK_REGEX = r"""((?:(?:https|ftp|http)?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|org|uk)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|uk|ac)\b/?(?!@)))"""
MEDIA_REGEX = r'(GIF|image|video) omitted'
NOTIFICATION_REGEX = r'(created this group|added you)'
IGNORE_WORDS_REGEX = r'(happy|birthday|thank|https)'

# Source: https://www.analyticsvidhya.com/blog/2021/04/whatsapp-group-chat-analyzer-using-python/
class WhatsappToStats:
    def __init__(self, file_path: str, datetime_from: datetime) -> None:
        if not os.path.isfile(file_path):
            print(f"Unable to find the file '{file_path}'")

        self.today = datetime.now().strftime("%Y-%m-%d")
        self.path_to_storage = get_path_to_storage()
        self.path_to_reports = f"{self.path_to_storage}/reports/whatsapp"

        if not os.path.isdir(self.path_to_reports):
            os.makedirs(self.path_to_reports, exist_ok=True)

        self.datetime_from = datetime_from
        self.datetime_from_title = f"Since {self.datetime_from.__format__('%Y-%m-%d')}"
        
        data = self.get_data(file_path)
        self.data = self.filter_data(data)

    def filter_data(self, data: list) -> list:
        filtered_data = []

        for record in data:
            record_date = datetime.combine(record[0], record[1])

            if record_date.__lt__(self.datetime_from):
                continue
            
            filtered_data.append(record)
        
        return filtered_data

    # Expected format: [2022/05/27, 10:22:01]
    def get_line_datetime(self, line: str) -> datetime:
        pattern = '^\[(([0-9]+)(\/)([0-9]+)(\/)([0-9][0-9]),\s(\d{2}):(\d{2}):(\d{2}))\]\s'
        result = re.match(pattern, line)
        
        if not result:
            return False 

        try:
            date_string = result[1]
        except:
            return None
        
        date_string = date_string.replace(',', '')
        try:
            return datetime.strptime(date_string, '%Y/%m/%d %H:%M:%S')
        except:
            return None
    
    def line_starts_with_datetime(self, line: str) -> datetime:
        date_time = self.get_line_datetime(line)
        if not date_time:
            return False
        return True

    def get_line_without_datetime(self, line: str) -> str:
        date_time = self.get_line_datetime(line)
        
        if not date_time:
            return line

        date_string = f"[{date_time.__format__('%Y/%m/%d, %H:%M:%S')}] "
        return line.replace(date_string, '')

    def get_line_author(self, line: str) -> str:
        author, _ = self.get_line_author_and_message(line)
        return author

    # To-do: repeat the date strip for consistency
    def get_line_author_and_message(self, line: str) -> str:
        author = None 
        message = None
        line_parts = line.split(':')
        
        if len(line_parts) > 1:
            if not line_parts[0].endswith('https'):
                author = line_parts.pop(0)
                author = author.strip()
                author = author.split(' ')[0]
        
        message = (':'.join(line_parts)).strip()

        return author, message

    def get_data_points(self, line) -> date and time and str and str:
        date = None
        time = None
        
        date_time = self.get_line_datetime(line)
        if date_time is not None:
            date = date_time.date()
            time = date_time.time()

            line = self.get_line_without_datetime(line)
        
        author, message = self.get_line_author_and_message(line)
        return date, time, author, message

    def ignore_line(self, line: str) -> Boolean:
        if len(line) == 0:
            return True 

        if line.endswith('created this group'):
            return True
        
        if line.endswith('added you'):
            return True

        return False

    def get_data(self, file_path: str) -> list:
        data = []
        with open(file_path, encoding='utf-8') as fp:
            fp.readline() # skip the first line (encryption message)
            message_buffer = [] 
            date, time, author = None, None, None
            while True:
                line = fp.readline()
                if not line:
                    break

                # Sanatise the strings
                # - remove non ascii, like [U+200E] -> LTR
                # line = (line.encode('utf-8', 'ignore')).decode('utf-8')
                line = f"{line}".strip()

                if self.ignore_line(line):
                    continue

                if self.line_starts_with_datetime(line): 
                    if len(message_buffer) > 0:
                        data.append([date, time, author, ' '.join(message_buffer)])
                        
                        # testing this
                        message_buffer.clear()
                    
                    date, time, author, message = self.get_data_points(line)
                    message_buffer.append(message)
                # (Not sure about this below...)
                # else:
                    # message_buffer.append(line)
        
        fp.close()

        return data

    def get_data_frame(self) -> pd.DataFrame:

        # Ignore when author is none
        data_frame = pd.DataFrame(self.data, columns=['Date', 'Time', 'Author', 'Message'])
        data_frame = data_frame[data_frame['Author'].notnull()]
        data_frame['Date'] = pd.to_datetime(data_frame['Date'])
        
        print(f"Shape: {data_frame.shape}")
        print(f"Unique authors: {data_frame['Author'].nunique()}")
            
        print(f"Processing data")
        weeks = {
            0: 'Monday',
            1: 'Tuesday',
            2: 'Wednesday',
            3: 'Thrusday',
            4: 'Friday',
            5: 'Saturday',
            6: 'Sunday'
        }

        data_frame['Day'] = data_frame['Date'].dt.weekday.map(weeks)
        data_frame = data_frame[[
            'Date',
            'Day',
            'Time',
            'Author',
            'Message'
        ]]

        data_frame['Day'] = data_frame['Day'].astype('category')

        # Looking newborn dataset.
        data_frame.head()

        data_frame['Letters'] = data_frame['Message'].apply(lambda s : len(s))
        data_frame['Words'] = data_frame['Message'].apply(lambda s : len(s.split(' ')))
        data_frame['Links'] = data_frame['Message'].apply(lambda x: re.findall(LINK_REGEX, x)).str.len()
        links = np.sum(data_frame['Links'])
        data_frame['Media'] = data_frame['Message'].apply(lambda x : re.findall(MEDIA_REGEX, x)).str.len()
        media = np.sum(data_frame['Media'])

        return data_frame

    def get_totals(self, data_frame: pd.DataFrame) -> dict:
        messages = data_frame.shape[0]
        words = np.sum(data_frame['Words'])
        links = np.sum(data_frame['Links'])
        media = np.sum(data_frame['Media'])
        return dict({
            'messages': messages,
            'words': words,
            'media': media,
            'links': links,

            'words_per_message': round(words / messages, 5),
            'links_per_message': round(links / messages, 5),
            'media_per_message': round(media / messages, 5),
        })

    def show_wordlist(self, data_frame: pd.DataFrame) -> WordCloud:
        messages = []
        
        # Ignore author names by default
        authors = data_frame['Author'].unique()
        ignore_authors_regex = f"({'|'.join(authors)})"

        filters = [
            NOTIFICATION_REGEX,
            LINK_REGEX,
            MEDIA_REGEX,
            IGNORE_WORDS_REGEX,
            ignore_authors_regex,
        ]

        for message in data_frame['Message']:
            for filter in filters:
                message = re.sub(filter, '', message, flags=re.IGNORECASE)

            if len(message) < 3:
                continue

            messages.append(message)

        text = " ".join(messages)
        wordcloud = WordCloud(
            stopwords=STOPWORDS, 
            background_color="black",
            min_word_length=4
        ).generate(text)
        
        ### Display the generated image:
        fig = plt.figure(figsize=(10,5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        path_to_file = f"{self.path_to_reports}/{self.today}-wordlist.png"
        fig.savefig(path_to_file)
        print(f"Saved to {path_to_file}")
        plt.close()

    def get_stats_per_author(self, data_frame: pd.DataFrame) -> list:
        stats = []
        authors = data_frame['Author'].unique()
        
        for author in authors:
            data_frame_author = data_frame[data_frame['Author'] == author]

            totals = self.get_totals(data_frame_author)
            stats.append({
                'author': author,
                'totals': totals
            })

        return stats

    def graph_top10_messages(self, data_frame: pd.DataFrame):
        data_frame_top10 = data_frame
        data_frame_top10 = data_frame_top10['Author'].value_counts()
        data_frame_top10 = data_frame_top10.head(10)

        bars = data_frame_top10.keys()
        x_pos = np.arange(len(bars))

        fig = plt.figure(figsize=(10,5))
        data_frame_top10.plot.bar()
        plt.xlabel('Authors', fontsize=12)
        plt.ylabel('No. of messages', fontsize=10)
        plt.title(f"Top 10 by messages ({self.datetime_from_title})", fontsize=10)
        plt.xticks(x_pos, bars)
        
        path_to_file = f"{self.path_to_reports}/{self.today}-top10-messages.png"
        fig.savefig(path_to_file)
        print(f"Saved to {path_to_file}")
        plt.close()

    def graph_top10_media(self, data_frame: pd.DataFrame):
        data_frame_top10 = data_frame[data_frame['Media'] > 0]

        # print("Top 10 media")
        # print(data_frame_top10)
        # exit(0)

        if data_frame_top10.__len__() == 0:
            return

        data_frame_top10 = data_frame_top10['Author'].value_counts()
        data_frame_top10 = data_frame_top10.head(10)

        # Debugging
        # print(data_frame_top10)
        # exit(0)

        bars = data_frame_top10.keys()
        x_pos = np.arange(len(bars))

        fig = plt.figure(figsize=(10,5))
        data_frame_top10.plot.bar()

        plt.xlabel('Authors', fontsize=12)
        plt.ylabel('No. of media', fontsize=10)
        plt.title(f"Top 10 by media ({self.datetime_from_title})", fontsize=10)
        plt.xticks(x_pos, bars)
        
        path_to_file = f"{self.path_to_reports}/{self.today}-top10-media.png"
        fig.savefig(path_to_file)
        print(f"Saved to {path_to_file}")
        plt.close()
    
    def graph_top10_links(self, data_frame: pd.DataFrame):
        data_frame_top10 = data_frame[data_frame['Links'] > 0]

        if data_frame_top10.__len__() == 0:
            return

        data_frame_top10 = data_frame_top10['Author'].value_counts()
        data_frame_top10 = data_frame_top10.head(10)

        bars = data_frame_top10.keys()
        x_pos = np.arange(len(bars))

        fig = plt.figure(figsize=(10,5))
        data_frame_top10.plot.bar()

        plt.xlabel('Authors', fontsize=12)
        plt.ylabel('No. of links', fontsize=10)
        plt.title(f"Top 10 by links ({self.datetime_from_title})", fontsize=10)
        plt.xticks(x_pos, bars)
        
        path_to_file = f"{self.path_to_reports}/{self.today}-top10-links.png"
        fig.savefig(path_to_file)
        print(f"Saved to {path_to_file}")
        plt.close()

    """
    For some reason this function is creating 2 instances of plt
    - Not sure what is going on here!?
    """
    def graph_top10_words(self, data_frame: pd.DataFrame):
        data_frame_top10 = data_frame[['Author', 'Words']].groupby('Author').sum()
        data_frame_top10 = data_frame_top10.sort_values('Words', ascending=False).head(10)
        
        # Debugging data frame
        print('Preview of data frame')
        print(data_frame)

        bars = list(data_frame_top10['Words'].keys())
        x_pos = np.arange(len(bars))
        # print({
        #     'bars': bars,
        #     'x_pos': x_pos,
        # })
        
        fig = plt.figure(figsize=(10,5))
        data_frame_top10.plot.bar()
        
        plt.xlabel('Authors', fontsize=12)
        plt.ylabel('No. of words', fontsize=10)
        plt.title(f"Top 10 by word count ({self.datetime_from_title})", fontsize=10)
        plt.xticks(x_pos, bars)
        
        path_to_file = f"{self.path_to_reports}/{self.today}-top10-words.png"
        fig.savefig(path_to_file)
        print(f"Saved to {path_to_file}")
        # plt.show()
        plt.close()

    def show_data(self):
        self.data_frame = self.get_data_frame()
        print("Data Frame")
        print(self.data_frame)

        self.totals = self.get_totals(self.data_frame)
        path_to_file = f"{self.path_to_reports}/{self.today}-totals.json"
        save_list_as_json(self.totals, path_to_file)
        print(f"Saved as {path_to_file}")
        
        self.stats_per_author = self.get_stats_per_author(self.data_frame)
        path_to_file = f"{self.path_to_reports}/{self.today}-author-stats.json"
        save_list_as_json(self.stats_per_author, path_to_file)
        print(f"Saved as {path_to_file}")

        self.graph_top10_messages(self.data_frame)
        self.graph_top10_media(self.data_frame)
        self.graph_top10_links(self.data_frame)
        self.graph_top10_words(self.data_frame)
        self.show_wordlist(self.data_frame)


    


