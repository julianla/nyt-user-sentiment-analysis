import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')
import os, sys


def plot_StanfordNLP(dates):
  # Plots the sentiment share on the y-axis and the date on x-axis
  owd = os.getcwd()
  os.chdir(owd + '/Stanford_NLP_data')
  df = pd.read_table('NLP_results.txt', delimiter=',')
  df['date'] = pd.to_datetime(df['date'])
  df.index = df['date']
  del df['date']
  ax = df.resample('D').mean().plot(lw=2,colormap='jet',marker='.',markersize=10,title='User Sentiment in the NYT Comment Section')
  ax.set_ylabel("Sentiment Share")
  plt.savefig('Sentiment Tracker.png')


if __name__ == "__main__": 
  if '--args' not in sys.argv:
    print >> sys.stderr, 'Please pass the "--args" flag followed by a list of dates'
    sys.exit(1) 
  dates = sys.argv[sys.argv.index('--args')+1:] # everything passed after --args
  plot_StanfordNLP(dates)
    
    
