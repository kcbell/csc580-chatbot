"""
The function to get the birth date..
Returns a response sentence including birthday when it is found.
Other wise it the response says 'was born in the past..'
"""

import re, nltk, random, getSubjectInfo

from urllib import urlopen


def getRelatedTopic(name): #name = <firstName><space><lastName> or <name>
    
    links = getLinks(name,50)
    result = None
		
    if len(links) > 0:
        
        idx = -1
        
        #check to see if the linked page refers back to this page
        while len(links) != 0 and idx == -1:
            topic = random.choice(links)  #randomly picks a topic(link)

            print "checking related topic: " + topic[0] 
            rLinks = getLinks(topic[0],100) #get links from the linked page

            #print rLinks
            for l in rLinks:
                idx = l[0].lower().find(name.lower()) #check to see if there is a link to this page
                if idx > -1:
                    break                    
                
            if idx == -1:
                links.remove(topic)      #if no link, remove the toic (link)

        if idx > -1: #if a topic (link) is found
            relatedSentence = getRelatedSentence(name, topic)
            relatedSentence = relatedSentence.replace("&quot;", '"').replace("&amp;", '&').replace('[play]','').replace('[Listen]', '')
            pageTitle = topic[0].replace(" ","_") #convert to firstName_lastName
            
            # call Jake's function here
            #result = getSubjectInfo.getFacts(name, pageTitle)         #get some fuct from the linked page

            result = (topic[0], relatedSentence if len(relatedSentence) > 0 and relatedSentence[-1] in ['.','!'] else None)
            
    return result

def getLinks(name, maxLink):
    startTag = '[['
    endTag = ']]'
    links = []
    
    title = name.replace(" ","_") #convert to firstName_lastName
    url = "http://en.wikipedia.org/w/api.php?format=xml&prop=revisions&rvprop=content&rvsection=0&action=query&redirects=yes&titles=" + title
    #print "using url " + url
    try:
        html = urlopen(url).read()
    except:
        return links

    
    if len(html) > 0: #if the page is found
        str = html
    else:   # if the page not found
        return links  #return empty list
    
    idx1 = str.find(startTag)   # find start tag
    count = 0
    while idx1 > -1 and count < maxLink:
        idx2 = str.find(endTag) # find end tag
        link = str[(idx1 + len(startTag)) : idx2] #get link
        if len(link) > 0 and not link.startswith("File:"): #if any link is found
            idx = link.find("|")  #look for text for display purpose only
            if idx > -1:
                txt = link[idx+1:]
                link = link[:idx] #remove the text
            else:
                txt = ""

            links.append((link.replace("&amp;#039;","'"),txt)) #append the link to the list
                
        str = str[idx2 + len(endTag):] #slide the window
        idx1 = str.find(startTag) #find next start tag
        count += 1                #increment the count
        
    return links                  #return the list of links

def getRelatedSentence(name, topic):
    #print name, topic
    title = name.replace(" ","_") #convert to firstName_lastName
    url = "http://en.wikipedia.org/w/api.php?format=xml&prop=extracts&explaintext=true&action=query&redirects=yes&titles=" + title
    #url = "http://en.wikipedia.org/w/api.php?format=xml&prop=revisions&rvprop=content&rvsection=0&action=query&redirects=yes&titles=" + title

    target = ""
    
    try:
        html = urlopen(url).read()
    except:
        return target
    
    raw = nltk.clean_html(html)
    rawSents = nltk.sent_tokenize(raw)
    sentences = []
    for rawSent in rawSents:
        if rawSent.find("\n"):
            splits = rawSent.split("\n")
            sentences.extend(splits)
        else:
            sentences.append(rawSent)
    
    target = ""
    for sent in sentences:
        if len(topic[1]) > 0 and sent.find(topic[1]) > -1:
            target = sent
            break
        elif len(topic[1]) == 0 and sent.find(topic[0]) > -1:
            target = sent
            break
        
    if len(target) > 0:
        print target
    
    return target
        
            
    
    


def main():
    msg = raw_input()
    resp = getRelatedTopic(msg)
    print 'Response:'
    print resp
    
if __name__ == "__main__":
    main()
