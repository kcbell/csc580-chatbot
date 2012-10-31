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
import nltk, re, getBirthday, threading
from nltk.chat import eliza,zen

# this is a standin function for all responses that can easily be changed from here
#responseFun = eliza.eliza_chatbot.respond
responseFun = zen.zen_chatbot.respond

class TestBot(SingleServerIRCBot):
    state = 0
    mode = ""
    mTimer = ""
    states={0:{"_GREETED":1,"_INQUIRED":2,"_OUTREACH":4},
            1:{"_GREETED":3,"_INQUIRED":2},
            2:{"_GREETED":11,"_INQUIRED":11,"_REPLIED":10,"_FRUSTRATED":8},
            3:{"_GREETED":3,"_INQUIRED":2,"_REPLIED":3},
            4:{"_GREETED":5,"_INQUIRED":6,"_REPLIED":10,"_FRUSTRATED":7},
            5:{"_GREETED":11,"_INQUIRED":11,"_REPLIED":10,"_FRUSTRATED":8},
            6:{"_GREETED":11,"_INQUIRED":11,"_REPLIED":10,"_FRUSTRATED":8},
            7:{"_GREETED":5,"_INQUIRED":11,"_REPLIED":10,"_FRUSTRATED":9},
            8:{"_GREETED":11,"_INQUIRED":11,"_REPLIED":10,"_FRUSTRATED":9},
            9:{"_GREETED":11,"_INQUIRED":11,"_REPLIED":10,"_FRUSTRATED":11},
            10:{"_GREETED":11,"_INQUIRED":11,"_REPLIED":10},
            11:{"_GREETED":11,"_INQUIRED":11,"_REPLIED":11,"_FRUSTRATED":11}}
    responses=["","Hello!","I am Fine! How about you?","","Hi, there!","How are you?","I am good. How are you?","I said, Hi..","I said, How are you?..","Forget you!","That's good to hear. Bye!",""]

    def __init__(self, channel, nickname, server, port=6667):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)
        self.mTimer = threading.Timer(10.0,self.outreach)
        self.mTimer.start()

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments()[0])

    def on_pubmsg(self, c, e):
        a = e.arguments()[0].split(":", 1)
        if len(a) > 1 and irc_lower(a[0]) == irc_lower(self.connection.get_nickname()):
            self.do_command(e, a[1].strip())
        return

#We don't care about DCC messaging
#    def on_dccmsg(self, c, e):
#        c.privmsg("You said: " + e.arguments()[0])
#
#    def on_dccchat(self, c, e):
#        if len(e.arguments()) != 2:
#            return
#        args = e.arguments()[1].split()
#        if len(args) == 4:
#            try:
#                address = ip_numstr_to_quad(args[2])
#                port = int(args[3])
#            except ValueError:
#                return
#            self.dcc_connect(address, port)

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
            c.privmsg(self.channel,"I forgot!")
            self.state = 0
            self.mode = ""
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
            #if len(response) > 0:
            #    c.privmsg(self.channel,nick + ": " + response)
            #else:
            #    print "the end of the state reached."
                #if self.state == 2:
                    #c.privmsg(self.channel,nick + ": " + self.respond("inquiry"))
	    	
    def respond(self, nick, msg):
        c = self.connection
        if msg.lower().find("hello") > -1 or msg.lower().find("hi") > -1 or msg.lower().find("hey") > -1:
            self.nextState("_GREETED")
            if len(self.responses[self.state]) > 0:
                c.privmsg(self.channel,nick + ": " + self.responses[self.state])
                if self.state == 2 or self.state == 5 or self.state == 6:
                    self.mTimer = threading.Timer(20.0, self.frustrated, args=(nick,))
                    self.mTimer.start()
            return
        elif msg.lower().find("how") > -1 and msg.lower().find("?") > -1:
            self.nextState("_INQUIRED")
            if len(self.responses[self.state]) > 0:
                c.privmsg(self.channel,nick + ": " + self.responses[self.state])
                if self.state == 2 or self.state == 5 or self.state == 6:
                    self.mTimer = threading.Timer(20.0, self.frustrated, args=(nick,))
                    self.mTimer.start()
            return
        elif msg.lower().find("good") > -1 or msg.lower().find("fine") > -1 or msg.lower().find("ok") > -1:
            self.nextState("_REPLIED")
            if len(self.responses[self.state]) > 0:
                c.privmsg(self.channel,nick + ": " + self.responses[self.state])
            return
        else:
            m = re.search("(\w+)[^\w](\w+)[^\w](born\??)", msg)
            if m:
                name = m.group(1) + " " + m.group(2)
                c.privmsg(self.channel,nick + ": " + getBirthday.getBirthday(name))
                return
            
            m = re.search("(\w+)[^\w](\w+)[^\w][s][^\w](birthday\??)", msg)
            if m:
                name = m.group(1) + " " + m.group(2)
                c.privmsg(self.channel,nick + ": " + getBirthday.getBirthday(name))
                return
                          

            c.privmsg(self.channel,nick + ": " + responseFun(msg))
            return
        
    
    def nextState(self, inp):
        print inp
        nextStates = self.states[self.state]
        self.state = nextStates[inp]
                       

    def outreach(self):
        c = self.connection
        (chname, chobj) = self.channels.items()[0]
        users = chobj.users()
        users.sort()
        try:
            idx = users.index("foaad_")
        except ValueError:
            idx = -1
        if idx < 0:
            try:
                idx = users.index("toshi_")
            except ValueError:
                idx = -1
        if idx < 0:
            idx = 0
        #while idx < len(users):
            #self.state = 0
        nick = users[idx]
        self.nextState("_OUTREACH")
        response = self.responses[self.state]
        if len(response) > 0:
            c.privmsg(self.channel,nick + ": " + response)
            self.mTimer.cancel()
            self.mTimer = threading.Timer(20.0, self.frustrated, args=(nick,))
            self.mTimer.start()
            #idx += 1
             
    def frustrated(self,nick):
        c = self.connection
        self.nextState("_FRUSTRATED")
        response = self.responses[self.state]
        if len(response) > 0:
            c.privmsg(self.channel,nick + ": " + response)
            self.mTimer.cancel()
            self.mTimer = threading.Timer(10.0, self.frustrated, args=(nick,))
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

    
