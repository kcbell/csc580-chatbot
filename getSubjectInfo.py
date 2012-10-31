"""
This function get the first 2 lines
of the subject being passed in as the parameter.
The two lines are taken from Wikipedia.
"""

import re, nltk

from urllib import urlopen

def checkForUppercaseLetter(s):
    if s[0] != ' ':
        return False
    index = 0
    while index < len(s) and s[index] == ' ':
        index += 1
    return s[index].isupper()

def getSubjectInfo(subject): 
    subjURL = subject.replace(" ", "_") 
    url = "http://en.wikipedia.org/w/api.php?format=xml&prop=revisions&rvprop=content&action=query&titles=" + subjURL
    html = urlopen(url).read()
    raw = nltk.clean_html(html)
    start = raw.lower().find(("'''" + subject.split(' ')[0]).lower())
    raw = raw[start:]
    raw = re.sub("'''([a-zA-Z0-9 \.]+)'''", '\g<1>', raw)
    raw = re.sub('\{\{(.+?)\}\}', '', raw)
    raw = re.sub('ref(.+?)/ref', '', raw)
    raw = re.sub('&[a-zA-Z;]+;', '', raw)
    raw = re.sub(r'\[\[([#a-zA-Z0-9 \.\(\)]+)\|([#a-zA-Z0-9 \.\(\)]+)\]\] \[\[([#a-zA-Z0-9 \.\(\)]+)\]\]', '\g<2> \g<3>', raw)
    raw = re.sub(r'\[\[([#a-zA-Z0-9 \.\(\)]+)\|([#a-zA-Z0-9 \.\(\)]+)\]\]', '\g<2>', raw)
    raw = re.sub(r'\[\[([#a-zA-Z0-9 \.\(\)]+)\]\]', '\g<1>', raw)
    raw = raw.replace('\n', ' ')
    endPunctuationCount = 0
    index = 0
    while index < len(raw) and endPunctuationCount < 2:
        if raw[index] in ['.', '?', '!'] and (raw[index - 1].islower() or not raw[index - 1].isalpha()) and checkForUppercaseLetter(raw[index + 1:]):
            endPunctuationCount += 1
        index += 1
    raw = raw[:index]
    return "I don't know about that." if len(raw) <= 1 else raw[0].upper() + raw[1:]

def main():
    msg = raw_input()
    resp = getSubjectInfo(msg)
    print 'Response:'
    print resp
    
if __name__ == "__main__":
    main()
