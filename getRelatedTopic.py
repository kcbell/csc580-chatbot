"""
The function to get the birth date..
Returns a response sentence including birthday when it is found.
Other wise it the response says 'was born in the past..'
"""

import re, nltk, random

from urllib import urlopen


def getRelatedTopic(name): #name = <firstName><space><lastName> or <name>
    
    links = getLinks(name,50)
    result = None
		
    if len(links) > 0:
        
        idx = -1
        
        #check to see if the linked page refers back to this page
        while len(links) != 0 and idx == -1:
            topic = random.choice(links)  #randomly picks a topic(link)
            rLinks = getLinks(topic,100) #get links from the linked page
            #print rLinks
            for l in rLinks:
                idx = l.lower().find(name.lower()) #check to see if there is a link to this page
                if idx > -1:
                    break                    
                
            if idx == -1:
                links.remove(topic)      #if no link, remove the toic (link)

        if idx > -1: #if a topic (link) is found
            pageTitle = topic.replace(" ","_") #convert to firstName_lastName
            
            # call Jake's function here
            result = (pageTitle, name)         #get some fuct from the linked page
    
    return result

def getLinks(name, maxLink):
    title = name.replace(" ","_") #convert to firstName_lastName
    url = "http://en.wikipedia.org/w/api.php?format=xml&prop=revisions&rvprop=content&rvsection=0&action=query&redirects=yes&titles=" + title
    html = urlopen(url).read()

    startTag = '[['
    endTag = ']]'
    links = []
    str = html
    idx1 = str.find(startTag)
    count = 0
	
    while idx1 > -1 and count < maxLink:
        idx2 = str.find(endTag)
        link = str[(idx1 + len(startTag)) : idx2]
        str = str[idx2 + len(endTag):]
        '''
        if len(link) > 0:
            try:
                links.index(link)
            except ValueError:
                links.append(link)
        '''
        if len(link) > 0:
            idx = link.find("|")
            if idx > 0:
                link = link[:idx]
            links.append(link.replace("&amp;#039;","'"))
        idx1 = str.find(startTag)
        count += 1
        
    return links

    
def main():
    msg = raw_input()
    resp = getRelatedTopic(msg)
    print 'Response:'
    print resp
    
if __name__ == "__main__":
    main()
