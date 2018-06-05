from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

#---------- MODEL IN MEMORY ----------------#
# create your own connection, use '\list' in psql to find the name and owner of the database
# cnx = create_engine('postgresql://yichiang:yichiang@52.206.3.40:5432/adtracking')

import os
import pandas as pd
import numpy as np
import pickle
from collections import Counter, defaultdict
import re

# import sklearn models
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from skmultilearn.problem_transform import LabelPowerset

# nlp libraries/api
import en_core_web_lg
from spacy import displacy
import gensim
from neuralcoref import Coref

spacy = en_core_web_lg.load()
coref = Coref(nlp=spacy)

# Load opinion lexicon
neg_file = open("../neg_words.txt",encoding = "ISO-8859-1")
pos_file = open("../pos_words.txt",encoding = "ISO-8859-1")
neg = [line.strip() for line in neg_file.readlines()]
pos = [line.strip() for line in pos_file.readlines()]
opinion_words = neg + pos

# Setup nltk corpora path and Google Word2Vec location
# google_vec_file = 'GoogleNews-vectors-negative300.bin'
# word2vec = gensim.models.KeyedVectors.load_word2vec_format(google_vec_file, binary=True)
# pickle.dump(word2vec, open("word2vec_google.pkl", 'wb'))
word2vec = pickle.load(open("../word2vec_google.pkl", 'rb'))

# load the Multi-label binarizer
mlb = pickle.load(open("../mlb.pkl", 'rb'))

# load the fitted naive bayes model
naive_model1 = pickle.load(open("../naive_model1.pkl", 'rb'))

def check_similarity(aspects, word):
    similarity = []
    for aspect in aspects:
        similarity.append(word2vec.n_similarity([aspect], [word]))
    # set threshold for max value
    if max(similarity) > 0.30:
        return aspects[np.argmax(similarity)]
    else:
        return None

# def aspect_pos_neg(aspect_sent, key, sent_dict):
#     '''
#     function: append pos or negative sentiment to aspect_sent dictionary
#     '''
#     if sent_dict[key] > 0:
#         aspect_sent[key]["pos"] += sent_dict[key]
#     else:
#         aspect_sent[key]["neg"] += abs(sent_dict[key])
#     return aspect_sent

def assign_term_to_aspect(aspect_sent, terms_dict, sent_dict, pred):
    '''
    function: takes in a sentiment dictionary and appends the aspect dictionary
    inputs: sent_dict is a Counter in the form Counter(term:sentiment value)
            aspect_sent is total sentiment tally
            terms_dict is dict with individual aspect words associated with sentiment
    output: return two types of aspect dictionaries: 
            updated terms_dict and aspect_sent
    '''
    aspects = ['ambience', 'food', 'price', 'service']
    
    
    
    # First, check word2vec
    # Note: the .split() is used for the term because word2vec can't pass compound nouns
    for term in sent_dict:
        try:
            # The conditions for when to use the NB classifier as default vs word2vec
            if check_similarity(aspects, term.split()[-1]):
                terms_dict[check_similarity(aspects, term.split()[-1])][term] += sent_dict[term]
                if sent_dict[term] > 0:
                    aspect_sent[check_similarity(aspects, term.split()[-1])]["pos"] += sent_dict[term]
                else:
                    aspect_sent[check_similarity(aspects, term.split()[-1])]["neg"] += abs(sent_dict[term])
            elif (pred[0] == "anecdotes/miscellaneous"):
                continue
            elif (len(pred) == 1):
                terms_dict[pred[0]][term] += sent_dict[term]
                if sent_dict[term] > 0:
                    aspect_sent[pred[0]]["pos"] += sent_dict[term]
                else:
                    aspect_sent[pred[0]]["neg"] += abs(sent_dict[term])
            # if unable to classify via NB or word2vec, then put them in misc. bucket
            else:
                terms_dict["misc"][term] += sent_dict[term]
                if sent_dict[term] > 0:
                    aspect_sent["misc"]["pos"] += sent_dict[term]
                else:
                    aspect_sent["misc"]["neg"] += abs(sent_dict[term])
        except:
            print(term, "not in vocab")
            continue
    return aspect_sent, terms_dict
    
    
def feature_sentiment(sentence):
    '''
    input: dictionary and sentence
    function: appends dictionary with new features if the feature did not exist previously,
              then updates sentiment to each of the new or existing features
    output: updated dictionary
    '''

    sent_dict = Counter()
    sentence = spacy(sentence)
    
    for token in sentence:
    #    print(token.text,token.dep_, token.head, token.head.dep_)
        #check if the word is an opinion word, then assign sentiment
        if token.text in opinion_words:
            sentiment = 1 if token.text in pos else -1
            # if target is an adverb modifier (i.e. pretty, highly, etc.)
            # but happens to be an opinion word, ignore and pass
            if (token.dep_ == "advmod"):
                continue
            elif (token.dep_ == "amod"):
                sent_dict[token.head.text] += sentiment
            # for opinion words that are adjectives, adverbs, verbs...
            for child in token.children:
                # if there's a adj modifier (i.e. very, pretty, etc.) add more weight to sentiment
                # This could be better updated for modifiers that either positively or negatively emphasize
                if ((child.dep_ == "amod") or (child.dep_ == "advmod")) and (child.text in opinion_words):
                    sentiment *= 1.5
                # check for negation words and flip the sign of sentiment
                if child.dep_ == "neg":
                    sentiment *= -1
                # if verb, check if there's a direct object
                if (token.pos_ == "VERB") & (child.dep_ == "dobj"):                        
                    sent_dict[child.text] += sentiment
                    # check for conjugates (a AND b), then add both to dictionary
                    subchildren = []
                    conj = 0
                    for subchild in child.children:
                        if subchild.text == "and":
                            conj=1
                        if (conj == 1) and (subchild.text != "and"):
                            subchildren.append(subchild.text)
                            conj = 0
                    for subchild in subchildren:
                        sent_dict[subchild] += sentiment

            # check token head and go to noun
            for child in token.head.children:
                # if the verb is referring to a noun, 
                noun = ""
                if child.pos_ == "NOUN":
                    noun = child.text

                    # Check for compound nouns
                    for subchild in child.children:
                        if subchild.dep_ == "compound":
                            noun = subchild.text + " " + noun
                    sent_dict[noun] += sentiment
    return sent_dict

def classify_and_sent(sentence, aspect_sent, terms_dict):
    '''
    function: classify the sentence into a category, and assign sentiment
    note: aspect_dict is a parent dictionary with all the aspects
    input: sentence & aspect dictionary, which is going to be updated
    output: updated aspect dictionary
    '''
    # classify sentence with NB classifier
    predicted = naive_model1.predict([sentence])
    pred = mlb.inverse_transform(predicted)
    
    # get aspect names and their sentiment in a dictionary form
    sent_dict = feature_sentiment(sentence)
    
    # try to categorize the aspect names into the 4 aspects in aspect_dict
    aspect_sent, terms_dict = assign_term_to_aspect(aspect_sent, terms_dict, sent_dict, pred[0])
    return aspect_sent, terms_dict

def replace_pronouns(text):
    coref.one_shot_coref(text)
    return coref.get_resolved_utterances()[0]

def split_sentence(text):
    '''
    splits review into a list of sentences using spacy's sentence parser
    '''
    review = spacy(text)
    bag_sentence = []
    start = 0
    for token in review:
        if token.sent_start:
            bag_sentence.append(review[start:(token.i-1)])
            start = token.i
        if token.i == len(review)-1:
            bag_sentence.append(review[start:(token.i+1)])
    return bag_sentence

def remove_special_char(sentence):
    return re.sub(r"[^a-zA-Z0-9.',:;?]+", ' ', sentence)

def review_pipe(review, aspect_sent, terms_dict={'ambience':Counter(), 'food':Counter(), 'price':Counter(), 'service':Counter(),'misc':Counter()}):
    review = replace_pronouns(review)
    sentences = split_sentence(review)
    for sentence in sentences:
        sentence = remove_special_char(str(sentence))
        aspect_sent, terms_dict = classify_and_sent(sentence.lower(), aspect_sent, terms_dict)
    return aspect_sent, terms_dict

# initialize dictionaries
terms_dict={'ambience':Counter(), 'food':Counter(), 'price':Counter(), 'service':Counter(),'misc':Counter()}
aspect_sent={'ambience':Counter(), 'food':Counter(), 'price':Counter(), 'service':Counter(),'misc':Counter()}



@app.route("/")
def viz_page():
    """
    Homepage: serve our visualization page, awesome.html
    """
    with open("AspectMiningWeb.html", 'r') as viz_file:
        return viz_file.read()


@app.route("/process", methods=["POST"])
def prob():
    """
    When A POST request with json data is made to this uri,
    Read the example from the json, predict probability and
    send it with a response
    """
    # Get decision score for our example that came with the request
    data = request.json
    sentence = data["sentence"]
    aspect_sent, terms_dict = review_pipe(sentence, aspect_sent, terms_dict)
    
    
    return jsonify(sentence)