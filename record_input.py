from xmlrpc.client import NOT_WELLFORMED_ERROR
import pandas as pd
import time

class input_record:
    #new game setup
    def __init__(self,initEast,initSouth,initWest,initNorth):
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
        self.currRound = 1
        self.currHand = 0
        self.currContDealer = 0
        self.scoreList = {3:8,4:16,5:24,6:32,7:48,8:64,9:96,10:128}
        self.inProgress = True
                
    def pre_game(self,**args):
        if args['replace']==True: #change player info
            for player in self.players:
                if player not in self.score:
                    self.score[player] = 0

        if self.currContDealer==0: #if the dealer did not win
            self.currHand += 1
            if self.currHand>4: #if one round ended
                self.currHand = self.currHand%4+1
                self.currRound += 1

        self.pos['currEast'] = self.players[(self.currHand-1)%4] #calculate curren position
        self.pos['currSouth'] = self.players[(self.currHand)%4]
        self.pos['currWest'] = self.players[(self.currHand+1)%4]
        self.pos['currNorth'] = self.players[(self.currHand+2)%4]

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
        self.data['eastFlower'].append(args['flowers'][0])
        self.data['southFlower'].append(args['flowers'][1])
        self.data['westFlower'].append(args['flowers'][2])
        self.data['northFlower'].append(args['flowers'][3])

    def post_game(self,**args):
        self.data['winner'].append(args['winner'])
        if args['winner']==self.pos['currEast']: #if dealer win
            self.currContDealer += 1
        else:
            self.currContDealer = 0
        self.data['points'].append(args['points']) # update data
        if args['loser']=='none':
            self.data['loserPos'].append(args['loser'])
        else:
            self.data['loserPos'].append(self.inverse_dict(self.pos)[args['loser']][4:])
        self.data['loser'].append(args['loser'])
        self.data['selfDrawn'].append(args['selfDrawn'])

        if args['winner']!='none': #update scores
            if args['selfDrawn']==True:
                temPlayers = self.players
                winner = args['winner']
                temPlayers.remove(winner)
                self.score[winner] += 1.5*self.scoreList[args['points']]
                for loser in temPlayers:
                    self.score[loser] -= 0.5*self.scoreList[args['points']]
            else:
                self.score[args['winner']] += self.scoreList[args['points']]
                self.score[args['loser']] -= self.scoreList[args['points']]

        self.data['eastScore'].append(self.score[self.pos['currEast']])
        self.data['southScore'].append(self.score[self.pos['currSouth']])
        self.data['westScore'].append(self.score[self.pos['currWest']])
        self.data['northScore'].append(self.score[self.pos['currNorth']])

        if self.currRound==4 and self.currHand==4:
            self.inProgress = False
            self.complete()

    def get_time(self):
        now = time.time()
        day = time.localtime(now).tm_wday
        hour = time.localtime(now).tm_hour
        min = time.localtime(now).tm_min
        return ((day)*24*60+hour*60+min)

    def complete(self):
        df = pd.DataFrame(self.data)
        date = time.localtime(time.time())
        df.to_csv('records/'+str(date.tm_year)+str(date.tm_mon)+str(date.tm_mday)+str(date.tm_hour)+str(date.tm_min)+'.csv')
        self.inProgress = False
        print(self.score)

    def manual(self):
        while self.inProgress==True:
            replace = input("Is there any change of player? 'y' for yes, 'n' for no: ")
            if replace=='y': #change player info
                players = input('Please enter the four players in the order of "Init East","Init South","Init West","Init North": ')
                self.players = players.split(',')
            dice = int(input("Please enter the sum of the three dice: "))
            flowers = input("Please enter the number of flowers for each player in the order of 'east','south','west','north': ")
            flowers = flowers.split(',')
            self.pre_game(replace=replace,dice=dice,flowers=flowers)
            winner = input("Who is the winner? Type 'none' if no one wins: ")
            points = int(input("What is the point for the winner? Type 0 if no one wins: "))
            loser = input("Which position is the loser? type 'none if no one lose or someone seld-drawn: ")
            selfDrawn = input("Is it a self-drawn? 'y' for yes, 'n' for no: ")
            if selfDrawn=='y':
                selfDrawn = True
            elif selfDrawn=='n':
                selfDrawn = False
            self.post_game(winner=winner,points=points,loser=loser,selfDrawn=selfDrawn)
            complete = input('Is the game ended? "y" for yes, "n" for no: ')
            if complete=='y':
                self.complete()

    def inverse_dict(self,dict):
        newDict ={}
        for key,val in dict.items():
            newDict[val]=key
        return newDict

if __name__=='__main__':
    players = input('Please enter the four players in the order of "Init East","Init South","Init West","Init North": ')
    players = players.split(',')
    record = input_record(players[0],players[1],players[2],players[3])
    record.manual()