__author__="Thomas Mayer"
__date__="2014-04-29"

import reader
import settings
import collections
from math import sqrt, factorial
import measures
from copy import copy
import re
    
class DomainDist():
    """
    A generalized domain distribution where each verse is given a value between 0 an 1 to 
    indicate its relevance with respect to the input search terms. Search terms can be given
    for one or more texts/languages.
    """

    def __init__(self,domain_name,filename):
        """
        Construct a new domain distribution on the basis of search terms in a given TSV file. The
        structure of the file is as follows (separated by TABs):
        
        File    marker_type marker  polarity
        eng w   not 0
        
        Marker types can be w (wordforms), m (morphs) or r (regular expressions). Markers are 
        strings of search terms to look for. Polarity indicates whether the given marker must 
        occur in the verse (marked with 0 or nothing as default) or must not occur in the verse 
        (marked with 1).
        
        :param domain_name: the domain name given to this domain distribution (e.g., negation)
        
        :param filename: the name of the file where the search terms and texts are given. 
        """
        
        # open file and convert input data to a list of InputMarker objects
        fh = open(filename).readlines()
        categories = fh[1].strip().split('\t')
        input_markers = list()
        for line in fh[1:]:
            parameters = line.strip().split('\t')
            polarity = 0
            if len(parameters) == 4: polarity = parameters[3]
            marker = InputMarker(domain_name,parameters[0],parameters[0][:3],parameters[1],
                parameters[2],int(polarity))
            input_markers.append(marker)
            
        # sort markers to make sure that negative markers are listed at the end to delete all
        # verses where they occur
        input_markers.sort(key=lambda x: (x.text,x.polarity))
        self.input_markers = input_markers
        
        # make dictionary with text as key and markers as values
        text_by_markers = collections.defaultdict(list)
        for input_marker in input_markers:
            text_by_markers[input_marker.text].append(input_marker)
        self.text_by_markers = text_by_markers
        
        # convenience functions to add or remove a given list of verses
        def addtodict(list_of_verses,form):
            for verse in list_of_verses:
                domain_verses[verse].add(form)
        def remfromdict(list_of_verses):
            for verse in list_of_verses:
                domain_verses[verse].clear()
                
        domain_verses_texts = dict()
        all_relevant_verses = set()
        
        # go through each text and extract the distribution
        for text in text_by_markers:
            t = reader.ParText(text,portions=range(40,67)) # only NT for the time being
            wordforms_by_verses = t.wordforms_verses()
            substrings_by_wordforms = t.substrings_wordforms()
            
            domain_verses = collections.defaultdict(set)
            markers = list()
            
            # go through each marker in the respective text
            for marker in text_by_markers[text]:
                print(marker)
                string = marker.form
                category = marker.type
                polarity = marker.polarity
                if polarity == 0: markers.append(string) 
                rel_verses = list()
                if category.lower() == "w":
                    rel_verses = wordforms_by_verses[string]
                elif category.lower() == "m":
                    string_wordforms = substrings_by_wordforms[string]
                    for string_wordform in string_wordforms:
                        rel_verses.extend(wordforms_by_verses[string_wordform])
                elif category.lower() == "r":
                    verse_tuples = t.get_verses_strings()
                    regex = re.compile(string)
                    rel_verses = [v[0] for v in verse_tuples for m in [regex.search(v[1])] if m]
                else:
                    print("Error: This marker category does not exist!")
                    
                if polarity == 1:
                    remfromdict(rel_verses)
                else:
                    addtodict(rel_verses,string)
            
            # normalize all extracted verses by the number of markers that are present in the verse
            # in comparison to the overall number of markers for the respective text
            domain_verses_normalized = dict()
            for verse in domain_verses:
                if domain_verses[verse]:
                    markers_in_verse = len(domain_verses[verse])
                    domain_verses_normalized[verse] = markers_in_verse/len(markers)
                    #print(text,verse,markers_in_verse,domain_verses[verse],markers,markers_in_verse/len(markers))
                    
            domain_verses_texts[text] = domain_verses_normalized
            all_relevant_verses.update(domain_verses.keys())
            
        # normalize the individual values over all texts
        # the normalization is in terms of the number of overall number of texts not the 
        # texts that show the respective verse as relevant (marked in the count variable) 
        domain_dist = dict()
        for verse in all_relevant_verses:
            count = 0 
            value = 0
            for t in domain_verses_texts:
                if verse in domain_verses_texts[t]:
                    count += 1
                    value += domain_verses_texts[t][verse]
            if count > 0: domain_dist[verse] = value/len(domain_verses_texts)
            
        self.domain_dist = domain_dist
        #print(domain_dist)
        
    def __str__(self):
        return "\n".join("{} {}".format(d,self.domain_dist[d]) for d in self.domain_dist)
        
    def compare(self,text,method=measures.jaccard,thresh=0.2):
        """
        Compares a given search distribution to the input text.
        
        :param text: filename of the text to be compared with the search distribution
        :type text: ParText object
        :param method: method to be used for the association measure
        """
        
        verses = text.get_verses()
        translation = collections.defaultdict(lambda: collections.defaultdict(int))
        
        wordforms_dict = text.get_lexicon()
        
        for verse in self.domain_dist:
            if verse in verses:
                for word in set(verses[verse]):
                    translation[word][verse] += 1
                    
        wordforms = list(translation.keys())
        current_slot = 0
        list_of_markers = list()
        
        
        def get_best_candidate():
            """
            Auxiliary method to determine the current best candidate.
            """
            
            best_candidate = (0,'')
            a = sum(domain_copy[d] for d in domain_copy)
            a_old = sum(self.domain_dist[d] for d in self.domain_dist)
            n = len(text)
            
            for wordform in wordforms:
                #print(wordform)
                b = len(wordforms_dict[wordform])
                ab = sum(domain_copy[d] * translation[wordform][d] for d in domain_copy)
                
                currvalue = method(ab,a,b,n)
                #print(currvalue)
            
                # check whether the entire domain would be more suitable for the wordform
                entire_value = method(ab,a_old,b,n)
                amplitude = ab/a_old
                dedication = ab/b
                if entire_value > currvalue:
                    continue
                    
                if currvalue >= best_candidate[0]:
                    best_candidate = (currvalue,wordform,amplitude,dedication)
                
            
            wordforms.remove(best_candidate[1])
            return best_candidate
            
            
        while True:
        
            domain_copy = copy(self.domain_dist)
            current_rank = 0
            
            while True:
                if len(wordforms) == 0:
                    break
                    
                best_cand = get_best_candidate()
                if best_cand[0] < thresh:
                    current_slot += 1
                    break
                
                # clean up the rest of the domain to remove marker entries
                marker_to_remove = best_cand[1]
                curr_verses = list(domain_copy.keys())
                for v in curr_verses:
                    nr_occurrences = translation[marker_to_remove][v]
                    occ_in_domain = domain_copy[v]
                    diff = occ_in_domain - nr_occurrences
                    if diff == 0:
                        #del domain_copy[v]
                        translation[marker_to_remove][v] = 0
                    elif diff > 0:
                        #domain_copy[v] = diff
                        translation[marker_to_remove][v] = diff
                    else:
                        print("ERROR: diff smaller than zero")
                        
                print(best_cand)
                
            if current_rank == 0:
                break
                
        
class Marker():

    def __init__(self,domain,text,iso,type,form):
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
        
    def __str__(self):
        
        output_list = [self.domain,self.type,self.form]
        return "{} {} {}".format(*output_list)
        
class InputMarker(Marker):

    def __init__(self,domain,text,iso,type,form,polarity):
        Marker.__init__(self,domain,text,iso,type,form)
        self.polarity = polarity
        
    def __str__(self):
        
        output_list = [self.domain,self.text,self.type,self.form,self.polarity]
        return "{} {} {} {} {}".format(*output_list)
        
class OutputMarker(Marker):

    def __init__(self,domain,text,iso,type,form,slot=0,rank=0,extraction_value=0,amplitude=0,
        dedication=0):
        Marker.__init__(self,domain,text,iso,type,form)
        self.slot = slot
        self.rank = rank
        self.extraction_value = extraction_value
        self.amplitude = amplitude
        self.dedication = dedication
    
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
