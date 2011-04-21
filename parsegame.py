#!/usr/bin/env python
from twisted.web import microdom
from Queue import Queue

import MySQLdb
import time

import pickle

import re
from threading import Thread

import sys
sys.path.append('./BeautifulSoup-3.2.0')
from BeautifulSoup import BeautifulSoup



# Data model
class Game(object):
    def __init__(self):
        self.id = ""
        self.jarchiveID = -1
        self.playDate = ""
        self.firstPlayer = -1
        self.firstScore = -1
        self.secondPlayer = -1
        self.secondScore = -1
        self.thirdPlayer = -1
        self.thirdScore = -1
        self.players = []
        self.categories = []

class Category(object):
    def __init__(self):
        self.clues = []
        self.id = ""
        self.name = ""
        self.game = -1
        self.boardPosition = -1
        self.round = -1

class Player(object):
    def __init__(self):
        self.id = ""
        self.fullName = ""
        self.nick = ""
        self.description = ""

class Clue(object):
    def __init__(self):
        self.answers = []
        self.id = ""
        self.text = ""
        self.game = -1
        self.category = -1
        self.value = -1
        self.answer = ""
        self.isDD = False
        self.pickIndex = -1

class Answer(object):
    def __init__(self):
        self.id = ""
        self.player = -1
        self.clue = -1
        self.correct = False
        self.wager = -1
        self.turn = -1
        self.text = ""
        self.nick = ""

def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

class GameLoader(Thread):

    def __init__(self, queue, gameNumber):
        Thread.__init__(self)
        self.sharedObject = queue
        self.gamePlayers  = {}
        self.clueCategories = []
        self.gameNumber = gameNumber 
        self.roundNumber = 0
        self.theGame = None

    def run(self):
        print "Producer running, game number: " + str(self.gameNumber)
        self.loadGame(self.gameNumber)
        print "Producer done, game number: " + str(self.gameNumber)

    def loadGame(self, gameNumber):
        self.gamePlayers  = {}
        self.clueCategories = []
        self.roundNumber = 0
        self.theGame = None

        self.theGame = Game()
        self.theGame.id = gameNumber
        try:
            #dom_responses = microdom.parseString(str(BeautifulSoup(open("games/game_responses_" + str(self.gameNumber) + ".html"))).replace(' & ', ' &amp; ').replace('$&!', '$&amp;!').replace('an &', 'an &amp;').replace('aw &','aw &amp;'))
            dom_responses = microdom.parseString(str(BeautifulSoup(open("games/game_responses_" + str(self.gameNumber) + ".html"))).replace(' & ', ' &amp; ').replace('$&!', '$&amp;!').replace(' &<',' &amp;<').replace('B&B','B&amp;B').replace('&"','&amp;"'))
            #dom_responses = microdom.parseString(BeautifulSoup(open("games/game_responses_" + str(self.gameNumber) + ".html")).prettify())
            dom = microdom.parseString(str(BeautifulSoup(open("games/game_" + str(self.gameNumber) + ".html"))).replace(' & ', ' &amp; ').replace('$&!', '$&amp;!').replace(' &<', ' &amp;<').replace('B&B','B&amp;B').replace('&"','&amp;"'))
        except Exception, e:
            print "Exception parsing game " + str(self.gameNumber)
            print e
            return

        title = dom.getElementById("game_title")
        
        (jid, playDate) = title.firstChild().firstChild().data.split(' - ')
        jid = jid.replace('Show #', '')
        hthrees = dom.getElementsByTagName("h3")
        for hthree in hthrees:
            if "Final scores" in hthree.firstChild().data:
                scoreTable = hthree.parentNode.getElementsByTagName("table")[-2]
                break
        scoreTable = scoreTable.childNodes

        self.parse_contestants(dom, scoreTable)

        self.theGame.jarchiveID = jid
        self.theGame.playDate = playDate 
        self.theGame.firstPlayer = self.gamePlayers[scoreTable[0].childNodes[0].firstChild().data]
        self.theGame.firstScore = scoreTable[1].childNodes[0].firstChild().data.replace('$', '').replace(',', '')
        self.theGame.secondPlayer = self.gamePlayers[scoreTable[0].childNodes[1].firstChild().data]
        self.theGame.secondScore = scoreTable[1].childNodes[1].firstChild().data.replace('$', '').replace(',', '')
        self.theGame.thirdPlayer = self.gamePlayers[scoreTable[0].childNodes[2].firstChild().data]
        self.theGame.thirdScore = scoreTable[1].childNodes[2].firstChild().data.replace('$', '').replace(',', '')

        self.parse_clues(dom, dom_responses)
        self.sharedObject.put( self.theGame )


    def parse_contestants(self, dom, scoreTable):
#        cur = dbcon.cursor()
        contestants = dom.getElementById("contestants_table").getElementsByTagName("p")

        
        for i, contestant in enumerate(contestants):
            nPlayer = Player()
            desc = contestant.lastChild().data
            contestant = contestant.firstChild()
            (url, playerId) = contestant.getAttribute("href").split('=')
            ##print "jarchive ID: " + playerId
            fullName = contestant.firstChild().data
            nick = scoreTable[0].childNodes[i].firstChild().data
            #print "fullName: " + fullName
            #print "nick: " + nick
            desc = desc.replace(', ', '')
            #print "desc: " + desc
            nPlayer.fullName = fullName
            nPlayer.nick = nick
            nPlayer.id = playerId
            nPlayer.description = desc
            self.theGame.players.append(nPlayer)

            #cur.execute("INSERT INTO PLAYER (fullName, nick, description) VALUES (%s, %s, %s)", (fullName, nick, desc))
            #dbcon.commit()
            self.gamePlayers[nick] = playerId

    def parse_clues(self, dom, dom_responses):
        for clue_prefix in ["J", "DJ", "FJ"]:

            if clue_prefix == "J":
                jround = dom.getElementById("jeopardy_round")
                self.roundNumber = 0
            elif clue_prefix == "DJ":
                jround = dom.getElementById("double_jeopardy_round")
                self.roundNumber = 1
            elif clue_prefix == "FJ":
                jround = dom.getElementById("final_jeopardy_round")
                self.roundNumber = 2

            categories = []
            category_elements = jround.getElementsByTagName("td")

            for category in category_elements:
                if category.getAttribute("class") == "category_name":
                    cText = remove_html_tags(category.toxml())
                    categories.append(cText)


            for i in range(0, len(categories)):
                nCat = Category()
                #print categories[i]
                nCat.name = categories[i]
                nCat.game = self.theGame.id
                nCat.boardPosition = i
                nCat.round = self.roundNumber

                #cur.execute("INSERT INTO CATEGORY (name, game, boardPosition) VALUES (%s, %s, %s)", (categories[i], self.gameID, i))
                #dbcon.commit()
                self.theGame.categories.append(nCat)
                #self.clueCategories.append(cur.lastrowid)
            
                

            # a jeopardy board is 6x5
            # the order works out that the index of the elements in the array + 1 are the clue id's

            if clue_prefix in ["J", "DJ"]:
                # outer loop is the category index
                for i in range(1, 7):
                    # inner loop is the clue index
                    for j in range(1, 6): 
                        nClue = Clue()
                        clueLocator = "clue_" + clue_prefix + "_" + str(i) + "_" + str(j)
                        clue = dom.getElementById(clueLocator)
                        clueText = ""
                        clueValue = 0
                        isDD = 0
                        isFinal = 0
                        clueAnswer = ''
                        pickIndex = -1
                        if not clue:
                            continue

                        for childNode in clue.childNodes:
                            clueText = clueText + remove_html_tags(childNode.toxml())
                        #print clueText

                        clue = dom.getElementById("clue_" + clue_prefix + "_" + str(i) + "_" + str(j) + "_stuck")
                        for childNode in clue.parentNode.childNodes:
                            if childNode.getAttribute("class") == "clue_value":
                                clueValue = int(childNode.firstChild().data.replace('$', '').replace(',',''))
                                #print clueValue 

                            if childNode.getAttribute("class") == "clue_value_daily_double":
                                (dd, clueValue) = childNode.firstChild().data.split(' ')
                                isDD = 1
                                clueValue = int(clueValue.replace('$', '').replace(',',''))
                                #print "Value: " + str(clueValue)

                            if childNode.getAttribute("class") == "clue_order_number":
                                pickIndex = int(childNode.firstChild().firstChild().data)
                                #print "Answer number: " + str(pickIndex) 

                        clue_response = dom_responses.getElementById("clue_" + clue_prefix + "_" + str(i) + "_" + str(j) + "_stuck")
                        # yeah, this sucks, look at the html for why we do this.
                        #           <td>         <tr>       <table>    <div>      <td>       <tr>       <table>    <tr>        <td>
                        responses = clue_response.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.lastChild().firstChild()
                        correct_answer = responses.getElementsByTagName("em")[0].firstChild()

                        if isinstance(correct_answer, microdom.Text):
                            clueAnswer = correct_answer.data
                            #print "answer: " + clueAnswer
                        else: 
                            clueAnswer = correct_answer.firstChild().data
                            #print "answer: " + clueAnswer


                        player_status = responses.getElementsByTagName("table")[0].getElementsByTagName("td")
                        turn = 0
                        for player in player_status:
                            if player.getAttribute("class") == "wrong":
                                if player.firstChild().data == "Triple Stumper":
                                    #print "No players got this correct"
                                    pass
                                else:
                                    nick = player.firstChild().data 
                                    nAnswer = Answer()
                                    nAnswer.nick = nick
                                    nAnswer.correct = 0
                                    nAnswer.wager = clueValue
                                    nAnswer.turn = turn
                                    nClue.answers.append(nAnswer)
                                    
                            else:
                                nick = player.firstChild().data 

                                nAnswer = Answer()
                                nAnswer.nick = nick
                                nAnswer.correct = 1
                                nAnswer.wager = clueValue
                                nAnswer.turn = turn
                                nClue.answers.append(nAnswer)

                            turn = turn + 1

                        nClue.text = clueText
                        nClue.game = self.theGame.id
                        nClue.value = clueValue
                        nClue.answer = clueAnswer
                        nClue.isDD = isDD
                        nClue.pickIndex = pickIndex
                        if self.roundNumber == 1:
                            # when we're in double jeopardy, be sure we set the category correctly
                            self.theGame.categories[i + 5].clues.append(nClue)
                        else:
                            self.theGame.categories[i - 1].clues.append(nClue)

            else:
                nClue = Clue()
                clue = dom.getElementById("clue_" + clue_prefix )
                clueText = ""
                clueValue = 0
                isDD = 0
                isFinal = 1
                clueAnswer = ''
                pickIndex = -1
                self.roundNumber = 2
                for childNode in clue.childNodes:
                    clueText = remove_html_tags(childNode.toxml())
                fjround = dom_responses.getElementById("final_jeopardy_round")
                correct_answer = fjround.getElementsByTagName("em")[0]
                clueAnswer = remove_html_tags(correct_answer.toxml())
                tds = fjround.getElementsByTagName("td")
                for td in tds:
                    if td.getAttribute("class") == "clue_text":
                        table = td.getElementsByTagName("table")[0]
                        turn = 0
                        for i in range(len(table.childNodes)):
                            # we expect 6 rows; 0 is the person, 1 is the wager, etc..
                            tr = table.childNodes[i]
                            if tr.firstChild().getAttribute("class") == "right":
                                nick =  tr.firstChild().firstChild().data
                                clueValue =  int(table.childNodes[i+1].firstChild().firstChild().data.replace('$', '').replace(',',''))
                                nAnswer = Answer()
                                nAnswer.nick = nick
                                nAnswer.correct = 1
                                nAnswer.wager = clueValue
                                nAnswer.turn = turn
                                nClue.answers.append(nAnswer)
                                turn = turn + 1
                            elif tr.firstChild().getAttribute("class") == "wrong":
                                nick =  tr.firstChild().firstChild().data
                                clueValue =  int(table.childNodes[i+1].firstChild().firstChild().data.replace('$', '').replace(',',''))
                                #print "wrong: "
                                #print nick
                                #print clueValue
                                nAnswer = Answer()
                                nAnswer.nick = nick
                                nAnswer.correct = 0
                                nAnswer.wager = clueValue
                                nAnswer.turn = turn
                                nClue.answers.append(nAnswer)
                                turn = turn + 1

                    break
                nClue.text = clueText
                nClue.game = self.theGame.id
                nClue.value = clueValue
                nClue.answer = clueAnswer
                nClue.isDD = isDD
                nClue.pickIndex = pickIndex
                self.theGame.categories[-1].clues.append(nClue)


                    
                    


class DBLoader(Thread):

    def __init__(self, queue, tid):
        Thread.__init__(self)
        self.sharedObject = queue
        self.alive = True
        self.tid = tid

    def run(self):
        print "Consumer running: " + str(self.tid)
        dbcon=MySQLdb.connect(host = "localhost", user = "root", passwd = "", db = "j3")
        while self.alive:
            aGame = self.sharedObject.get()
            print str(self.tid) + " started processing a game"
            self.writeGameToDB(aGame, dbcon)
            print str(self.tid) + " done processing a game"
            queue.task_done()
        dbcon.close()

    def stop(self):
        self.alive = False

    def writeGameToDB(self, aGame, dbcon):
        cur = dbcon.cursor()

        for i in range(0,len(aGame.players)):
            cur.execute("INSERT INTO PLAYER (fullName, nick, description) VALUES (%s, %s, %s)", 
                (aGame.players[i].fullName, aGame.players[i].nick, aGame.players[i].description))
            dbcon.commit()
            aGame.players[i].id = cur.lastrowid

        cur.execute("INSERT INTO GAME (jarchiveID, playDate, firstPlayer, firstScore, secondPlayer, secondScore, thirdPlayer, thirdScore) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ", 
                 ( aGame.jarchiveID, aGame.playDate, 
                   aGame.players[0].id, aGame.firstScore, 
                   aGame.players[1].id, aGame.secondScore, 
                   aGame.players[2].id, aGame.thirdScore))

        dbcon.commit()
        aGame.id = cur.lastrowid

        for i in range(0, len(aGame.categories)):
            cur.execute("INSERT INTO CATEGORY (name, game, boardPosition, round) VALUES (%s, %s, %s, %s)", 
                (aGame.categories[i].name, aGame.id, aGame.categories[i].boardPosition, aGame.categories[i].round))
            dbcon.commit()
            aGame.categories[i].id = cur.lastrowid
            for j in range(0, len(aGame.categories[i].clues)):
                clue = aGame.categories[i].clues[j]
                clue.category = aGame.categories[i].id

                cur.execute("INSERT INTO CLUE (text, game, category, value, answer, isDD, pickIndex) "\
                                     " VALUES (%s,    %s,    %s,        %s,     %s,      %s,    %s) ",
                                    (clue.text, aGame.id, clue.category, clue.value, clue.answer, clue.isDD, clue.pickIndex))
                dbcon.commit()
                
                clue.id = cur.lastrowid

                for k in range(0, len(clue.answers)):
                    cur.execute("INSERT INTO ANSWER (player, clue, correct, wager, turn) "\
                        " VALUES (%s,      %s,    %s,       %s,     %s)", 
                        (clue.answers[k].nick, clue.id, clue.answers[k].correct, clue.answers[k].wager, clue.answers[k].wager))

                    dbcon.commit()

if __name__ == "__main__":
    db_path = "db/games.db" 
    queue = Queue()
    consumers = []

    for i in range(0, 10):
        consumers.append(DBLoader(queue, i))
        consumers[i].start()


    for i in range(1, 3576):
    #for i in range(1, 2):
        producer = GameLoader(queue, i)
        producer.start()
        if i % 10 == 0:
           time.sleep(25)

    for i in range(0, 10):
        consumers[i].stop()

