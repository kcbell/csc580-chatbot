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
                  '.*about\s+(.+)',
                  '.*what\s+(?:is|was)\s+(.+)',
                  '.*who\s+(?:is|was)\s+(.+)',
                  '.*subject\s+of\s+(.+)',
                  ]

# some pre-defined forms of birthday queries
birthQueries = [
                '.*(?:is|was)\s+(.+)\s+born',
                '.*(?:birth|birthdate|birthdate)\s+of\s+(.+)',
                '.*(?:date|day|when)\s+(.+)\s+(?:is|was)\s+born.',
                ".*(?:is|was)\s+(.+)'s\s+birthda(?:y|te).",
                ]

def cleanSubject(subject):
    s = subject.strip()
    s = re.sub('\s+', ' ', s)
    for c in string.punctuation:
        s = s.replace(c, '')
    return s

def getResponse(msg):
    for q in birthQueries:
        match = re.match(q, msg, re.IGNORECASE)
        if match != None:
            subject = cleanSubject(match.group(1))
            return getBirthday(subject)
    for q in subjectQueries:
        match = re.match(q, msg, re.IGNORECASE)
        if match != None:
            subject = cleanSubject(match.group(1))
            return getSubjectInfo(subject)
    return "I don't know what you're talking about."
    
def main():
    msg = raw_input()
    resp = getResponse(msg)
    print 'Response:'
    print resp
    
if __name__ == "__main__":
    main()
