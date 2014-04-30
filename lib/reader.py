__author__="Thomas Mayer"
__date__="2014-04-22"

import collections
import settings
from scipy.sparse import lil_matrix, csc_matrix, coo_matrix
from scipy.io import mmread, mmwrite
import scipy.special
import numpy as np

class ParText():
    """Reads a file in the BibleText format and provides several ways to access the text.
    Parameters:
    =============
    filename: name of the file to be read (first three letters must indicate ISO 639-3 code)
    commentmarker: character that marks a comment line 
    separator: character that separates Bible IDs from the actual text
    enc: encoding of the file (default: UTF-8)
    """
    
    def __init__(
        self,
        filename,
        commentmarker="#",
        sep="\t",
        enc="utf-8"
        ):
        
        self.iso = filename[:3]
        
        # open file
        fh = open(settings._data_dir + filename,'r',encoding=enc).readlines()
        
        # collect all verses    
        self.verses = [(int(items[0].strip()),items[1].strip().lower().split()) for line in fh 
                    for items in [line.split(sep,1)] 
                    if not line.strip().startswith(commentmarker)] 
                    
        self.versedict = {v[0]:v[1] for v in self.verses}
                    
    def __getitem__(self,id):
        """Returns the text of the verse given by the verse id.
        """
        
        return self.versedict[id]
    
    def get_verses(
        self,
        format="dict"
        ):
        """Returns the verses of the parallel text
        Parameters:
        ==============
        format: either as a list of tuples [format='tuple'] (40001001,"bla...bla") 
            or as a dictionary [format='dict'] {400010001: "bla...bla"}
        """
        if format == "tuple":
            return self.verses
        else:
            return dict(self.verses)
            
    def get_lexicon(
        self
        ):
        """Returns the wordforms of the text together with the information in which verses they
        occur. 
        """
        
        lex = collections.defaultdict(set)
        for id,verse in self.verses:
            for word in verse:
                lex[word].add(id)
                
        for l in lex:
            lex[l] = sorted(list(lex[l]))
                
        return lex
            
    def get_wordforms(
        self,
        format="types"
        ):
        """Returns the wordforms (types or tokens) of the parallel text.
        Parameters:
        ===========
        format: either as a dict of types [format='types'] (with frequency as value) 
            or a list of tokens [format='tokens']
        """
        # collect all wordforms (types and tokens)
        self.wordforms = collections.defaultdict(int)
        for id,verse in self.verses:
            for word in verse:
                if word.strip() != '': self.wordforms[word] += 1
           
        
        if format == "tokens":
            return sorted(self.wordforms.keys())
        else:
            return self.wordforms
            
    def wordforms_verses(
        self
        ):
        """Returns a dictionary of wordforms in which verses they occur.
        """
        
        wordforms_by_verses = collections.defaultdict(set)
        
        for id,verse in self.verses:
            for word in verse:
                wordforms_by_verses[word.lower()].add(id)
                
        return wordforms_by_verses
        
    def substrings_wordforms(
        self
        ):
        """Returns a dictionary of substrings in which wordforms they occur.
        """
        
        substrings_by_wordforms = collections.defaultdict(set)
        wordforms = self.get_wordforms()
        
        for word in wordforms:
            word = word.lower()
            for i in range(len(word)+1):
                for j in range(i+1,len(word)+1):
                    substrings_by_wordforms[word[i:j]].add(word)
                    
        return substrings_by_wordforms
            
    def get_verseids(
        self
        ):
        """Returns the verse Ids for this parallel text."""
        
        return sorted([v[0] for v in self.verses])
        
    def get_matrix(
        self
        ):
        """Returns a sparse matrix with verse IDs as row names and words as column names where
        each cell indicates how many times the word occurs in the respective verse."""

        wordforms = self.get_wordforms(format="tokens")
        
        rowdata = list()
        coldata = list()
        data = list()
        wordforms_by_number = {w: i for i,w in enumerate(wordforms)}
        wfcounter = 0
        for id,verse in self.verses:
            for word in verse:
                #words_by_verses[word].append(id)
                rowdata.append(wordforms_by_number[word])
                coldata.append(id)
                data.append(1)
                
        sparse = coo_matrix((data,(rowdata,coldata)),dtype="int8",shape=(len(wordforms),99999999))

        return sparse,wordforms_by_number
        
        
            
if __name__ == "__main__":
    
    text = ParText("../data/deu-x-bible-elberfelder1871-v1.txt")
    lexicon = text.get_lexicon()
    
    """
    text1 = ParText("deu-x-bible-elberfelder1871-v1.txt")
    matrix1,wordforms1 = text1.get_matrix()
    print("and again...")
    text2 = ParText("eng-x-bible-darby-v1.txt")
    matrix2,wordforms2 = text2.get_matrix()
    print("collecting common verses...")
    verseids1 = text1.get_verseids()
    verseids2 = text2.get_verseids()
    print("what is common?")
    common_verseids = list(set(verseids1).intersection(set(verseids2)))
    print("building csc matrices")
    cv = np.array(common_verseids)
    m1 = csc_matrix(matrix1,dtype="int16")[:,cv]
    m2 = csc_matrix(matrix2,dtype="int16")[:,cv]
    matrix_obs = m1 * m2.T
    vector1 = matrix1.sum(1)
    vector2 = matrix2.sum(1)
    matrix_exp = np.outer(vector1,vector2) / len(common_verseids)
    """
    

    
    