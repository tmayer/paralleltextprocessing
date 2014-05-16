Python Parallel Text Processing
=====

# Tutorial

## 1. Create a generalized search distribution

* import the domain.py module:

```
import domain
```

* construct an object of class *DomainDist* by giving a name for the domain (e.g., "negation") and 
a file where the search terms are listed (e.g., "neg_domain.txt" in the resp. folder):
```
d = domain.DomainDist("negation","../files/neg_domain.txt")
```

* files with search terms have the following structure (elements are separated by TABs):

```
File    marker_type marker  polarity
deu w   nicht   0
eng m   n't 0
```

* have a look at the generalized distribution:

```
print(d)
```

* save the distribution to a tab separated file (".tsv")

```
d.save()
```

* reload a saved distribution in tsv format from a given file

```
d1 = domain.DomainDist("negation","negation_dist.tsv")
```

## 2. Compare a given DomainDist to a Bible text file

* compare it to a given text in ParText format:

```
import reader
text = reader.ParText("fra")
d.compare(text)
```

# Description

## class DomainDist

### Instantiation

An object of class DomainDist is instantiated by giving the domain a meaningful name (argument 
*domain_name*) and a filename where the search terms are provided (argument *filename*). Files with
search terms have the following structure (note that the first line is the header):

```
File    marker_type marker  polarity
deu w   nicht   0
eng w   not 0
```

The first column indicates the text in which the marker has to be searched. The second column 
gives the marker type. Marker types can be w (word forms), m (morphs) or r (regular expressions). 
The third column contains the actual marker (e.g., *nicht* in a German text). The last column is
optional and can contain whether the marker should be present (0 or default) or absent (1) in the 
text. In the latter case, a given verse is only counted if one positive marker is present but none 
of the negative markers (marked with 1). 

As an alternative, a DomainDist object can be created by loading an already established domain
distribution (as generated with the save() method described below). In this case, the filename has
to end with .tsv or .csv. Files of this sort contain three columns for each line (with no header 
line). The first column gives the verse ID, the second column gives the (average) frequency of 
occurrence of the given marker(s) in the verse, the third column gives the (average) weight for 
this verse.

```
40001019	1	0.5
40001020	1	1.0
40001025	1	1.0
```

### Finding the generalized search distribution

The input file potentially contains search terms for different input texts. In this case, all 
markers are first sorted according to texts and then according to whether they are positive or 
negative, with positive markers being search for first. Then each text is treated separately. 

For a given text, first all verses containing positive markers are searched for. For each verse, 
the number of times the marker(s) occur(s) in the text is stored. Finally, those verses containing
negative markers are removed from the list. The weights of the remaining verses are then normalized 
for each text individually by computing the number of different markers in this verse divided by 
the total number of (positive) markers that is given for this text. The frequency of occurrence 
gives the number of tokens of all markers in this verse. 

At the end, the verses are normalized with respect to all texts. For each verse that has been 
detected in at least one text, the weight and the frequency of occurrence of markers is normalized
by taking the average of all values for the individual texts. For the frequency of occurrence the
ceiling of the average value is taken. Note that a text is only taken into consideration in this
step if it contains the actual verse. If the verse does not exist, the text is ignored in this 
step. If the verse exists, but no marker given for that text has been found in the respective verse
a frequency of occurrence of 0 and a weight of 0 contributes to the overall average values across
all texts.

