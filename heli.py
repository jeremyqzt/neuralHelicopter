# Imports each and every method and class
# of module tkinter and tkinter.ttk

#https://keras.io/getting-started/sequential-model-guide/

from tkinter import *
from tkinter.ttk import *
import random
import time
import keras
import random
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
import numpy as np
        
class game:
    def __init__(self, generations=1, compPlayers=10):
        self.generation = generations
        self.compPlayers = compPlayers
    def loop(self):
        nextGen = []
        for i in range(0, self.generation):
            self.startGame(nextGen)
            mainloop()

            #Iteration Done
            #Don't worry about human score
            scores = self.gameMap.finalScore[1:]
            comps = self.gameMap.comps[1:]

            #Tear Down old map
            #self.master.destroy()
            #del self.master
            #del self.gameMap
            self.master.destroy() #destroys the canvas and therefore all of its child-widgets too
            #canvas = Canvas(master)
            #canvas.pack()

            #Evolve
            nextGen = geneticAlgo(comps, scores).getNextGen()

    def startGame(self, nextGen):
        self.master = Tk()
        if nextGen == []:
            for i in range(0, self.compPlayers):
                nextGen.append(computerPlayer())
        self.gameMap = gameMap(self.master, 1 + self.compPlayers, nextGen)
        self.master.title("Helicopter - Evolution")
        self.master.geometry("900x300")


class geneticAlgo:
    evolveRate = 0.05
    def __init__(self, comp, score):
        self.comps = comp
        self.scores = score
        self.nextGenCount = len(score)

    def evolve(self):
        self.select()
        self.cross()
        self.mutate()

    def getNextGen(self):
        self.evolve()
        return self.comps
    def mixArrays(self, array1, array2):
        ret = np.empty(array1.shape)
        for i in range(len(array1)):
            for t in range(len(array1[i])):
                pick = random.randint(-5,5)
                if pick == 0:
                    ret[i][t] = array1[i][t] + self.evolveRate * pick
                else:
                    ret[i][t] = array2[i][t] + self.evolveRate * pick

        return ret    
    #Keep 2 best
    def select(self):
        self.best = self.scores.index(max(self.scores))
        self.secondBest = self.scores.index(sorted(self.scores)[-2])

        self.bestModel = np.array(self.comps[self.best].model.get_weights())
        self.comps[self.best].model.save_weights("./models/score-%d" % (self.scores[self.best]))
        self.secondBestModel = np.array(self.comps[self.best].model.get_weights())


    #Cross Breeding occupies 80% (Averages between best and second)
    def cross(self):
        for i in range(0, len(self.comps)):
            if i != self.best and i != self.secondBest:
                t = self.comps[i].model.get_weights()
                for w in range(0, len(t),2):
                    t[w] = self.mixArrays(self.bestModel[w], self.secondBestModel[w])
                self.comps[i].model.set_weights(t)               
            
    def randomize(self, array1):
        ret = np.empty(array1.shape)
        for i in range(len(array1)):
            for t in range(len(array1[i])):
                ret[i][t] = array1[i][t] * random.uniform(-1, 1)

        return ret             
            
    #Mutations occupies 25%
    def mutate(self):
        for i in range(0, len(self.comps)):
            value = random.randint(0, 3)
            if value != 1:
                continue
            t = self.comps[i].model.get_weights()
            for w in range(0, len(t),2):
                t[w] = self.randomize(t[w])
            self.comps[i].model.set_weights(t)      


class computerPlayer:
    def __init__(self):
        self.model = Sequential()
        self.model.add(Dense(16, activation='relu', input_dim=4))
        self.model.add(Dense(32, activation='relu'))
        self.model.add(Dense(1, activation='sigmoid'))

        self.model.compile(loss='binary_crossentropy',
                      optimizer='rmsprop',
                      metrics=['accuracy'])

    def getModel(self):
        return np.array(self.model.get_weights())

    def setModel(self, weights):
        self.model.set_weights(weights)

    def getMove(self, inVal):
        return self.model.predict_classes(np.array([inVal]))

class gameMap:
    bottomY = 290
    topY = 10
    obsHeight = 60
    nearestOb = 0
    obWidth = 10
    def __init__(self, master, playerCount, comps):
        self.master = master
        #Human always player 0
        self.comps = [None] + comps
        self.scoreTotal = 0
        self.v = [0]*playerCount
        self.a = [0]*playerCount
        self.finalScore = [0]*playerCount
        self.over = [False]*playerCount

        self.master.bind("<Up>", self.getEvnt)
        self.createGame(playerCount)

    def getEvnt(self, other):
        self.jumpVal(0)
 
    def jumpVal(self, index):
        self.v[index] = -1.85
        self.a[index] = 0

    def createGame(self, playerCount):
        self.canvas = Canvas(self.master)
        self.players= []
        self.canvas.create_rectangle(0, 0, 900, self.topY, fill = "green")
        self.canvas.create_rectangle(0, self.bottomY, 900, 300, fill = "green")
        self.score =  self.canvas.create_text((1, 11), text="Score: 0", anchor = "nw")
        self.createObstacle()
        human = True
        for i in range(0, playerCount):
            #Create 1 human player with different color
            player = self.createPlayer(10, 145, 5, human)
            self.players.append(player)
            human = False

        self.canvas.pack(fill = BOTH, expand = 1)
        self.periodic()

    def createObstacle(self, diff = 6):
        self.obs = []
        start = 500
        off = 900/diff
        for i in range(0, diff):
            rand = random.randint(self.topY + self.obsHeight + 90 ,self.bottomY - self.obsHeight)
            self.obs.append(self.canvas.create_rectangle(start + i*off, rand, start + self.obWidth + i*off, rand + self.obsHeight, fill = "green"))

    def createPlayer(self,x,y,r,human):
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        if human:
            return self.canvas.create_oval(x0, y0, x1, y1, fill="blue")
        else:
            return self.canvas.create_oval(x0, y0, x1, y1, fill="red")
    def moveObs(self):
        for i in range(0, len(self.obs)):
            ob = self.obs[i]
            self.canvas.move(ob, -3, 0)
            if self.canvas.coords(ob)[2] < 0:
                new = random.randint(self.topY + 90 ,self.bottomY - self.obsHeight)
                tup = (900, new, 910, new + self.obsHeight)
                self.canvas.coords(ob, tup)

    def periodic(self):
        period = 10
        self.scoreTotal += 1
        self.canvas.itemconfig(self.score, text=("Score: %d" % self.scoreTotal))
        self.moveObs()
        for i in range(0, len(self.players)):
            if self.over[i] == True:
                continue
            
            t = self.players[i]

            obsArr = []
            closestObs = None
            minX = 9999
            #Find cloest Obs
            for u in self.obs:
                closeCord = self.canvas.coords(u)
                if ((closeCord[0] > self.obWidth) and (closeCord[0] < minX)):
                    minX = closeCord[1]
                    closestObs = closeCord
                    
                obsArr.append(self.canvas.coords(u))
            
            #[x dist to next, y dist to next,
            #x dist to next bottom, y dist to next bottom,
            #dist to top, dist to bottom,
            #velocity, acceleration]
            cord = self.canvas.coords(t)

            centX = 10 # cant move sideways
            centY = cord[1] + 5
            inp = []
            #for y in obsArr:
            #    inp.append(self.buildLOS(centY, y))
            #    xRatio = (y[1] - centX) / 900
            #    inp.append(xRatio)

            #print(cord)
            inp.append(self.buildLOS(centY, closestObs))
            #print(closestObs)
            xRatio = (closestObs[0] - centX) / 900
            #print(xRatio)
            inp.append(xRatio)

            #Y grows going down
            dTop = (centY - self.topY) / 900
            dBottom = (self.bottomY - centY) / 900

            #inp.append((centY/(self.topY + self.bottomY)) * 2 - 1)
            inp.append(dTop)
            inp.append(dBottom)
            #inp.append((self.a[i]/2) * 2 -1)
            #inp.append((self.v[i]/2) * 2 -1)
            
            #print(inp)

            if i != 0:
                if (self.comps[i].getMove(inp) == 1):
                    self.jumpVal(i)

            self.canvas.move(t, 0, self.v[i])
            self.a[i] +=0.002
            self.v[i] += self.a[i]

            if self.checkCollissionBorders(cord):
                self.finalScore[i] = self.scoreTotal
                self.over[i] = True
                self.canvas.delete(t)
            if self.checkCollissionOb(cord, obsArr):
                self.finalScore[i] = self.scoreTotal
                self.over[i] = True
                self.canvas.delete(t)

        #Atleast 1 player, schedule next round
        if False in self.over:
            self.master.after(period, self.periodic)
        else:
            self.master.quit()

    #1 if in LOS of obstacle
    def buildLOS(self, heli, obs):
        if (heli >obs[1] and heli < obs[3]):
            return 1
        #centObs = (obs[1] + obs[3]) /2 
        #furthest = 200
        #dist = ((abs(heli - centObs)/furthest)* 2) - 1
        return 0

    def checkCollissionBorders(self, cord):
        if cord[1] <= self.topY or cord[3] > self.bottomY:
            return True
        return False

    def checkCollissionOb(self, cord, obs):
        for cordOb in obs:
            if cord[3] > cordOb[1] and cord[1] < cordOb[3]:
                if cordOb[0] < 10:
                    return True
        return False



if __name__ == "__main__":
    t = game(50, 20)
    t.loop()

