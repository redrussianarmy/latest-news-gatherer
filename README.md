# Latest News Gatherer

With this gatherer, user will be able to receive the latest news in the category of the news source user wants.

In this version, only Turkish news sources are available. These are:

* CnnTürk - general, sport, economy, magazine
* NTV - general, sport, economy
* Hürriyet - general, sport, economy, magazine
* Milliyet - general, economy, magazine
* Sabah - general, sport, economy
* Cumhuriyet - general
* HaberTürk - general, sport, economy, magazine
* AHaber - general, sport, economy, magazine
* TRTHaber - general, sport, economy
* BBCTürkçe - general, economy
* Sözcü - general
* Sputniknews - general
* Beinsports - sport

When the system is started, latest news is received with a thread running in parallel and saved to the file.

## Installation
In order to `clone` the complete content of this folder use the command:

```git
git clone git@github.com:redrussianarmy/paragraph-shortener.git
```

## Usage
```
root  
└── get_news.py  
└── sources.py  
└── ...
```

Here is the sample code:
```python
from get_news import News
from queue import Queue
from threading import Thread

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
```

When the source and category are entered as an input to the queue, the result is:
