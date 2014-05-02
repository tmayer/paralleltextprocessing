__author__="Thomas Mayer"
__date__="2014-04-29"

import reader
import settings
import collections
from math import sqrt, factorial
import measures
from copy import copy

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
    
class DomainDist():

    def __init__(self,domain_name,filename):
        
        fh = open(filename).readlines()
        categories = fh[1].strip().split('\t')
        input_markers = list()
        for line in fh[1:]:
            parameters = line.strip().split('\t')
            polarity = '0'
            if len(parameters) == 4: polarity = parameters[3]
            marker = InputMarker(domain_name,parameters[0],parameters[0][:3],parameters[1],
                parameters[2],polarity)
            #text,iso,type,form,
            input_markers.append(marker)
            
        # sort markers
        input_markers.sort(key=lambda x: (x.text,x.polarity))
        
    
class DomainDistComp():

    def __init__(
        self,
        text,
        domain,
        paradigm=0,
        threshold=1,
        slots=1,
        extracted_types="w",
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
            if verse in verses:
                for word in set(verses[verse]):
                    translation[word][verse] += 1
                    #translation[word][verse] = domain[verse][0]
          
        self.translation = translation
                
    def extract_marker(
        self,
        method=measures.jaccard
        ):
        
        
        best_candidate = (0,'')
        domain = self.copied_domain
        a = sum([domain[d][1] for d in domain])
        a_old = sum([self.domain[d][1] for d in self.domain])
        values = dict()
        n = len(self.text)
        
        for wordform in self.wordforms:
        
            b = len(self.wordforms_dict[wordform])
            ab = sum([domain[d][1] * self.translation[wordform][d] for d in domain])
            
                
            
            currvalue = method(ab,a,b,n)
            
            # check whether the entire domain would be more suitable for the wordform
            entire_value = method(ab,a_old,b,n)
            amplitude = ab/a_old
            dedication = ab/b
            if entire_value > currvalue:
                continue
            
            if currvalue >= best_candidate[0]:
                best_candidate = (currvalue,wordform,type,amplitude,dedication)
                
        self.extracted_markers.append((best_candidate[1],best_candidate[2]))
        print(best_candidate)
        
        self.wordforms.remove(best_candidate[1])
        
        
        return best_candidate
        
    def iterative_search(self,method=measures.jaccard,thresh=0.2):
        # define variables for iteration
        list_of_markers = list()
        
        #self.substrings_by_wordforms = substrings_to_wordforms(self.translation.keys())
        
        self.wordforms = list(self.translation.keys())
        self.wordforms_dict = self.text.get_lexicon()
        self.copied_translation = copy(self.translation)
        self.extracted_markers = list()
        self.current_slot = 0
        
        # iteration part
        while True:
            self.copied_domain = copy(self.domain)
            self.current_rank = 0
        
            while True:
                #print(self.wordforms)
                if len(self.wordforms) == 0:
                    break
                best_cand = self.extract_marker(method=method)
                if best_cand[0] < thresh:
                    self.current_slot += 1
                    break
                
                #print(best_cand)
                
                # clean up the rest domain to remove marker entries
                marker_to_remove = best_cand[1]
                curr_verses = list(self.copied_domain.keys())
                for d in curr_verses:
                    number_occurrences = self.copied_translation[marker_to_remove][d]
                    occurrences_in_domain = self.copied_domain[d][0]
                    diff = occurrences_in_domain - number_occurrences
                    if diff == 0:
                        del self.copied_domain[d]
                    elif diff > 0:
                        self.copied_domain[d] = (diff,1)
                    else:
                        del self.copied_domain[d]
                        #print("Error: diff smaller than zero!")
                    
                
                marker = Marker(self.domain_name,self.text.filename,self.text.iso,self.extracted_types,
                    best_cand[1],self.current_slot,self.current_rank,best_cand[0],best_cand[3],best_cand[4])
                self.current_rank += 1
                list_of_markers.append(marker)
                
            if self.current_rank == 0:
                break
        
        # return
        marker_list = MarkerList(self.domain_name,list_of_markers,self.text.iso)
        return marker_list
        
class Marker():

    def __init__(self,domain,text,iso,type,form,slot=0,rank=0,extraction_value=0,amplitude=0,
        dedication=0):
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
        self.iso = iso
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
        
class InputMarker(Marker):

    def __init__(self,domain,text,iso,type,form,polarity):
        self.domain = domain
        self.text = text
        self.iso = iso
        self.type = type
        self.form = form
        self.polarity = polarity
    
    
class MarkerList():

    def __init__(self,domain_name,marker_list,iso):
        self.marker_list = marker_list
        self.domain_name = domain_name
        self.iso = iso

    def plot(self):
        self.domain_name
        marker_list = sorted(self.marker_list,key=lambda x: (x.slot,x.rank))
        
        numberofslotsvis=4
        morphcolor="yellow"
        wordfcolor="green"
        slot=0
        ing=0
        
        rtx="si=3\n"
        rtx+="par=0;\n"
        rtx+='plot(c(0,'+str(numberofslotsvis)+'),c(0,1),col="white",main="'+self.domain_name+' - '+self.iso+'",xlab="",ylab="")\n'
        
        for marker in marker_list:
            try:
                #i=j[1]
                ing=marker.dedication
                ed=marker.amplitude
                rtx+='slot='+str(marker.slot)+';'
                if marker.rank == 0:
                    rtx+='par=0\n'
                if marker.type=="m":
                    plotcolor=morphcolor
                elif marker.type=="w":
                    plotcolor=wordfcolor
                rtx+='ing='+str(ing)+';ingg='+str(max(ing,0.3))+';ed='+str(ed)+';edd='+str(max(ed,0.3))+';str="'+marker.form+'"\n'
                rtx+='rect(slot,par,slot+ing,par+ed,col=\''+plotcolor+'\')\n'
                rtx+='text(slot+ing/2,par+ed/2,str,cex=si*edd)\n'
                rtx+='par=par+ed\n'
            except:
                pass
                
        return rtx
        
    def load(self,filename):
        pass
        
    def save(self,filename):
        pass

    def __str__(self):
        output_lines = list()
        for marker in self.marker_list:
            output_list = [marker.domain,marker.type,marker.form,marker.slot,marker.rank,
            marker.extraction_value,
            marker.amplitude,marker.dedication]
            output_lines.append("{:<20} {:<5} {:<20} {:>2} {:>2} {:<25} {:>2} {:>2}".format(*output_list))
        return "\n".join(output_lines)
            
def substrings_to_wordforms(wordforms):
    """Returns a dictionary of 
    """
    
    substrings_by_wordforms = collections.defaultdict(set)
    
    for word in wordforms:
        orig_word = word.lower()
        word = "#" + orig_word + "#"
        for i in range(len(word)+1):
            for j in range(i+1,len(word)+1):
                substrings_by_wordforms[word[i:j]].add(orig_word)
                
    return substrings_by_wordforms
        
            
if __name__ == "__main__":
    
    #dv = domain_distribution([("eng","w","went",1)])
    #text = reader.ParText("deu",portions=range(40,67))
    #d = DomainDistComp(text,dv,domain_name="negation")
    #ml = d.iterative_search(method=measures.jaccard,thresh=0.2)
    d = DomainDist("negation","../files/neg_domain.txt")
