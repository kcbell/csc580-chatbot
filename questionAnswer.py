"""
The function to process a message received from a user when that message
isn't a command. Tries to match the string to determine what the user is asking
about and then responds with information from Wikipedia.
"""

import re, nltk, string

from getBirthday import getBirthday
from getSubjectInfo import getSubjectInfo

# some pre-defined forms of subject queries
subjectQueries = [
                  '.*about\s+(?:a\s+|the\s+)?(.+)',
                  '.*what\s+(?:is|was)\s+(?:a\s+|the\s+)?(.+)',
                  '.*who\s+(?:is|was)\s+(?:a\s+|the\s+)?(.+)',
                  '.*subject\s+of\s+(?:a\s+|the\s+)?(.+)',
                  ]

# some pre-defined forms of birthday queries
birthQueries = [
                '.*(?:is|was)\s+(.+)\s+born',
                '.*(?:birth|birthdate|birthdate)\s+of\s+(.+)',
                '.*(?:date|day|when)\s+(.+)\s+(?:is|was)\s+born.',
                ".*(?:is|was)\s+(.+)'s\s+birthda(?:y|te).",
                ]

birthWords = ['birthday', 'birthdate', 'birth', 'born']

def cleanSubject(subject):
    s = subject.strip()
    s = s.replace("'s",'')
    s = re.sub('\s+', ' ', s)
    s = string.capwords(s)
    for c in string.punctuation:
        s = s.replace(c, '')
    return s

def getResponse(msg):
    for q in birthQueries:
        match = re.match(q, msg, re.IGNORECASE)
        if match != None:
            subject = cleanSubject(match.group(1))
            print 'found birthday for ' + subject
            return getBirthday(subject)
    for q in subjectQueries:
        match = re.match(q, msg, re.IGNORECASE)
        if match != None:
            subject = cleanSubject(match.group(1))
            print 'found subject ' + subject
            return getSubjectInfo(subject)
    # Okay, REs didn't work... try something else
    birth = False
    words = msg.split()
    cleanWords = []
    for word in words:
        s = word
        for c in string.punctuation:
            s = s.replace(c, '')
        if s in birthWords:
            birth = True
        else:
            cleanWords.append(word)
    if (len(cleanWords) == 0):
        return "I don't know what you're talking about."
    # start from end, grab all cap words to get subject
    cleanWords.reverse()
    subj = []
    for word in cleanWords:
        if (word[0] in string.ascii_uppercase):
            subj.append(word)
    if (len(subj) == 0):
        return "I don't know what you're talking about."
    else:
        subj.reverse()
        subject = cleanSubject(' '.join(subj))
        return getBirthday(subject) if birth else getSubjectInfo(subject)
    
def main():
    msg = raw_input()
    resp = getResponse(msg)
    print 'Response:'
    print resp
    
if __name__ == "__main__":
    main()
