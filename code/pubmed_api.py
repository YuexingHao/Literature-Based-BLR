from pymed import PubMed
import os
import openai
import datetime
import requests
import itertools
import pandas as pd

from IPython.display import display, HTML
import xml.etree.ElementTree as xml

from typing import Union
from pymed.helpers import batches
from pymed.article import PubMedArticle
from pymed.book import PubMedBookArticle

#@title Imports, creating some displays, and the `Conversation` class.
import json
import math

#@title OpenAI API Key
api_key="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" # TODO: Key for Kexin

openai.api_key = api_key #input("Enter your OpenAI API Key:")


class Conversation:
  def __init__(self, init=""):
    self.prompt = init
    self.displayed = ""
    self.responses = []

  def summarize(self, text, dontStop=False):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=self.prompt+text,
        temperature=0,
        max_tokens=100, ## TODO: SETTING=num of one-sent summary length
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
    self.responses.append(response)
    data = json.loads(str(response))
    # display(HTML(renderResponse(data, self.prompt+text, self.displayed)))
    self.prompt = data['choices'][0]['text']
    self.displayed = self.prompt
    return data['choices'][0]['text']

  def query(self, question, qna_prompt="", dontStop=False):
    start_sequence = "\nA:"
    restart_sequence = "\n\nQ: "
    response = openai.Completion.create(
      engine="text-davinci-002",
      prompt=qna_prompt+self.prompt+question,
      temperature=0,
      max_tokens=100,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0,
      stop=["\n"]
    )
    data = json.loads(str(response))
    return data['choices'][0]['text']

  def renderResponse(r, i="This is a test. Hello,", hide="This"):
    probs_count = 10

  def display(self):
    display(HTML(renderResponse(json.loads(str(self.responses[len(self.responses)-1])),'','')))
# Define function: Find longest common substring
# reference: https://stackoverflow.com/questions/18715688/find-common-substring-between-two-strings

def lcs(S,T):
    m = len(S)
    n = len(T)
    counter = [[0]*(n+1) for x in range(m+1)]
    longest = 0
    lcs_set = set()
    for i in range(m):
        for j in range(n):
            if S[i] == T[j]:
                c = counter[i][j] + 1
                counter[i+1][j+1] = c
                if c > longest:
                    lcs_set = set()
                    longest = c
                    lcs_set.add(S[i-c+1:i+1])
                    lcs_set_start = i-c+1
                    lcs_set_end = i+1
                elif c == longest:
                    lcs_set.add(S[i-c+1:i+1])
                    
    if list(lcs_set) == []:
      return (list(lcs_set),int(lcs_set_start),int(lcs_set_end))
    else:
      return (list(lcs_set)[0],int(lcs_set_start),int(lcs_set_end))


def all_lcs(abs,summ):
  # print("ABSTRACT:", abs)
  abs = abs.lower()
  summ = summ.lower()
  lcs_set = []
  span_set = [] # location of the summary texts in abstract
  
  while len(summ.strip().split(" ")) >= 5:
    # while there are three words remaining in the summary
    lcs_i, j, k = lcs(abs,summ)
    lcs_set.append(lcs_i)
    span_set.append((j,k))
    #abs = abs.replace(lcs_i,"")
    summ = summ.replace(lcs_i,"") # remove lcs from abstract
  return (lcs_set,span_set)
  

# Define function: color text function
# reference: https://stackoverflow.com/a/42534887
from IPython.display import HTML as html_print

def cstr(s, color='black'):
    return "<text style=color:{}>{}</text>".format(color, s)

def hl_substring(S,spans,color="red"):
  # display S (str) while highlighting S[i:j]
  spans.sort(key=lambda y: y[1]) # sort spans
  left = S[:spans[0][0]-1]
  output = left
  for k in range(len(spans)):
    i = spans[k][0]
    j = spans[k][1]
    word = S[i:j]
    if k < len(spans)-1:
      right = S[j:spans[k+1][0]]
    else:
      right = S[j+1:]
    
    # print("- red: ", word)
    # print("== black: ", right)
    output = output + ' '.join([cstr(word, color), right])
  
  return html_print(cstr(output, color='black'))


##### ONE-SENTENCE SUMMARY SETUP ######

# init
qna_prompt = """I am a highly intelligent question answering bot. If you ask me a question that is rooted in the following text, I will give you the answer. If you ask me a question that has no clear answer, I will respond with "Unknown"."""
instruction_sum = "Summarize the texts above for a healthcare professional in one sentence:"

# Try summarization
def summarize(abstract):
  
  c1 = Conversation(abstract)
  c1_summary = c1.summarize(instruction_sum).lstrip("\n")
  # print("One-sentence summary:\n", c1_summary)
  # In the abstract: highlight texts that went into the summary
  lcs, spans = all_lcs(abstract,c1_summary)
  return c1_summary
  # return hl_substring(abstract, spans)


# Create a PubMed object that GraphQL can use to query
# Note that the parameters are not required but kindly requested by PubMed Central
# https://www.ncbi.nlm.nih.gov/pmc/tools/developers/
pubmed = PubMed(tool="MyTool", email="my@email.address")

# Create a GraphQL query in plain text

# query = '(Old adults + acute LBP + Low Back Pain)' #TODO: Change it based on each search
query= 'Cognitive impairment, headache, memory loss'
# Execute the query against the API
results = pubmed.query(query, max_results=20) #TO CHANGE MAX_RESULTS 

author_ls=[]
affliation_ls=[]
keywords_ls=[]
art_id_ls=[]
pub_ls=[]
title_ls=[]
abst_ls=[]
summary_ls=[]

# Loop over the retrieved articles
for article in results:
    keyword=None
    # Extract and format information from the article
    article_id = article.pubmed_id.split('\n')[0] # FIX SOME WEIRD ERROR WHEN PUBMED_ID AUTO RETURNNED A LIST OF PUBMEDID  
    title = article.title
    if article.keywords:
        if None in article.keywords:
            article.keywords.remove(None)
        keyword = '", "'.join(article.keywords)
    publication_date = article.publication_date
    abstract = article.abstract
    if abstract == '':
      response=requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id='+str(article_id))
      strResponse=response.text #turn byte to json
      abstract=strResponse.split('abstract')[1].split('",')[0]
       
    if abstract is None:
      # continue  # Filtered out articles without abstract
      abstract=""
      sum_abst=""
    else:
      sum_abst=summarize(abstract)
    
    if keyword is None:
        keyword=""
    
    cur_author_ls=[]
    cur_aff_ls=[]     
    for d in article.authors:
        first_name=d.get('firstname')
        last_name=d.get('lastname')
        if first_name is None:
          if last_name is None:
            name='Nan'
          else:
            name=last_name
        else:
          if last_name is None:
            name=first_name
          else:
            name=first_name+' '+ last_name
        aff=d.get('affiliation')
        if aff is None:
          aff='UNKNOWN'
        cur_author_ls.append(name)
        cur_aff_ls.append(aff)
    author_ls.append(cur_author_ls)
    affliation_ls.append(cur_aff_ls)
    

    # Append lists to form a DataFrame
    keywords_ls.append(keyword)
    art_id_ls.append(article_id)
    pub_ls.append(publication_date)
    title_ls.append(title)
    abst_ls.append(abstract)
    summary_ls.append(sum_abst)


d={'Title':title_ls,'Article id':art_id_ls, 'Publication Date':pub_ls, \
   'Authors':author_ls, 'Affliations':affliation_ls, 'One Sentence Summary':summary_ls, 'Abstract':abst_ls}

df=pd.DataFrame(d)


# Try question answering
def PICO(sentence, query_type, qna_prompt):
  if query_type=='Population':
    q="\n\nQ: What is the patient population of focus? Please answer this question in detail.\nA:"
  elif query_type=='Clinical Condition':
    q="\n\nQ: What is the clinical condition or disease of focus in the texts above?\nA:"
  elif query_type=='Intervention':
    q="\n\nQ: Patients were randomrized to receive what treatments\nA:"
  elif query_type=='Patient Outcome':
    q="\n\nQ: What are the patient health outcomes of focus in the texts above?\nA:"
  elif query_type=='Study Outcome':
    q="\n\nQ: What is the study outcome? Please answer the question in detail.\nA:"
  return sentence.query(q, qna_prompt)
# Add a col of literature links 
def add_link(id):
  new_id=id.split('\n')[0]
  return "https://pubmed.ncbi.nlm.nih.gov/{0}/".format(new_id)


query_list=['Population','Clinical Condition','Intervention','Patient Outcome','Study Outcome']
for i in query_list:
  df[str(i)]=df.apply(lambda row: PICO(Conversation(row['Abstract']), i, qna_prompt), axis=1)
df['link']=df.apply(lambda row: add_link(row['Article id']), axis=1) #add article link

df.to_csv('../datasets/cognitive_impair.csv')
