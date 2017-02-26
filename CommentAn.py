import pickle, re, sys, os, json, urllib, time
from progress.bar import Bar
import numpy as np
from sklearn.naive_bayes import MultinomialNB
from pycorenlp import StanfordCoreNLP
import pandas as pd


class nyt_comments_analysis:
    """ Class for analyzing user sentiment in the New York Times comment section.
     
    Attributes:
        key: Your NYT API Key. Available here: https://developer.nytimes.com/signup
        date_or_url: Either the URL of the NYT article or the date of interest. 
        title: Will be attached to the end of the NYT_raw_comments file (either the date or the title of the article).
        results_document_name: Name of the results document.
    """
    
    def __init__(self, key, date_or_url):
        self.key = key
        self.date_or_url = date_or_url
        # Choose title of the raw result documents depending on whether a date or an URL was specified.
        if ".com" in date_or_url:
            title = re.findall('.*/(.*)[.]html', date_or_url)
            self.title = title[0]
            self.results_document_name = title
        else:
            self.title = date_or_url
            self.results_document_name = 'NLP_results'
        
    def get_comments(self, number_of_com = 0):
        """ Downloads user comments from the New York Times using the NYT API.
        Only 25 comments are returned per request. Setting offset = 1 returns
        the first 25 comments, offset = 2 return comments 2 to 26, offset = 3
        return comments 3-26 etc. Thus I loop over the comments by setting
        offset to 1, 26, 51 etc. Comments are written to the file 
        NYT_raw_comments_{title of the article or date}.txt. """

        # Choose right URI depending on whether a date or an URL was specified.
        if ".com" in self.date_or_url:
            URI =    'http://api.nytimes.com/svc/community/v3/user-content/url.json?api-key=%s&url=%s&sort=newest&offset=' %(self.key,self.date_or_url)
        else:
            URI =    'http://api.nytimes.com/svc/community/v3/user-content/by-date.json?api-key=%s&date=%s&offset=' %(self.key,self.date_or_url)
        # If no specific number of comments is specified download all of them.
        if number_of_com == 0:
            ufile = urllib.urlopen(URI + '1')    
            text = ufile.read()    
            text_json = json.loads(text)
            number_of_results = text_json["results"]["totalCommentsFound"] # Extract the text of the comments and the number of comments found on a given date
        else:
            number_of_results = int(float(number_of_com))
        # Write the comments to the file NYT_raw_comments_URL/DATE.txt
        with open('NYT_raw_comments_%s.txt' %(self.title), 'a') as f:
            for i in range(1, number_of_results+1, 25):
                ufile = urllib.urlopen(URI + '%s' %i)    # get file-like object for url
                info = ufile.info()     
                print info # Print information about the url content
                text = ufile.read() 
                f.write(text)
                time.sleep(0.3) # One can only make 5 calls per second. This short sleep takes care of that.

    def split_into_sentences(self, text):
        """ This function splits the comments into sentences and is provided by
        http://stackoverflow.com/users/3204551/deduplicator
        on Stack Overflow:
        http://stackoverflow.com/questions/4576077/python-split-text-on-sentences """
    
        caps = "([A-Z])"
        prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
        suffixes = "(Inc|Ltd|Jr|Sr|Co)"
        starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
        acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
        websites = "[.](com|net|org|io|gov)"
        text = " " + text + "    "
        text = text.replace("\n"," ")
        text = re.sub(prefixes,"\\1<prd>",text)
        text = re.sub(websites,"<prd>\\1",text)
        if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
        text = re.sub("\s" + caps + "[.] "," \\1<prd> ",text)
        text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
        text = re.sub(caps + "[.]" + caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
        text = re.sub(caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>",text)
        text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
        text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
        text = re.sub(" " + caps + "[.]"," \\1<prd>",text)
        if "\"" in text: text = text.replace(".\"","\".")
        if "!" in text: text = text.replace("!\"","\"!")
        if "?" in text: text = text.replace("?\"","\"?")
        text = text.replace(".",".<stop>")
        text = text.replace("?","?<stop>")
        text = text.replace("!","!<stop>")
        text = text.replace("<prd>",".")
        sentences = text.split("<stop>")
        sentences = sentences[:-1]
        sentences = [s.strip() for s in sentences]
        return sentences
        
    def prepare_comments(self):
        # Prepares the comments for analysis.
        with open('NYT_raw_comments_%s.txt' %(self.title), 'rU') as f:
            filecontent = f.readlines()
            # Extract the comments using regular expressions (in this case simpler than using json)
            for l in filecontent:
                commentbody = re.findall('"commentBody":"(.*?)","', l)    
        comments = []
        for comment in commentbody:
            comment = unicode(comment, errors='ignore') # Convert comments to unicode
            comment = re.sub('((www\..+)|(https?://.+))','URL', comment) # Normalize URLs
            comment = re.sub('[\s]+', ' ', comment) # Delete multiple white spaces
            comment = re.sub(r'#([^\s]+)', r'\1', comment) # DeletesHashtags
            comment = comment.strip() # Trim leading and trailing white spaces
            comment = comment.lower()
            comment    = re.sub('<br\\\/>', '', comment) # Delete various symbols
            comment    = re.sub('\\\+','' , comment)
            comment    = re.sub('----','' , comment)
            comments.append(comment)
        """ Split comments into sentences: while the Stanford CoreNLP autmotically
        splits a text into sentences, split_into_sentences() tends to do a better job
        in this case.
        """    
        sentences_split = []
        for comment in comments:
            sentences = self.split_into_sentences(comment) 
            sentences_split.append(sentences) 
        sentences = [item for sublist in sentences_split for item in sublist] # Generate list of sentences
        return sentences
                
    def predict_StanfordNLP(self):
        """ Predicts user sentiment using the Stanford NLP classifier
        and writes the sentiment for each sentence into the file StanfordNLP_{title of the article or date}.txt.
        Then, it writes the share of very negative, negative, neutral, positive and very positive sentences
        to the file {'NLP_results' or 'title of the article'}.txt, which can later be used for visualisation.
        """
        
        sentences = self.prepare_comments()
        owd = os.getcwd()
        if not os.path.exists(owd + '/Stanford_NLP_data'):
            os.makedirs(owd + '/Stanford_NLP_data') # Generate a new folder to store the data if it does not exist yet
        os.chdir(owd + '/Stanford_NLP_data')
        with open('StanfordNLP_%s.txt' %self.title, 'a') as myfile:
            bar = Bar('Processing', max = len(sentences)) # Generate a progressbar
            # Connect to the Stanford Core NLP Server and analyze the comments sentence-by-sentence
            for sentence in sentences: 
                sentence = str(sentence)
                nlp = StanfordCoreNLP('http://localhost:9000')
                res = nlp.annotate(sentence,
                                   properties={
                                       'annotators': 'sentiment',
                                       'outputFormat': 'json',
                                       'timeout': 1000000,
                                   })
                # Write the index of the sentence in a comment, the sentiment value and the sentiment to the file StanfordNLP_DATE.txt 
                for s in res["sentences"]:
                    myfile.write('%d,%s,%s'     %(s["index"], s["sentimentValue"], s["sentiment"]) + '\n') 
                bar.next() 
        # Write the share of each sentiment of the total number of sentences to the document NLP_results.txt
        with open('%s.txt' %self.results_document_name, 'a') as myfile:
            if os.stat('%s.txt' %self.results_document_name).st_size == 0:
                myfile.write('date/title,very negative,negative,neutral,positive,very positive'+ '\n')
            df = pd.read_table("StanfordNLP_%s.txt" %self.title, delimiter=',', names = ['Index', 'Sentiment_Value', 'Sentiment'])
            share_0 = np.mean(df['Sentiment_Value'] == 0) # Calculate shares of the sentiment value
            share_1 = np.mean(df['Sentiment_Value'] == 1)
            share_2 = np.mean(df['Sentiment_Value'] == 2)
            share_3 = np.mean(df['Sentiment_Value'] == 3)
            share_4 = np.mean(df['Sentiment_Value'] == 4)
            myfile.write('%s,%f,%f,%f,%f,%f' %(self.title,share_0,share_1,share_2,share_3,share_4) + '\n')    