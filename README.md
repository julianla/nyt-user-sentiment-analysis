# nyt-user-sentiment-analysis
A project written in Python to perform a sentiment analysis of the user comments made on [nytimes.com](http://nytimes.com) using the [Stanford CoreNLP](http://stanfordnlp.github.io/CoreNLP/index.html).

## Details

This program downloads user comments made on [nytimes.com](http://nytimes.com) using the [New York Times API](https://developer.nytimes.com) either by date or by URL. It then analyzes the comments sentence by sentence using the Stanford CoreNLP and stores the sentiment of each sentence to a `txt` file before calculating the share of very negative, negative, neutral, positive and very positive sentences. These are then saved as a different `txt` file that can later be used for further analysis, visualization etc.

## Installation

### NYT API

First, [request an API key](https://developer.nytimes.com).

### Install Stanford CoreNLP for Python

This follows instructions provided on [stackoverflow](http://stackoverflow.com/questions/32879532/stanford-nlp-for-python/40496870#40496870) by [sds](http://stackoverflow.com/users/850781/sds).
[Download CoreNLP ](http://stanfordnlp.github.io/CoreNLP/) and move the folder to your project directory. Then install [py-corenlp](https://github.com/smilli/py-corenlp/):

`pip install py-corenlp`

## Usage

`from CommentAn import nyt_comments_analysis`

After importing nyt_comments_analysis from CommentAn.py one has to specify the API key and either the date in the format: 'YYYY-MM-DD' (e.g. '2017-02-21') or the URL whose comments one is interested in (e.g. 'https://www.nytimes.com/2016/07/01/nyregion/new-york-city-overcrowded-sidewalks.html').

`nyt = nyt_comments_analysis({'key'}, {'date or url'})`

The program then recognizes the input and adjusts its search accordingly.

### Download Comments

To download the user comments, simply type

`nyt.get_comments()`

in case you want to download all the comments from that date/URL or

`nyt.get_comments({# of comments you want to download})`

if you want to limit your selection.
There are two points to notice here:
* Each API is limited to 1000 calls per day. Given that each call contains 25 comments, it is not possible to download more than 25 000 comments per day.
* If you choose to limit your selection, the number of comments you receive will still be a multiple of 25. This means that if you write nyt.get_comments(28), you will still receive 50 comments (but not more), unless there are less than 50 comments available in total. 

Comments will be saved as `NYT_raw_comments_{title of the article or date}.txt` 

### Predict Sentiment

#### Start the server

Using the command line write:

```
cd stanford-corenlp-full-2016-10-31
java -mx5g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -timeout 100000
```

Then simply type:

`nyt.predict_StanfordNLP()`

Given that the program connects to a server, this process might take some time. While the analysis of comments to articles usually takes a couple of minutes at most, analyzing all the comments on a given date (around 10,000 on average) can take around 2 hours (depending, of course, on your computer). Suggestions and ideas to speed this up are greatly appreciated.

The index of the sentence in the comment, the sentiment as a digit (0,1,2,3,4) and the sentiment as a string (in that order) are stored to the document `StanfordNLP_{title of the article or date}.txt`. The share of very negative, negative, neutral, positive and very positive sentences to the file `{'NLP_results' or 'title of the article'}.txt`. Both documents are stored in the folder `Stanford_NLP_data`.

Tested with Python 2.7.
