from __future__ import unicode_literals
from __future__ import division

from hazm import *
import pickle
import os.path
import re, os
import operator



class BagOfWords(object):

    def __init__(self):
        self.__number_of_words = 0
        self.__bag_of_words = {}

    def __add__(self, other):
        erg = BagOfWords()
        sum = erg.__bag_of_words
        for key in self.__bag_of_words:
            sum[key] = self.__bag_of_words[key]
            if key in other.__bag_of_words:
                sum[key] += other.__bag_of_words[key]
        for key in other.__bag_of_words:
            if key not in sum:
                sum[key] = other.__bag_of_words[key]
        return erg

    def add_word(self, word):
        self.__number_of_words += 1
        if word in self.__bag_of_words:
            self.__bag_of_words[word] += 1
        else:
            self.__bag_of_words[word] = 1

    def len(self):
        return len(self.__bag_of_words)

    def Words(self):
        """ Returning a list of the words contained in the object """
        return self.__bag_of_words.keys()

    def BagOfWords(self):
        """ Returning the dictionary, containing the words (keys) with their frequency (values)"""
        return self.__bag_of_words

    def WordFreq(self, word):
        """ Returning the frequency of a word """
        if word in self.__bag_of_words:
            return self.__bag_of_words[word]
        else:
            return 0


class Document(object):
    """ Used both for learning (training) documents and for testing documents. The optional parameter lear
    has to be set to True, if a classificator should be trained. If it is a test document learn has to be set to False. """
    _vocabulary = BagOfWords()

    def __init__(self, vocabulary):
        self.__document_class = None
        self._words_and_freq = BagOfWords()
        Document._vocabulary = vocabulary

    def read_document(self, tokenized_words, learn=False):#file_name -> tokenized_words
        words = tokenized_words.arrayOfWords
        self._number_of_words = 0
        for word in words:
            self._words_and_freq.add_word(word)
            if learn:
                Document._vocabulary.add_word(word)

    def __add__(self, other):#self: 1st doc - other: 2nd doc
        """ Overloading the "+" operator. Adding two documents consists in adding the BagOfWords of the Documents """
        res = Document(Document._vocabulary)
        res._words_and_freq = self._words_and_freq + other._words_and_freq
        return res

    def vocabulary_length(self):
        """ Returning the length of the vocabulary """
        return len(Document._vocabulary)

    def WordsAndFreq(self):
        """ Returning the dictionary, containing the words (keys) with their frequency (values) as contained
        in the BagOfWords attribute of the document"""
        return self._words_and_freq.BagOfWords()

    def Words(self):
        """ Returning the words of the Document object """
        d = self._words_and_freq.BagOfWords()
        return d.keys()

    def WordFreq(self, word):
        """ Returning the number of times the word "word" appeared in the document """
        bow = self._words_and_freq.BagOfWords()
        if word in bow:
            return bow[word]
        else:
            return 0

    def __and__(self, other):
        """ Intersection of two documents. A list of words occuring in both documents is returned """
        intersection = []
        words1 = self.Words()
        for word in other.Words():
            if word in words1:
                intersection += [word]
        return intersection


class DocumentClass(Document):
    def __init__(self, vocabulary):
        Document.__init__(self, vocabulary)
        self._number_of_docs = 0

    def Probability(self, word):
        """ returns the probabilty of the word "word" given the class "self" """
        voc_len = Document._vocabulary.len()
        SumN = 0
        for i in range(voc_len):
            SumN = DocumentClass._vocabulary.WordFreq(word)
        N = self._words_and_freq.WordFreq(word)
        erg = 1 + N
        erg /= voc_len + SumN
        return erg

    def __add__(self, other):
        """ Overloading the "+" operator. Adding two DocumentClass objects consists in adding the
        BagOfWords of the DocumentClass objectss """
        res = DocumentClass(self._vocabulary)
        res._words_and_freq = self._words_and_freq + other._words_and_freq

        return res

    def SetNumberOfDocs(self, number):
        self._number_of_docs = number

    def NumberOfDocuments(self):
        return self._number_of_docs


class Pool(object):
    def __init__(self):
        self.__document_classes = {}
        self.__vocabulary = BagOfWords()

    def sum_words_in_class(self, dclass_num):
        """ The number of times all different words of a dclass_num appear in a class """
        sum = 0
        for word in self.__vocabulary.Words():
            WaF = self.__document_classes[dclass_num].WordsAndFreq()
            if word in WaF:
                sum += WaF[word]
        return sum

    def learn(self, list_of_tokenized_words, dclass_num):#directory -> list_of_tokenizded_files - dclass_num : key ###CRITICAL
        """ directory is a path, where the files of the class with the name dclass_name can be found """
        x = DocumentClass(self.__vocabulary)
        for each in list_of_tokenized_words:
            d = Document(self.__vocabulary)
            d.read_document(each, learn=True)
            x = x + d
        self.__document_classes[dclass_num] = x
        x.SetNumberOfDocs(len(list_of_tokenized_words))

    def Probability(self, doc, dclass_num=None):
        """Calculates the probability for a class dclass_num given a document doc"""
        if dclass_num:
            sum_dclass = self.sum_words_in_class(dclass_num)
            prob = 0

            d = Document(self.__vocabulary)
            d.read_document(doc)

            for j in self.__document_classes:
                sum_j = self.sum_words_in_class(j)
                prod = 1
                for i in d.Words():
                    wf_dclass = 1 + self.__document_classes[dclass_num].WordFreq(i)
                    wf = 1 + self.__document_classes[j].WordFreq(i)
                    r = wf * sum_dclass / (wf_dclass * sum_j)
                    prod *= r
                prob += prod * self.__document_classes[j].NumberOfDocuments() / self.__document_classes[
                    dclass_num].NumberOfDocuments()
            if prob != 0:
                return 1 / prob
            else:
                return -1
        else:
            prob_list = []
            for dclass_num in self.__document_classes:
                prob = self.Probability(doc, dclass_num)
                prob_list.append([dclass_num, prob])
            prob_list.sort(key=lambda x: x[1], reverse=True)
            return prob_list

    def DocumentIntersectionWithClasses(self, doc_name):
        res = [doc_name]
        for dc in self.__document_classes:
            d = Document(self.__vocabulary)
            d.read_document(doc_name, learn=False)
            o = self.__document_classes[dc] & d
            intersection_ratio = len(o) / len(d.Words())
            res += (dc, intersection_ratio)
        return res


class wholeData():
    def __init__(self):
        self.DictionaryOfLabels = {}#consists of 9 keys [labels]

class tokenizedLine():
    def __init__(self,ClassNum, tokenizedArrayOfWords):
        self.arrayOfWords = tokenizedArrayOfWords
        self.classNum = ClassNum



numberOfCases = 50000
numberOfCasesForBuild = 250
numberOfCasesForTest = 5
gapBetweenTwoGroups = 8000
normalizer = Normalizer()
#lemmetizer = Lemmatizer()
whole_data = wholeData()
counter =0

inpuut = "Q"
while inpuut.lower() != "e":
    inpuut = input("read from 's.d' OR start from train data \n"
                   "and train.content OR end ?\n r : read | s : start | e : end\n")
    if(inpuut.lower()=='s' or inpuut.lower()=='r'):
        if inpuut.lower()=='s':
            content_reader = open('train.content','r',encoding='utf-8')
            label_reader = open('train.label','r',encoding='utf-8')
            for i in range(9):
                for j in range(numberOfCasesForBuild):
                    content_line = normalizer.normalize(content_reader.readline())
                    label_num = int(label_reader.readline())  # ClassNum
                    #print(label_num)
                    arrayOfWords = []
                    arrayOfSentences = sent_tokenize(content_line)
                    for each in arrayOfSentences:
                        arrayOfWords += word_tokenize(each)
                    sentence = tokenizedLine(label_num, arrayOfWords)
                    if not(label_num in whole_data.DictionaryOfLabels):
                        whole_data.DictionaryOfLabels[label_num] = []
                        whole_data.DictionaryOfLabels[label_num].append(sentence)
                    else:
                        whole_data.DictionaryOfLabels[label_num].append(sentence)
                    #counter = counter  +1

                for k in range(gapBetweenTwoGroups - numberOfCasesForBuild):
                    content_reader.readline()
                    label_reader.readline()

                '''
                content_line = normalizer.normalize(content_reader.readline())
                label_num = int(label_reader.readline())#ClassNum
                arrayOfWords = []
                arrayOfSentences = sent_tokenize(content_line)
                for each in arrayOfSentences:
                   arrayOfWords += word_tokenize(each)
                sentence = tokenizedLine(label_num,arrayOfWords)
                whole_data.DictionaryOfLabels.append(sentence)
                '''

            inpuut1 = input("do you want to save your scanned data "
                            "for later searches?\n y: yes | <other input> : no\n")
            if inpuut1.lower() == "y" or inpuut1.lower()== "yes":
                writer = open("s.d", "wb")
                pickle.dump(whole_data, writer)
            else:
                a = 0
        elif inpuut.lower() == 'r':
            if os.path.isfile("s.d")== False:
                print(">there is no file to load from. build it first with 'start'.")
            else:
                print(">reading file from s.d")
                reader = open("s.d","rb")
                whole_data = pickle.load(reader)
        #we have data , now we learn from database:

        print(">learning the basic data")

        labels = [1,2,3,5,8,10,11,13,16] #keys :)
        pool = Pool()
        for each in labels:
            pool.learn(whole_data.DictionaryOfLabels[each], each)
        #now that we have learned database, we give the test
        inpuut2 = 'Q'
        while inpuut2 != "e":
            inpuut2 = input("type the name of file containing tests OR type E to exit:")
            if inpuut2.lower() != "e":
                #reader = open(inpuut2, "r",encoding='utf-8')
                with open(inpuut2, "r",encoding='utf-8') as ins:
                    writer = open(inpuut2 + ".guessedlabels",'w')
                    lines = []
                    i =1
                    for line in ins:
                        lines.append(line)
                    for line in lines:
                        content_line = normalizer.normalize(line)
                        arrayOfWords1 = []
                        arrayOfSentences = sent_tokenize(content_line)
                        for each in arrayOfSentences:
                            arrayOfWords1 += word_tokenize(each)
                        sentence = tokenizedLine(None, arrayOfWords1)
                        results = pool.Probability(sentence)
                        #max_label=max(results.iteritems(), key=operator.itemgetter(1))[0]
                        writer.write(str(results[0][0]) + "\n")
                        print("test #"  + str(i) + ":\n"
                              + " > (label | probability) : (" +  str(results[0][0]) + " | " + str(results[0][1]) + ")\n")
                        i = i +1


    elif inpuut.lower() == 'e':
        a=0#n
    else:
        print(">wrong input! try again!")
    #read from file
    #arrayOfWords = word_tokenize(content_line)

#print(counter)
#print(len(whole_data.ArrayOfLines))
#for keys in whole_data.DictionaryOfLabels:
#    print(keys)
    #print(whole_data.DictionaryOfLabels[keys])