from math import factorial, log, sqrt

def jaccard(ab,a,b,n,aold=0,maxthres=0):
    return 2*ab/(a+b)
    
def tscore(ab,a,b,n,aold=0,maxthres=0):
    if ab>1: 
        return (ab/n-a/n*b/n)/sqrt(float(1)/n*ab/n)
    else:
        return 0
    
def phi(ab,a,b,n,aold=0,maxthres=0):      
    a1=a-ab
    b1=b-ab
    d=n-ab-a1-ab
    try:
        ph=float(ab*d-a1*b1)/sqrt((ab+a1)*(b1+d)*(ab*b1)*(a1*d))
    except:
        ph=0
    return ph

def tscorenormalized(ab,a,b,n,aold=0,maxthres=0):
    if ab>1: 
        czx=(ab/n-a/n*b/n)/sqrt(1/n*ab/n)
        #v=max(min(max(a,b),aold),maxthres)
        v = a
        czn=(v/n-v/n*v/n)/sqrt(1/n*v/n)
        cz=czx/czn
    else:
        cz=0
    return cz
            
def tscorenormalized2(ab,a,b,n,aold,maxthres):
    gab=b-ab
    gb=n-b
    if ab>1: 
        czx=(ab/n-a/n*b/n)/sqrt(float(1)/n*ab/n)
        try:
            czg=(gab/n-aold/n*gb/n)/sqrt(float(1)/n*gab/n)
        except:
            czg=0
        v=max(min(max(a,b),aold),maxthres)
        czn=(v/n-v/n*v/n)/sqrt(float(1)/n*v/n)
        if czg > 0:
            cz=0 
        else:
            cz=czx/czn
    else:
        cz=0
    return cz
    
def jaccardwae(ab,a,b,n,aold,maxthres):
    ab2=ab-a*b/n
    try:
        czb=(ab/b)**2*log(ab+1,n+a**2)**4
    except:
        czb=0;ab=0;b=1
    try:
        cza=(ab2/a)**2*log(ab+1,n+a**2)**4
    except:
        cza=0;ab=0;b=1
    if cza<0:
        cza=0
    if czb<0:
        czb=0
    cz=max(czb,cza)*max(ab/b,ab2/a)        
    return cz

def loglikelihood(n,k,a,b):
    try:
        k=int(k)
        x = (a * b) / float(n) 
        return (x - k * log(x) + log(factorial(k))) / log(n)
    except:
        return 0.0

def logl(ab,a,b,n,aold,maxthres):
    cz=loglikelihood(n,ab,a,b)
    return cz