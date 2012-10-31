"""
The function to get the birth date..
Returns a response including birthday when it is fouond.
Other wise it the response says 'was born in the past..'
"""

import re, nltk

from urllib import urlopen


def getBirthday(name): #name = <firstName><space><lastName> or <name>
    states = {}
    state = 0
    months = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    birthDate = []
    title = name.replace(" ","_") #convert to firstName_lastName
    url = "http://en.wikipedia.org/w/api.php?format=xml&prop=revisions&rvprop=content&action=query&titles=" + name
    #url = "http://en.wikipedia.org/wiki/" + title
    html = urlopen(url).read()
    #raw = nltk.clean_html(html)
    #tokens = nltk.word_tokenize(raw)
    #tokens = html.split("|")
    idx = html.lower().find("birth date")
    if idx > -1:
        text = html[idx:]
        print text[:100]
        m = re.search("(\d{4})[^\w](\d{1,2})[^\w](\d{1,2})", text)

        if m:
            print m.group(1), m.group(2), m.group(3)
            year, month, day = m.group(1, 2, 3)
            print month, day, year
            result = name + " was born on " + months[int(month)] + " " + day + "," + year
        else:
            result = name + " was born in the past.."
    else:
        result = name + " was born in the past.."

    return result
        


#print getBirthday("Michael Jackson")


