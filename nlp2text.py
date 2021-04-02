import os
os.environ['CLASSPATH'] = "stanford-parser-4.0.0/"
import sys
import argparse
from nltk.parse.stanford import StanfordParser
from nltk.tag.stanford import StanfordPOSTagger, StanfordNERTagger
from nltk.tokenize.stanford import StanfordTokenizer
from nltk.tree import *
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer

import nltk

inputString = input("Enter the String to convert to ISL: ")
java_path = "/usr/bin/java"
os.environ['JAVAHOME'] = java_path
for each in range(1,len(sys.argv)):
    inputString += sys.argv[each]
    inputString += " "
print(inputString)

parser=StanfordParser(model_path='stanford-parser-4.0.0/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz')

englishtree=[tree for tree in parser.parse(inputString.split())]
parsetree=englishtree[0]
dict={}
# "***********subtrees**********"
parenttree= ParentedTree.convert(parsetree)
for sub in parenttree.subtrees():
    dict[sub.treeposition()]=0
#"----------------------------------------------"
isltree=Tree('ROOT',[])
i=0
for sub in parenttree.subtrees():
    if(sub.label()=="NP" and dict[sub.treeposition()]==0 and dict[sub.parent().treeposition()]==0):
        dict[sub.treeposition()]=1
        isltree.insert(i,sub)
        i=i+1
    if(sub.label()=="VP" or sub.label()=="PRP"):
        for sub2 in sub.subtrees():
            if((sub2.label()=="NP" or sub2.label()=='PRP')and dict[sub2.treeposition()]==0 and dict[sub2.parent().treeposition()]==0):
                dict[sub2.treeposition()]=1
                isltree.insert(i,sub2)
                i=i+1
for sub in parenttree.subtrees():
    for sub2 in sub.subtrees():
        if(len(sub2.leaves())==1 and dict[sub2.treeposition()]==0 and dict[sub2.parent().treeposition()]==0):
            dict[sub2.treeposition()]=1
            isltree.insert(i,sub2)
            i=i+1
parsed_sent=isltree.leaves()
print(parsed_sent)
words=parsed_sent
stop_words = {'mustn', 'most', 'weren', 'will', 'll', 'did', "don't", 'the', 'is', 'hasn', 'mightn', 'own', 'doesn', 'wasn', 'other', 'aren', "you'll", 'o', 'should', "didn't", 'theirs', "aren't", 'an', 'was', "shouldn't", "hasn't", "doesn't", "wasn't", "you're", "hadn't", 'doing', "you'd", 'does', 'but', 'both', 'not', 'only', 'don', "couldn't", 'whom', 'haven', 'isn', 'be', 'm', 'y', 'ma', "won't", 'once', "mustn't", 'shan', "you've", 'too', 'because', 'against', 've', "isn't", 'd', 's', 'didn', "it's", "wouldn't", 'nor', 're', 'just', 'such', "should've", 'if', 'needn', 't', 'have', 'off', 'or', 'won', "needn't", 'hadn', 'further', 'shouldn', 'each', 'are', 'had', 'no', 'couldn', "that'll", 'as', 'having', 'while', 'than', "mightn't", 'wouldn', 'a', "haven't", "shan't", "she's", 'into', "weren't", 'very', 'were', 'am', 'and', 'being', 'so', 'has', 'yours', 'for', 'yourselves', 'by', 'ours' , 'been', 'ain'}
ps = PorterStemmer()
lemmatized_words=[]
from textblob import TextBlob
from textblob import Word
for w in words:
    if w not in stop_words:
        t = Word(w)
        blob_object = TextBlob(w) 
        
        if blob_object.tags[0][1][0] == 'V':
                lemmatized_words.append(t.lemmatize('v'))
        else:
                lemmatized_words.append(t.lemmatize())

islsentence = ""
print(lemmatized_words)
for w in lemmatized_words:
    if w not in stop_words:
        islsentence+=w
        islsentence+=" "
print(islsentence) 
