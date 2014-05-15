Python Parallel Text Processing
=====

# Tutorial

## 1. Create a generalized search distribution

* import the domain.py module:
    import domain
* construct an object of class *DomainDist* by giving a name for the domain and a file where the
search terms are listed:
    d = domain.DomainDist("negation","../files/neg_domain.txt")
* files with search terms have the following structure (elements are separated by TABs):
    File    marker_type marker  polarity
    deu w   nicht   0
    eng m   n't 0
* have a look at the generalized distribution:
    print(d)
* compare it to a given text in ParText format:
    import reader
    text = reader.ParText("fra")
    d.compare(text)