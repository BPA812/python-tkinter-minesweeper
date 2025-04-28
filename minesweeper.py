# Python Version 2.7.3
# File: minesweeper.py

from tkinter import *
from tkinter import messagebox as tkMessageBox
from collections import deque
import random, platform, time
from datetime import time, date, datetime
SX,SY = 10,10
STATE_DEFAULT,STATE_CLICKED,STATE_FLAGGED = 0,1,2
BTN_CLICK,BTN_FLAG,window = "<Button-1>","<Button-2>" if platform.system() == 'Darwin' else "<Button-3>",None
class Minesweeper:
    def __init__(self, tk):
        self.images = {
            "plain": PhotoImage(file = "images/tile_plain.gif"),
            "clicked": PhotoImage(file = "images/tile_clicked.gif"),
            "mine": PhotoImage(file = "images/tile_mine.gif"),
            "flag": PhotoImage(file = "images/tile_flag.gif"),
            "wrong": PhotoImage(file = "images/tile_wrong.gif"),
            "numbers": []
        }
        for i in range(1, 9):
            self.images["numbers"].append(PhotoImage(file = "images/tile_"+str(i)+".gif"))
        self.tk = tk
        self.frame = Frame(self.tk)
        self.frame.pack()
        self.labels = {
            "time": Label(self.frame, text = "00:00:00"),
            "mines": Label(self.frame, text = "Mines: 0"),
            "flags": Label(self.frame, text = "Flags: 0")
        }
        self.labels["time"].grid(row = 0, column = 0, columnspan = SY)
        self.labels["mines"].grid(row = SX+1, column = 0, columnspan = int(SY/2))
        self.labels["flags"].grid(row = SX+1, column = int(SY/2)-1, columnspan = int(SY/2))
        self.restart()
        self.updateTimer()

    def setup(self):
        self.flagCount,self.correctFlagCount,self.clickedCount = 0,0,0
        self.startTime = None
        self.tiles = dict({})
        self.mines = 0
        for x in range(0, SX):
            for y in range(0, SY):
                if y == 0:
                    self.tiles[x] = {}
                id = str(x) + "_" + str(y)
                isMine = False
                gfx = self.images["plain"]
                if random.uniform(0.0, 1.0) < 0.1:
                    isMine = True
                    self.mines += 1
                tile = {
                    "id": id,
                    "isMine": isMine,
                    "state": STATE_DEFAULT,
                    "coords": {
                        "x": x,
                        "y": y
                    },
                    "button": Button(self.frame, image = gfx),
                    "mines": 0
                }
                tile["button"].bind(BTN_CLICK, self.onClickWrapper(x, y))
                tile["button"].bind(BTN_FLAG, self.onRightClickWrapper(x, y))
                tile["button"].grid( row = x+1, column = y )
                self.tiles[x][y] = tile
        for x in range(0, SX):
            for y in range(0, SY):
                mc = 0
                for n in self.getNeighbors(x, y):
                    mc += 1 if n["isMine"] else 0
                self.tiles[x][y]["mines"] = mc
    def restart(self):
        self.setup()
        self.refreshLabels()
    def refreshLabels(self):
        self.labels["flags"].config(text = "Flags: "+str(self.flagCount))
        self.labels["mines"].config(text = "Mines: "+str(self.mines))
    def gameOver(self, won):
        for x in range(0, SX):
            for y in range(0, SY):
                if self.tiles[x][y]["isMine"] == False and self.tiles[x][y]["state"] == STATE_FLAGGED:
                    self.tiles[x][y]["button"].config(image = self.images["wrong"])
                if self.tiles[x][y]["isMine"] == True and self.tiles[x][y]["state"] != STATE_FLAGGED:
                    self.tiles[x][y]["button"].config(image = self.images["mine"])
        self.tk.update()
        m = "You Win! Play again?" if won else "You Lose! Play again?"
        r = tkMessageBox.askyesno("Game Over", m)
        if r:
            self.restart()
        else:
            self.tk.quit()
    def updateTimer(self):
        ts = "00:00:00"
        if self.startTime != None:
            delta = datetime.now() - self.startTime
            ts = str(delta).split('.')[0] # drop ms
            if delta.total_seconds() < 36000:
                ts = "0" + ts # zero-pad
        self.labels["time"].config(text = ts)
        self.frame.after(100, self.updateTimer)
    def getNeighbors(self, x, y):
        neighbors = []
        coords = [
            {"x": x-1,  "y": y-1}, 
            {"x": x-1,  "y": y},
            {"x": x-1,  "y": y+1},
            {"x": x,    "y": y-1},
            {"x": x,    "y": y+1},
            {"x": x+1,  "y": y-1},
            {"x": x+1,  "y": y},
            {"x": x+1,  "y": y+1},
        ]
        for n in coords:
            try:
                neighbors.append(self.tiles[n["x"]][n["y"]])
            except kError:
                pass
        return neighbors
    def onClickWrapper(self, x, y):
        return lambda Button: self.onClick(self.tiles[x][y])
    def onRightClickWrapper(self, x, y):
        return lambda Button: self.onRightClick(self.tiles[x][y])
    def onClick(self, tile):
        if self.startTime == None:
            self.startTime = datetime.now()
        if tile["isMine"] == True:
            self.gameOver(False)
            return
        if tile["mines"] == 0:
            tile["button"].config(image = self.images["clicked"])
            self.clearSurroundingTiles(tile["id"])
        else:
            tile["button"].config(image = self.images["numbers"][tile["mines"]-1])
        if tile["state"] != STATE_CLICKED:
            tile["state"] = STATE_CLICKED
            self.clickedCount += 1
        if self.clickedCount == (SX * SY) - self.mines:
            self.gameOver(True)
    def onRightClick(self, tile):
        if self.startTime == None:
            self.startTime = datetime.now()
        if tile["state"] == STATE_DEFAULT:
            tile["button"].config(image = self.images["flag"])
            tile["state"] = STATE_FLAGGED
            tile["button"].unbind(BTN_CLICK)
            if tile["isMine"] == True:
                self.correctFlagCount += 1
            self.flagCount += 1
            self.refreshLabels()
        elif tile["state"] == 2:
            tile["button"].config(image = self.images["plain"])
            tile["state"] = 0
            tile["button"].bind(BTN_CLICK, self.onClickWrapper(tile["coords"]["x"], tile["coords"]["y"]))
            if tile["isMine"] == True:
                self.correctFlagCount -= 1
            self.flagCount -= 1
            self.refreshLabels()
    def clearSurroundingTiles(self, id):
        q = deque([id])
        while len(q) != 0:
            k = q.popleft()
            p = k.split("_")
            x = int(p[0])
            y = int(p[1])
            for tile in self.getNeighbors(x, y):
                self.clearTile(tile, q)
    def clearTile(self, tile, q):
        if tile["state"] != STATE_DEFAULT:
            return
        if tile["mines"] == 0:
            tile["button"].config(image = self.images["clicked"])
            q.append(tile["id"])
        else:
            tile["button"].config(image = self.images["numbers"][tile["mines"]-1])
        tile["state"] = STATE_CLICKED
        self.clickedCount += 1
def main():
    window = Tk()
    window.title("Minesweeper")
    minesweeper = Minesweeper(window)
    window.mainloop()
if __name__ == "__main__":
    main()