"""
This function get the first 2 lines
of the subject being passed in as the parameter.
The two lines are taken from Wikipedia.
"""

import re, nltk

from urllib import urlopen

def checkForUppercaseLetter(str):
	if str[0] != ' ':
		return False

	index = 0
	while index < len(str) and str[index] == ' ':
		index += 1
	return str[index].isupper()

def getSubjectInfo(subject): 
    subjURL = subject.replace(" ","_") 
    url = "http://en.wikipedia.org/w/api.php?format=xml&prop=revisions&rvprop=content&action=query&titles=" + subjURL
    html = urlopen(url).read()
    raw = nltk.clean_html(html)
    start = raw.find("'''" + subject.split(' ')[0])
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
	if raw[index] in ['.', '?', '!'] and (raw[index-1].islower() or not raw[index-1].isalpha()) and checkForUppercaseLetter(raw[index+1:]):
		endPunctuationCount += 1
	index += 1
    raw = raw[:index]
    return raw

def main():
    msg = raw_input()
    resp = getSubjectInfo(msg)
    print 'Response:'
    print resp
    
if __name__ == "__main__":
    main()
