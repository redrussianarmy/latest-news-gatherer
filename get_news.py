import feedparser 
import re, html
from queue import Queue
import os.path
import pickle
from threading import Thread, Lock
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize, sent_tokenize
import time
from copy import deepcopy
from sources import sources

class News:
    def __init__(self):
        self.dict_lock = Lock()
        self.news_dict = {}
        self.fileName = "news.pickle"
        self.filePath = os.path.dirname(os.path.abspath(__file__)) + "/news.pickle"
    
    def _write_to_dict(self, source, category, news):
        '''
            Writes to dictionary
        '''
        with self.dict_lock:
            if not (source,category) in self.news_dict:
                self.news_dict[source,category] = []
            self.news_dict[source,category] = news

    def _write_to_file(self):
        '''
            Writes to file from dictionary
        '''
        with open(os.path.dirname(os.path.abspath(__file__)) + "/" + self.fileName, "wb") as pickle_file:
            try:
                pickle.dump(self.news_dict, pickle_file)
            except:
                print("Writing was failed!") 

    def _read_from_file(self):      
        if os.path.exists(self.filePath):
            with open(os.path.dirname(os.path.abspath(__file__)) + "/" + self.fileName, "rb") as pickle_file:
                return self._read_from_dict(pickle_file)
        else:
            empty_dict = {}
            self._write_to_file()
            return empty_dict
    
    def _read_from_dict(self, pickle_file):
        '''
            returns dictionary from pickle file
        '''
        with self.dict_lock:
            return pickle.load(pickle_file)
    
    def _limit(self, news_list, char_limit):
        '''
            returns limited content
            input 1: description list
            input 2: character limit
        '''
        content = ""
        for item in news_list:                        
            if (len(content)+len(item)) > char_limit:
                if len(content) == 0:
                    content += item
                    content = content[:char_limit] # for a sentence bigger than char_limit
                    return content
                break
            else: 
                content += item
        return content
    
    def _filter(self, feed_entry):
        '''
            returns filtered entry
            input: raw feed entry
        '''
        feed_entry = re.sub("<[^>]+>|\xa0|Devamı için tıklayınız", "", feed_entry)
        feed_entry = html.unescape(feed_entry)
        feed_entry = sent_tokenize(feed_entry)      
        return feed_entry
    
    def _get_dict(self):
        '''
            returns deep copy of news_dict
        '''
        return deepcopy(self.news_dict)       
    
    def load_news(self):
        '''
            Loads news to pickle file in every x seconds
        '''
        char_limit = 250
        sleep_time_of_load_news = 300
        while True:
            for (source,category) in sources:
                try:
                    feedurl = sources[source,category]
                    thefeed = feedparser.parse(feedurl)
                    description = thefeed.entries[0].get("description")            
                except:
                    print(f'data could not be parsed from {source} / {category}')              
                description_list = self._filter(description)
                content = self._limit(description_list, char_limit)               
                self._write_to_dict(source, category, content)
                self._write_to_file()   
            time.sleep(sleep_time_of_load_news)
    
    def run(self, in_queue, out_queue):
        '''
            Sends content of given source and category with reading related pickle file
            args:
                in_queue: (source, category)
                out_queue: (source, category, content)
            return:
                news content of a given news source and category
        '''
        out_reading = self._get_dict()
        while True:
            in_dict = in_queue.get()
            if all([x in in_dict.keys() for x in ["source","category"]]):              
                source = in_dict['source']
                category = in_dict['category']        
            else:
                raise Exception("all slots need to be present")     
            out_reading = self._read_from_file()
            # pick key matched result
            if source and category and (source, category) in out_reading:
                content = out_reading[source, category]
                
                output = {'source': source, 'category': category, 'content': content}  
            else:
                output = {'source': '', 'category': '', 'content': ''}
            out_queue.put(output)

if __name__ == "__main__":
    q1 = Queue()
    q2 = Queue()
    news = News() 
    th1 = Thread(target=news.load_news, args=())
    th2 = Thread(target=news.run, args=(q1,q2))
    th1.start()
    th2.start()
    while True:
        q1.put({"source":input(), "category":input()})
        print(q2.get())