__author__="Thomas Mayer"
__date__="2014-04-29"

import reader
import settings
import collections
from math import sqrt

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
        t = reader.ParText(text)
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
    
class Domain_distribution_comparison():

    def __init__(
        self,
        text,
        domain,
        paradigm=0,
        threshold=1,
        slots=1,
        extracted_types="wordforms"
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
        
        translation = collections.defaultdict(lambda: collections.defaultdict(int))
        
        for verse in domain:
            for word in verses[verse]:
                translation[word][verse] += 1
          
        self.translation = translation
        
    def jaccard(
        ab,
        a,
        b,
        n
        ):
        return 2*ab/(a+b)
        
    def dice(
        ab,
        a,
        b,
        n
        ):
        return ab
                
    def get_distances(
        self,
        method=jaccard
        ):
        
        wordforms = self.translation.keys()
        wordforms_dict = self.text.get_wordforms()
        
        best_candidate = (0,'')
        domain = self.domain
        a = sum([domain[d] for d in domain])
        values = dict()
        
        for wordform in wordforms:
            b = wordforms_dict[wordform]
            ab = sum([domain[d] * self.translation[wordform][d] for d in domain])
            n = len(self.text)
            #print(wordform)
            #print(a,b,ab,n)
            currvalue = 2*ab/(a+b)
            values[wordform] = (a,b,ab,n,currvalue)
            if currvalue > best_candidate[0]:
                best_candidate = (currvalue,wordform)
        
        return best_candidate, values
        

        
            
if __name__ == "__main__":
    
    dv = get_domain_distribution([("eng","m","n't",1),
        ("eng","w","not",1)
        ])
    text = reader.ParText("deu")
    d = Domain_distribution_comparison(text,dv)
    cand, values = d.get_distances()