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
    url = "http://en.wikipedia.org/w/api.php?format=xml&prop=extracts&explaintext=true&action=query&redirects=yes&titles=" + subjURL
    html = urlopen(url).read()
    raw = nltk.clean_html(html)
    raw = re.sub(r'\[.*\]', '', raw)
    raw = raw.replace('\n', ' ')
    return raw

def getFirstTwoLines(raw):
    endPunctuationCount = 0
    index = 0
    try:
        while index < len(raw) and endPunctuationCount < 2:
            if raw[index] in ['.', '?', '!'] and (raw[index - 1].islower() or not raw[index - 1].isalpha()) and checkForUppercaseLetter(raw[index + 1:]):
                endPunctuationCount += 1
            index += 1
        raw = raw[:index]
    except IndexError:
        pass
    ret = "I don't care about that." if len(raw) <= 1 else raw[0].upper() + raw[1:]
    return "Which one?" if ret.endswith(" to:") else ret

def getContentDict(raw):
    if 'may refer to:' in raw[:raw.find(':')+1] or len(raw) < 1:
        return None
    raw = raw.replace('&quot;', '"')
    raw = re.sub(r'(\s)*==+(.+?)==+(\s)*', '[\g<2>] ', raw)
    sections = re.findall(r'\[(.+?)\]', raw)
    subjDict = {}
    index = 0
    tempRaw = raw
    uselessInfo = ['bibliography', 'primary sources', 'further reading and resources', 'external links', 'notes', 'see also', 'further reading', 'references', 'publications']

    subjDict['Introduction'] = tempRaw[:tempRaw.find(sections[index])-1]
    while index < len(sections) - 1:
        if sections[index].strip().lower() in uselessInfo:
            index += 1
            continue
        start = tempRaw.find(sections[index])
        end = tempRaw.find(sections[index+1])
        s = tempRaw[start+len(sections[index])+1:end-1]
        if s != ' ':
            subjDict[sections[index].strip()] = tempRaw[start+len(sections[index])+1:end-1].strip()
        index += 1
        tempRaw = tempRaw[end:]
    if sections[index].strip().lower() not in uselessInfo:
        subjDict[sections[index].strip()] = tempRaw[tempRaw.find(sections[index])+len(sections[index])+1:].strip()    
    return subjDict

def getRandomFacts(subject, subjDict):
    factList = []
    subjSplit = subject.split(' ')
    for k in subjDict.keys():
        sentences = nltk.sent_tokenize(subjDict[k])
        for s in sentences:
            for subjToken in subjSplit:
                if subjToken in s and s[-1] in ['.', '!']:
                    factList.append(s.replace('&amp;', '&'))
                    break
    return factList

def getFacts(origSubj, newSubj):
    content = getContentDict(getSubjectInfo(newSubj))
    if content == None:
        return []
    facts = getRandomFacts(origSubj, content)
    return facts

def main():
    msg = raw_input()
    #resp = getFirstTwoLines(getSubjectInfo(msg))
    facts = getFacts(msg, msg)
    for f in facts:
        print f
    
if __name__ == "__main__":
    main()
