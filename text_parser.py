import os
os.environ['CLASSPATH'] = "./stanford-parser-4.0.0/"
import sys
import argparse
from nltk.parse.stanford import StanfordParser
from nltk.tree import *
from nltk.stem import WordNetLemmatizer
import nltk

class Parser():
    def __init__(self,sentence):
        self.sentence = sentence

    def parse(self):
        # inputString = input("Enter the String to convert to ISL: ")
        # # java_path = "/usr/bin/java"
        # # os.environ['JAVAHOME'] = java_path
        # for each in range(1,len(sys.argv)):
        #     inputString += sys.argv[each]
        #     inputString += " "
        # print(inputString)

        parser=StanfordParser(model_path='./stanford-parser-4.0.0/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz')

        englishtree=[tree for tree in parser.parse(self.sentence.split())]
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
        words=parsed_sent
        stop_words = {'mustn', 'most', 'weren', 'will', 'll', 'did', "don't", 'the', 'is', 'hasn', 'mightn', 'own', 'doesn', 'wasn', 'other', 'aren', "you'll", 'o', 'should', "didn't", 'theirs', "aren't", 'an', 'was', "shouldn't", "hasn't", "doesn't", "wasn't", "you're", "hadn't", 'doing', "you'd", 'does', 'but', 'both', 'not', 'only', 'don', "couldn't", 'whom', 'haven', 'isn', 'be', 'm', 'y', 'ma', "won't", 'once', "mustn't", 'shan', "you've", 'too', 'because', 'against', 've', "isn't", 'd', 's', 'didn', "it's", "wouldn't", 'nor', 're', 'just', 'such', "should've", 'if', 'needn', 't', 'have', 'off', 'or', 'won', "needn't", 'hadn', 'further', 'shouldn', 'each', 'are', 'had', 'no', 'couldn', "that'll", 'as', 'having', 'while', 'than', "mightn't", 'wouldn', 'a', "haven't", "shan't", "she's", 'into', "weren't", 'very', 'were', 'am', 'and', 'being', 'so', 'has', 'yours', 'for', 'yourselves', 'by', 'ours' , 'been', 'ain'}
        lemmatized_words=[]

        def get_wordnet_pos(treebank_tag):
            if treebank_tag.startswith('J'):
                return 'a'
            elif treebank_tag.startswith('V'):
                return 'v'
                
            elif treebank_tag.startswith('R'):
                return 'r'
            else:
                return 'n'

        lemmatizer = WordNetLemmatizer()

        tag = nltk.pos_tag(words)
        for i in tag:
            if i[0] not in stop_words:
                lemmatized_words.append(lemmatizer.lemmatize(i[0], pos = get_wordnet_pos(i[1])))
        
        islsentence = []
        for w in lemmatized_words:
            if w not in stop_words:
                islsentence.append(w.lower())
        return islsentence

def main(sentence):
    p = Parser(sentence)
    return p
