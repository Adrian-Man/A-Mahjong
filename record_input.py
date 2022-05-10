from xmlrpc.client import NOT_WELLFORMED_ERROR
import pandas as pd
import time

class input_record:
    #new game setup
    def __init__(self,initEast,initSouth,initWest,initNorth,currRound,currHand): #create a record
        self.data = {
                        'round':[], #圈
                        'hand':[], #局
                        'contDealer':[], #連續做莊
                        'dealer':[], #莊
                        'initEast':[],
                        'initSouth':[],
                        'initWest':[],
                        'initNorth':[],
                        'east':[],
                        'south':[],
                        'west':[],
                        'north':[],
                        'time':[],
                        'dice':[],
                        'eastFlower':[], #no. of flower for each player
                        'southFlower':[],
                        'westFlower':[],
                        'northFlower':[],
                        'eastScore':[],
                        'southScore':[],
                        'westScore':[],
                        'northScore':[],
                        'winner':[],
                        'points':[], #番
                        'loserPos':[], 
                        'loser':[],
                        'selfDrawn':[] #自摸
                    } #data to be saved
        self.players = [initEast,initSouth,initWest,initNorth]
        self.pos ={'currEast':initEast,'currSouth':initSouth,'currWest':initWest,'currNorth':initNorth}
        self.score = {initEast:0,initSouth:0,initWest:0,initNorth:0} #player scoreboard
        self.currRound = int(currRound)
        self.currHand = int(currHand)
        self.currContDealer = 0
        self.scoreList = {3:8,4:16,5:24,6:32,7:48,8:64,9:96,10:128}
        self.inProgress = True
        self.df = pd.DataFrame(self.data)
        self.date = time.localtime(time.time())
        self.file = 'records/'+str(self.date.tm_year)+str(self.date.tm_mon)+str(self.date.tm_mday)+str(self.date.tm_hour)+str(self.date.tm_min)+'.csv' #create file
                
    def pre_game(self,**args):
        if args['replace']=='y': #change player info
            for player in self.players:
                if player not in self.score.keys():
                    self.score[player] = 0

        self.pos['currEast'] = self.players[((self.currHand-1)%4)] #calculate current position
        self.pos['currSouth'] = self.players[((self.currHand)%4)]
        self.pos['currWest'] = self.players[((self.currHand+1)%4)]
        self.pos['currNorth'] = self.players[((self.currHand+2)%4)]

        self.data['round'].append(self.currRound) #update data
        self.data['hand'].append(self.currHand)
        self.data['contDealer'].append(self.currContDealer)
        self.data['dealer'].append(self.pos['currEast'])
        self.data['initEast'].append(self.players[0])
        self.data['initSouth'].append(self.players[1])
        self.data['initWest'].append(self.players[2])
        self.data['initNorth'].append(self.players[3])
        self.data['east'].append(self.pos['currEast'])
        self.data['south'].append(self.pos['currSouth'])
        self.data['west'].append(self.pos['currWest'])
        self.data['north'].append(self.pos['currNorth'])
        self.data['time'].append(self.get_time())
        self.data['dice'].append(args['dice'])
        self.data['eastFlower'].append(int(args['flowers'][0]))
        self.data['southFlower'].append(int(args['flowers'][1]))
        self.data['westFlower'].append(int(args['flowers'][2]))
        self.data['northFlower'].append(int(args['flowers'][3]))

    def post_game(self,**args):
        self.data['winner'].append(args['winner'])
        if args['winner']==self.pos['currEast']: #if dealer win
            self.currContDealer += 1
        else:
            self.currContDealer = 0
        self.data['points'].append(args['points'])
        if args['loser']=='none': #find the loser
            self.data['loserPos'].append(args['loser'])
        else:
            self.data['loserPos'].append(self.inverse_dict(self.pos)[args['loser']][4:])
        self.data['loser'].append(args['loser'])
        self.data['selfDrawn'].append(args['selfDrawn'])

        if args['winner']!='none': #update scores
            if args['selfDrawn']==True:
                if args['loser']=='none': #self drawn
                    temPlayers = self.players.copy()
                    winner = args['winner']
                    temPlayers.remove(winner)
                    self.score[winner] += 1.5*self.scoreList[args['points']]
                    for loser in temPlayers:
                        self.score[loser] -= 0.5*self.scoreList[args['points']]
                else: #someone responsible for the self drawn
                    winner = args['winner']
                    self.score[winner] += 1.5*self.scoreList[args['points']]
                    self.score[args['loser']] -= 1.5*self.scoreList[args['points']]
            else: #someone wins
                self.score[args['winner']] += self.scoreList[args['points']]
                self.score[args['loser']] -= self.scoreList[args['points']]

        self.data['eastScore'].append(self.score[self.pos['currEast']])
        self.data['southScore'].append(self.score[self.pos['currSouth']])
        self.data['westScore'].append(self.score[self.pos['currWest']])
        self.data['northScore'].append(self.score[self.pos['currNorth']])

        if self.currRound==4 and self.currHand==4: #game ended
            self.inProgress = False

        if self.currContDealer==0: #if the dealer did not win
            self.currHand += 1
            if self.currHand>4: #one round ended
                self.currHand = 1
                self.currRound += 1

    def get_time(self):
        now = time.time()
        day = time.localtime(now).tm_wday
        hour = time.localtime(now).tm_hour
        min = time.localtime(now).tm_min
        return ((day)*24*60+hour*60+min)

    def complete(self):
        self.df = pd.DataFrame(self.data)
        self.df.to_csv(self.file)
        print(self.score)

    def manual(self):
        while self.inProgress==True:
            replace = input("Is there any change of player? 'y' for yes, 'n' for no: ")
            if replace=='y': #change player info
                players = input('Please enter the four players in the order of "Init East","Init South","Init West","Init North": ')
                while True:
                    try:
                        self.players = players.split(',')
                        t = players[0]
                        t = players[1]
                        t = players[2]
                        t = players[3]
                        break
                    except:
                        players = input('Please enter the four players in the order of "Init East","Init South","Init West","Init North": ')
            dice = input("Please enter the sum of the three dice: ")
            while True:
                try:
                    dice = int(dice)
                    break
                except:
                    dice = input("Please enter the sum of the three dice: ")
            flowers = input("Please enter the number of flowers for each player in the order of 'east','south','west','north': ")
            while True:
                try:
                    flowers = flowers.split(',')
                    t = flowers[0]
                    t = flowers[1]
                    t = flowers[2]
                    t = flowers[3]
                    break
                except:
                    flowers = input("Please enter the number of flowers for each player in the order of 'east','south','west','north': ")
            self.pre_game(replace=replace,dice=dice,flowers=flowers)
            winner = input("Who is the winner? Type 'none' if no one wins: ")
            if winner=='none':
                points = 0
                loser = 'none'
                selfDrawn = False
            else:
                points = int(input("What is the point for the winner? "))
                selfDrawn = input("Is it a self-drawn? 'y' for yes, 'n' for no: ")
                if selfDrawn=='y':
                    selfDrawn = True
                elif selfDrawn=='n':
                    selfDrawn = False
                loser = input("Who is the loser? type 'none' if no one lose or someone seld-drawn: ")
            self.post_game(winner=winner,points=points,loser=loser,selfDrawn=selfDrawn)
            complete = input('Is the game ended? "y" for yes, "n" for no: ')
            self.complete()
            if complete=='y':
                self.inProgress = False

    def inverse_dict(self,dict):
        newDict = {val:key for key,val in dict.items()}
        return newDict

if __name__=='__main__':
    players = input('Please enter the four players in the order of "Init East","Init South","Init West","Init North": ')
    while True:
        try:
            players = players.split(',')
            t = players[0]
            t = players[1]
            t = players[2]
            t = players[3]
            break
        except:
            players = input('Please enter the four players in the order of "Init East","Init South","Init West","Init North": ')
    gameIndex = input('Please enter the initial round and hand in the order of "Round","Hand": ')
    while True:
        try:
            gameIndex = gameIndex.split(',')
            t = gameIndex[0]
            t = gameIndex[1]
            break
        except:
            gameIndex = input('Please enter the initial round and hand in the order of "Round","Hand": ')
    record = input_record(players[0],players[1],players[2],players[3],gameIndex[0],gameIndex[1])
    record.manual()