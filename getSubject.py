"""
Function to pull a subject out of a message using some REs and chunking.
"""

import re, nltk, string

from nltk.corpus import brown
from nltk.chunk import RegexpParser

punct = '!"#$%&*+,-./:;<=>?@[\]^_`{|}~' + "'"

# over-sensitive
npGrammar = r"""
      NP: {(<NP>|<NPS>|<NN>|<NNS>)+} 
    """
    
# some things that sometimes get caught which shouldn't
bad = ['Have', 'Who', 'He', '', 'Him', 'You', 'She' 'I', 'Her', 'Them', 'They', 'Your', 'My', 'Me', 'Oh', 'We', 'Us']
# some things that get caught ALONG WITH good things
trim = ['Is', 'is', 'Hi', 'hi', 'Hello', 'hello']

def getPOSTagger():
    # lazy init
    if not hasattr(getPOSTagger, 'tagger'):
        brown_tagged_sents = brown.tagged_sents(categories='news',simplify_tags=True)
        t0 = nltk.DefaultTagger('NN')
        t1 = nltk.UnigramTagger(brown_tagged_sents, backoff=t0)
        getPOSTagger.tagger = nltk.BigramTagger(brown_tagged_sents, backoff=t1)
    return getPOSTagger.tagger

def getChunker():
    # lazy init
    if not hasattr(getChunker, 'chunker'):
        getChunker.chunker = RegexpParser(npGrammar)
    return getChunker.chunker

def chunkMsg(msg):
    tagger = getPOSTagger()
    sents = nltk.sent_tokenize(msg)
    words = [sent.split() for sent in sents]
    tagged = map(tagger.tag, words)
    chunker = getChunker()
    chunks = map(chunker.parse, tagged)
    return chunks

def cleanSubject(subject):
    s = subject.strip()
    s = s.replace("'s",'')
    s = re.sub('\s+', ' ', s)
    s = string.capwords(s)
    for c in punct:
        s = s.replace(c, '')
    return s

def getSubjects(msg):
    chunkses = chunkMsg(msg)
    subjects = []
    for chunks in chunkses:
        for chunk in chunks:
            if hasattr(chunk, 'node') and chunk.node == 'NP':
                subject = cleanSubject(' '.join([w for (w,t) in chunk if w not in trim]))
                if (subject not in bad):
                    subjects.append(subject)
    return subjects
    
def main():
    msg = raw_input()
    resp = getSubjects(msg)
    print 'Response:'
    print resp
    
if __name__ == "__main__":
    main()
