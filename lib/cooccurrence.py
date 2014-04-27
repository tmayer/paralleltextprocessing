__author__="Thomas Mayer"
__date__="2014-04-22"

import reader
import collections
from scipy.sparse import lil_matrix, csc_matrix, coo_matrix
import numpy as np

def cooccurrence(text1,text2):
    """Counts the frequency of cooccurrence for all wordforms in the two texts.
    Parameter:
    ==========
    text1: first text (dictionary of verse IDs as keys and verse texts as values)
    text2: second text (dictionary of verse IDs as keys and verse texts as values)
    """
    
    translation = collections.defaultdict(lambda: collections.defaultdict(int))
    
    for id,verse1 in text1.verses:
        if id in text2.verses:
            words1 = list({s for s in verse1.split() if s.strip() != ''})
            words2 = list({s for s in text2[id].split() if s.strip() != ''})
            for word1 in words1:
                for word2 in words2:
                    translation[word1][word2] += 1
            
    return translation
    
def matrix_cooccurrence(text1,text2):
    
    matrix1,wordforms1 = text1.get_matrix()
    matrix2,wordforms2 = text2.get_matrix()
    # determining shared verses of both texts
    verseids1 = text1.get_verseids()
    verseids2 = text2.get_verseids()
    common_verseids = list(set(verseids1).intersection(set(verseids2)))
    # building cooccurrence matrix
    cv = np.array(common_verseids)
    m1 = csc_matrix(matrix1,dtype="int16")[:,cv]
    m2 = csc_matrix(matrix2,dtype="int16")[:,cv]
    cooc_matrix = m1 * m2.T
            
    return cooc_matrix,wordforms1,wordforms2
        
            
if __name__ == "__main__":
    print("reading text1...")
    text1 = reader.ParText("../data/deu-x-bible-elberfelder1871-v1.txt")
    print("reading text2...")
    text2 = reader.ParText("../data/eng-x-bible-darby-v1.txt")
    print("counting cooccurrences...")
    #translation = cooccurrence(text1,text2)
    tmatrix,wf1,wf2 = matrix_cooccurrence(text1,text2)