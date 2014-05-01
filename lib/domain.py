__author__="Thomas Mayer"
__date__="2014-04-29"

import reader
import settings
import collections
from math import sqrt, factorial
import measures

def get_domain_distribution(triggers):
    """
    Parameters:
    ===========
    triggers: list of triggers. Each trigger has four parts:
        1) text: the text where the trigger should be searched for
        2) category: category of the trigger (Word w, Morph m, Regular expression r)
        3) string: the actual string that should be searched for (either a word, character sequence
            or a regular expression
        4) polarity: whether the trigger should ignore (0) the resp. verse or include (1) it 
            in the domain
    """
    
    domain_verses = set()
    
    for text,category,string,polarity in triggers:
        print(text,category,string,polarity)
        t = reader.ParText(text,portions=range(40,67))
        wordforms_by_verses = t.wordforms_verses()
        substrings_by_wordforms = t.substrings_wordforms()
        string = string.lower()
        
        if category.lower() == "w":
            if polarity == 0:
                domain_verses.difference_update(wordforms_by_verses[string])
            else:
                domain_verses.update(wordforms_by_verses[string])
        elif category.lower() == "m":
            string_wordforms = substrings_by_wordforms[string]
            for string_wordform in string_wordforms:
                string_verses = wordforms_by_verses[string_wordform]
                if polarity == 0:
                    domain_verses.difference_update(string_verses)
                else:
                    domain_verses.update(string_verses)
        elif category.lower() == "r":
            pass
        else:
            print("Error!")
            
    domain_dict = {d:1 for d in domain_verses}
            
    return domain_dict
    
def domain_distribution(triggers):
    """
    Parameters:
    ===========
    triggers: list of triggers. Each trigger has four parts:
        1) text: the text where the trigger should be searched for
        2) category: category of the trigger (Word w, Morph m, Regular expression r)
        3) string: the actual string that should be searched for (either a word, character sequence
            or a regular expression
        4) polarity: whether the trigger should ignore (0) the resp. verse or include (1) it 
            in the domain
    """
    
    domain_verses = collections.defaultdict(int)
    
    for text,category,string,polarity in triggers:
        print(text,category,string,polarity)
        t = reader.ParText(text,portions=range(40,67))
        wordforms_by_verses = t.wordforms_verses()
        substrings_by_wordforms = t.substrings_wordforms()
        string = string.lower()
        
        def addtodict(list_of_verses):
            for verse in list_of_verses:
                domain_verses[verse] += 1
        def remfromdict(list_of_verses):
            for verse in list_of_verses:
                del domain_verses[verse]
        
        if category.lower() == "w":
            if polarity == 0:
                remfromdict(wordforms_by_verses[string])
            else:
                addtodict(wordforms_by_verses[string])
        elif category.lower() == "m":
            string_wordforms = substrings_by_wordforms[string]
            for string_wordform in string_wordforms:
                string_verses = wordforms_by_verses[string_wordform]
                if polarity == 0:
                    remfromdict(string_verses)
                else:
                    addtodict(string_verses)
        elif category.lower() == "r":
            pass
        else:
            print("Error!")
            
    domain_dict = {d:(domain_verses[d],1) for d in domain_verses}
            
    return domain_dict
    
class DomainDistComp():

    def __init__(
        self,
        text,
        domain,
        paradigm=0,
        threshold=1,
        slots=1,
        extracted_types="wordforms",
        domain_name = "x"
        ):
        """Compares a given text to a domain (or search) distribution.
        Parameters:
        ===========
        text: the text in ParText format that should be compared
        domain: the domain distribution with which it is to be compared
        """
    
        wordforms_verses2 = text.wordforms_verses()
        verses = text.get_verses()
        self.domain = domain
        self.text = text
        self.domain_name = domain_name
        self.extracted_types = extracted_types
        
        translation = collections.defaultdict(lambda: collections.defaultdict(int))
        
        for verse in domain:
            for word in set(verses[verse]):
                translation[word][verse] += 1
                #translation[word][verse] = domain[verse][0]
          
        self.translation = translation
                
    def extract_marker(
        self,
        method=measures.jaccard
        ):
        
        wordforms = self.translation.keys()
        wordforms_dict = self.text.get_lexicon()
        
        best_candidate = (0,'')
        domain = self.domain
        a = sum([domain[d][1] for d in domain])
        values = dict()
        n = len(self.text)
        
        for wordform in wordforms:
            b = len(wordforms_dict[wordform])
            ab = sum([domain[d][1] * self.translation[wordform][d] for d in domain])
            #ab = sum([self.translation[wordform][d] for d in domain])
            #print(wordform)
            #print(a,b,ab,n)
            currvalue = method(ab,a,b,n)
            #values[wordform] = (a,b,ab,n,currvalue)
            if currvalue > best_candidate[0]:
                best_candidate = (currvalue,wordform)
        
        return best_candidate
        
    def iterative_search(self,method=measures.jaccard,thresh=0.5):
        list_of_markers = list()
        best_cand = self.extract_marker(method=method)
        marker = Marker(self.domain_name,self.text.filename,self.extracted_types,best_cand[1],
            0,0,best_cand[0],1,1)
        list_of_markers.append(marker)
        
        marker_list = MarkerList(self.domain_name,list_of_markers)
        return marker_list
        
class Marker():

    def __init__(self,domain,text,type,form,slot,rank,extraction_value,amplitude,dedication):
        """
        domain: 
        text: name of text where the marker has been extracted
        type: w (word), m (morph), r (regular expression), f (taken from file with distribution)
        form: actual form of the marker
        slot: 
        rank: rank within the slot
        extraction_value: value taken from the association measure
        amplitude: relationship of marker within the domain
        dedication: relationship of marker in the domain in comparison to other uses of the marker
        """
        
        self.domain = domain
        self.text = text
        self.type = type
        self.form = form
        self.slot = slot
        self.rank = rank
        self.extraction_value = extraction_value
        self.amplitude = amplitude
        self.dedication = dedication
        
    def __str__(self):
        
        output_list = [self.domain,self.type,self.form,self.slot,self.rank,self.extraction_value,
            self.amplitude,self.dedication]
        return "{} {} {} {} {} {} {} {}".format(*output_list)
    
    
class MarkerList():

    def __init__(self,domain_name,marker_list):
        self.marker_list = marker_list
        self.domain_name = domain_name

    def plot(self):
        self.domain_name
        for marker in self.marker_list:
            pass
        
    def load(self,filename):
        pass
        
    def save(self,filename):
        pass

    def __str__(self):
        for marker in self.marker_list:
            return str(marker)
            
if __name__ == "__main__":
    
    dv = domain_distribution([("eng","w","not",1)])
    text = reader.ParText("deu",portions=range(40,67))
    d = DomainDistComp(text,dv,domain_name="negation")
    ml = d.iterative_search(method=measures.tscorenormalized)