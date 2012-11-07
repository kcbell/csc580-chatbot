#! /usr/bin/env python
#
# irc chatbot program implementation in Python
# using NLTK built-in chatbots (Eliza,Zen) as example
# modified from original example using ircbot.py by Joel Rosdahl
# must have the python-irclib-0.4.8 installed
# Foaad Khosmood


# usage example: python testbot.py irc.mibbit.net "#mychannel" nickName1 
"""A simple example bot.

This is an example bot that uses the SingleServerIRCBot class from
ircbot.py.  The bot enters a channel and listens for commands in
private messages and channel traffic.  Commands in channel messages
are given by prefixing the text by the bot name followed by a colon.
It also responds to DCC CHAT invitations and echos data sent in such
sessions.

The known commands are:

    stats -- Prints some channel information.

    disconnect -- Disconnect the bot.  The bot will try to reconnect
                  after 60 seconds.

    die -- Let the bot cease to exist.

    dcc -- Let the bot invite you to a DCC CHAT connection.
"""
#import irc bot
from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad, ip_quad_to_numstr

# import NLTK objects
import nltk, re, getBirthday, threading, time, random
from nltk.chat import eliza,zen

import questionAnswer

from getSubject import getSubjects, punct
from getRelatedTopic import getRelatedTopic
from getSubjectInfo import getFacts

CHARS_PER_SEC = 25

class TestBot(SingleServerIRCBot):
    state = 0
    mTimer = ""
    states={0:{"_GREETED":1,"_INQUIRED":2,"_OUTREACH":4},
            1:{"_GREETED":3,"_INQUIRED":2},
            2:{"_GREETED":13,"_INQUIRED":2,"_INQUIRY":11},
            3:{"_GREETED":3,"_INQUIRED":2,"_REPLIED":3},
            4:{"_GREETED":5,"_INQUIRED":6,"_REPLIED":4,"_FRUSTRATED":7},
            5:{"_GREETED":8,"_INQUIRED":6,"_REPLIED":10,"_FRUSTRATED":8},
            6:{"_GREETED":13,"_INQUIRED":13,"_REPLIED":13,"_INQUIRY":11},
            7:{"_GREETED":5,"_INQUIRED":6,"_REPLIED":7,"_FRUSTRATED":9},
            8:{"_GREETED":8,"_INQUIRED":8,"_REPLIED":10,"_FRUSTRATED":9},
            9:{"_GREETED":5,"_INQUIRED":12,"_REPLIED":10,"_DONE":13},
            10:{"_DONE":13},
            11:{"_GREETED":8,"_INQUIRED":12,"_REPLIED":10,"_FRUSTRATED":8},
            12:{"_DONE":13},
            13:{"_GREETED":13,"_INQUIRED":13,"_REPLIED":13,"_FRUSTRATED":13}}
    responses=["","Hello!","I am Fine!","","Hi, there!","How are you?","I am good.","I said, Hi..","I said, How are you?..","Forget you!","That's good to hear... Good. Now the social niceties are out of the way.","How are you?","Pretty good.",""]

    def __init__(self, channel, nickname, server, port=6667):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)
        print "Connected as %s." % self.connection.get_nickname()
        self.mTimer = threading.Timer(60.0,self.outreach)
        self.mTimer.start()

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments()[0])

    def on_pubmsg(self, c, e):
        a = e.arguments()[0].split(":", 1)
        if len(a) > 1 and irc_lower(a[0]) == irc_lower(self.connection.get_nickname()):
            self.do_command(e, a[1].strip())
        elif len(a) > 1:
            print "Attempting interrupt"
            self.interrupt(nm_to_n(e.source()), a[1].strip())
        return

    # deals with other people's conversations
    def interrupt(self, nick, cmd, tangent = True):
        c = self.connection
        subjs = getSubjects(cmd)
        subjs.reverse() # start from end of message
        facts = None
        firstFact = None
        print "Got subjects: " + str(subjs)
        for subj in subjs:
            topic = getRelatedTopic(subj) if tangent else subj
            print "Got topic: " + str(topic)
            if topic != None:
                facts = getFacts(subj, topic[0])
                if (facts != None and len(facts) > 0):
                    firstFact = topic[1]
                    topic = topic[0]
                    break
        # I have something to talk about!
        print "Got facts: " + str(facts)
        if (facts == None or len(facts) == 0):
            print "Giving up"
            if tangent:
                resp = random.choice(["I don't care about that.",
                                      "That's boring.",
                                      "Why would you even want to talk about that?",
                                      "Why should I care?",
                                      "I couldn't care less.",
                                      "I'm sure you would know. On second thought, you probably wouldn't even know that.",
                                      None])# special one
                time.sleep(8)
                if resp == None:
                    resp = random.choice(["Well, I find that topic quite interesting.",
                                          "I would really like to know more about that.",
                                          "Sounds like a great learning opportunity for me."])
                    c.privmsg(self.channel,nick + ": " + resp)
                    time.sleep(5)
                    resp = random.choice(["That was sarcasm. Could you tell?",
                                          "*Sigh* Sarcasm is hard to communicate over text, isn't it?"])
                    c.privmsg(self.channel,nick + ": " + resp)
                else:
                    c.privmsg(self.channel,nick + ": " + resp)
            return 
        self.mTimer.cancel()
        random.shuffle(facts)
        if firstFact != None:
            facts.insert(0, firstFact)
        else:
            for fact in facts:
                if fact.find(topic) >= 0:
                    facts.remove(fact)
                    facts.insert(0, fact)
        time.sleep(len(facts[0]) / CHARS_PER_SEC)
        c.privmsg(self.channel, nick + ": " + self.formatFirst(facts[0]))
        for i in xrange(1, min(len(facts), 10), 2): # don't say more than 5 things
            time.sleep(len(facts[i]) / CHARS_PER_SEC)
            c.privmsg(self.channel,nick + ": " + facts[i])
        resp = random.choice(["You're not even listening, are you?",
                              "I can tell you don't care.",
                              "Oh, you don't understand anyway.",
                              "Are you even listening to me?",
                              "Well, it's lost on you anyway."])
        time.sleep(8)
        c.privmsg(self.channel,nick + ": " + resp)
        self.reset()
            
    def formatFirst(self, msg):
        resp = random.choice(["Did you know that %s?",
                              "I'll bet you didn't know that %s.",
                              "Interesting fact: %s.",
                              "Something you probably don't know is that %s.",
                              "You might be interested to know %s."])
        return resp % msg[:-1]

    #processes commands
    def do_command(self, e, cmd):
        nick = nm_to_n(e.source())
        c = self.connection
        #run through all known commands, add more here if needed
        if cmd == "disconnect":
            self.disconnect()
        elif cmd == "die":
            c.privmsg(self.channel,"I shall!!!")
            self.die()
        elif cmd == "forget":
            self.reset()
            c.privmsg(self.channel,"I forgot!")
        elif cmd == "stats":
            for chname, chobj in self.channels.items():
                c.notice(nick, "--- Channel statistics ---")
                c.notice(nick, "Channel: " + chname)
                users = chobj.users()
                users.sort()
                c.notice(nick, "Users: " + ", ".join(users))
                opers = chobj.opers()
                opers.sort()
                c.notice(nick, "Opers: " + ", ".join(opers))
                voiced = chobj.voiced()
                voiced.sort()
                c.notice(nick, "Voiced: " + ", ".join(voiced))
        else:
            print cmd
            self.mTimer.cancel()
            response = self.respond(nick, cmd)
	    	
    def respond(self, nick, msg):
        c = self.connection
        time.sleep(3)
        if re.search("^hi|^hey|^hello", msg.lower()):
            self.nextState("_GREETED")
            if len(self.responses[self.state]) > 0:
                c.privmsg(self.channel,nick + ": " + self.responses[self.state])
                if self.state == 5:
                    self.mTimer = threading.Timer(20.0, self.frustrated, args=(nick,))
                    self.mTimer.start()
            else:
                self.reset()
            return
        elif re.search("how[^\w]\w+[^\w]you\??|how[^\w]\w+[^\w]\w+[^\w]\w+\??", msg.lower()):
            self.nextState("_INQUIRED")
            if len(self.responses[self.state]) > 0:
                c.privmsg(self.channel,nick + ": " + self.responses[self.state])
                if self.state == 2 or self.state == 6:
                    time.sleep(3)
                    self.nextState("_INQUIRY")
                    c.privmsg(self.channel,nick + ": " + self.responses[self.state])
                    self.mTimer = threading.Timer(20.0, self.frustrated, args=(nick,))
                    self.mTimer.start()
                elif self.state == 12:
                    self.nextState("_DONE")
            else:
                self.reset()                
            return
        elif re.search("good(.|!)?|ok(.|!)?|fine(.|!)?|all[^\w]right", msg.lower()):
            self.nextState("_REPLIED")
            if len(self.responses[self.state]) > 0:
                c.privmsg(self.channel,nick + ": " + self.responses[self.state])
                if self.state == 10:
                    self.nextState("_DONE")
                    self.reset()
            else:
                self.reset()
            return
        else:
            print "Attempting talking about something.kcbe"
            self.interrupt(nick, msg, False)
            return
        time.sleep(5)
    
    def nextState(self, inp):
        print inp
        nextStates = self.states[self.state]
        self.state = nextStates[inp]
                       

    def outreach(self):
        c = self.connection
        (chname, chobj) = self.channels.items()[0]
        users = chobj.users()
        try:
            idx = users.index("foaad")
        except ValueError:
            idx = -1
        if idx < 0:
            try:
                idx = users.index("toshi_")
            except ValueError:
                idx = -1
        if idx < 0:
            while True:
                idx = random.randint(0,len(users)-1)
                if users[idx] != c.get_nickname():
                    break
                
        nick = users[idx]
        self.nextState("_OUTREACH")
        response = self.responses[self.state]
        if len(response) > 0:
            c.privmsg(self.channel,nick + ": " + response)
            self.mTimer.cancel()
            self.mTimer = threading.Timer(20.0, self.frustrated, args=(nick,))
            self.mTimer.start()
        else:
            self.reset()

             
    def frustrated(self,nick):
        c = self.connection
        self.nextState("_FRUSTRATED")
        response = self.responses[self.state]
        if len(response) > 0:
            c.privmsg(self.channel,nick + ": " + response)
            if self.state != 9:
                self.mTimer.cancel()
                self.mTimer = threading.Timer(10.0, self.frustrated, args=(nick,))
                self.mTimer.start()
            else:
                self.nextState("_DONE")
                self.reset()
        else:
            self.reset()

    def reset(self):
        self.state = 0
        self.mTimer.cancel()
        self.mTimer = threading.Timer(60.0,self.outreach)
        self.mTimer.start()

def main():
    import sys
    if len(sys.argv) != 4:
        print "Usage: testbot <server[:port]> <channel> <nickname>"
        sys.exit(1)

    s = sys.argv[1].split(":", 1)
    server = s[0]
    if len(s) == 2:
        try:
            port = int(s[1])
        except ValueError:
            print "Error: Erroneous port."
            sys.exit(1)
    else:
        port = 6667
    channel = '#' + sys.argv[2]
    nickname = sys.argv[3]

    bot = TestBot(channel, nickname, server, port)
    bot.start()

if __name__ == "__main__":
    main()

    
