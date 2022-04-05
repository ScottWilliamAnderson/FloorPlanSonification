# import PyOpenAL (will require an OpenAL shared library)
from openal import * 

import pyttsx3

import math

import os
# import the time module, for sleeping during playback
import time

'''
OpenAl uses a right-handed Cartesian coordinate system (RHS), 
where in a frontal default view X (thumb) points right, 
Y (index finger) points up, 
and Z (middle finger) points towards the viewer/camera.

therefore, to match the grid coordinate system of (x,y) (0, 0) in the top-left corner, 
a listener facing north on the grid will have an orientation 
(0, -1, 0, 0, 0, -1)
where 
(frontX, frontY, frontZ, upX, upY, upZ)
'''

class SoundGenerator():
    def __init__(self, grid, openingDict):
        self.grid = grid
        self.openingDict = openingDict
        # default orientation starts facing north
        self.listener = oalGetListener()
        self.listener.orientation = (0.0, -1.0, 0.0, 0.0, 0.0, -1.0)
        
        self.facing = {(0.0, -1.0, 0.0, 0.0, 0.0, -1.0): "North", 
                (1.0, 0.0, 0.0, 0.0, 0.0, -1.0): "East",
                (0.0, 1.0, 0.0, 0.0, 0.0, -1.0): "South",
                (-1.0, 0.0, 0.0, 0.0, 0.0, -1.0): "West"}

        
        # using pyttsx3 to speak the location, using the OS's default voice
        self.engine = pyttsx3.init()
        
        # try and set the voice to an english synthesizer
        voices = self.engine.getProperty('voices')  
        for voice in voices:
            if "English" in voice.name:
                self.engine.setProperty('voice', voice.id)
        # fix volume to match rest of sound stage
        self.engine.setProperty('volume', 0.75)
        
        

    def sayLocation(self, x, y):
        """ say the location, quadrant, orientation of the listener in the room and the tile they are standing on 

        Args:
            x (int): x coordinate of the listener
            y (int): y coordinate of the listener
        """        
        
        
        self.engine.say("You are standing in the " + str(self.findQuadrant(x, y)) + "quadrant of the floorplan, facing " + str(self.facing[self.listener.orientation]))
        self.engine.say("From the top-left corner, you are " + str(y) + " down, and " + str(x) + " across")
        self.engine.say("There is " + str(self.grid.getTileType(x, y)) + " here")
        self.engine.runAndWait()
        
    def sayOrientationChange(self, newOrientation):
        """ say the orientation change of the listener

        Args:
            newOrientation (string): hat direction of the listener in the format e.g. "HatUp.png"
        """        
        facing = {"HatUp.png": "north", "HatDown.png": "south", "HatLeft.png": "west", "HatRight.png": "east"}
        self.engine.say("You are now facing " + str(facing[newOrientation]))
        self.engine.runAndWait()
        
        # function that returns either top-left, top-right, bottom-left, or bottom-right quadrant where the given x,y coordinates are in the grid
    def findQuadrant(self, x, y):
        """ find the quadrant of the given x,y coordinates in the grid

        Args:
            x (int): x coordinate of the listener
            y (int): y coordinate of the listener

        Returns:
            string: the quadrant of the given x,y coordinates in the grid
        """        
        if x < self.grid.getSizeX() / 2 and y < self.grid.getSizeY() / 2:
            return "top-left"
        elif x < self.grid.getSizeX() / 2 and y >= self.grid.getSizeY() / 2:
            return "bottom-left"
        elif x >= self.grid.getSizeX() / 2 and y < self.grid.getSizeY() / 2:
            return "top-right"
        elif x >= self.grid.getSizeX() / 2 and y >= self.grid.getSizeY() / 2:
            return "bottom-right"
        
        
        
    def prepareOpeningSources(self, x, y):
        """ prepare the opening sources for playback 

        Returns:
            listener: the listener object
        """        
        self.listener.move_to((x, y, 0))
        # check listener is within grid boundary
        if 0 <= self.listener.position[0] < self.grid.getSizeX() and 0 <= self.listener.position[0] < self.grid.getSizeY(): 
            openings = self.openingDict.values()
            for opening in openings:
                coords = opening.getLocation()
                # check if the opening is a door or a window as seen from the listener's location
                isDoor = not self.grid.otherSide(int(self.listener.position[0]), int(self.listener.position[1]), int(coords[0]), int(coords[1]), len(opening.getPixels())) == "background"
                if isDoor:
                    # open the mono wave file
                    door = os.path.join(os.getcwd(), "sound", "door.wav")
                # print(test)
                    source = oalOpen(door)
                else:
                    window = os.path.join(os.getcwd(), "sound", "window.wav")
                    source = oalOpen(window)
                
                # increase the sound "dampening" to emulate a real room
                source.set_rolloff_factor(1.0)
                
                # source.set_position(coords)
                source.set_position((coords[0], coords[1], 0))
                opening.setSoundSource(source)
        return self.listener
    
    def getOpeningSources(self, x, y):
        """get the opening sources that are to be played at the given x,y coordinates

        Args:
            x (int): x coordinate of the listener
            y (int): y coordinate of the listener

        Returns:
            list: the opening sources that are to be played at the given x,y coordinates
        """        
        self.sourcesToPlay = []
        self.listener.move_to((x, y, 0))
        for opening in self.openingDict.values():
            coords = opening.getLocation()
            # print(self.distanceToListener(coords[0], coords[1]))
            wallcount = self.grid.getObstructionsInLine(self.grid.pixelsBetweenTwoPoints(x, y, coords[0], coords[1]), opening.getPixels())
            if wallcount < 1:
                self.sourcesToPlay.append(opening)
        return self.sourcesToPlay
        
            
    def playOpeningSources(self, x, y):
        """play the sound sources that the listener wants to hear at their x, y location

        Args:
            x (int): x coordinate of the listener
            y (int): y coordinate of the listener
        """        
        self.getOpeningSources(x, y)
        
        for opening in self.sourcesToPlay:
            player = opening.getSoundSource()
            player.play()
            print("playing " + str(player.position))
            time.sleep(0.1)
            while player.get_state() == AL_PLAYING:
            # wait until the file is done playing
                time.sleep(0.5)
            print("finished playing " + str(player.position))
        time.sleep(0.1)
        
        # release the Openal resources
        try: 
            oalQuit()
        except:
            pass
               
               
    def distanceToListener(self, x, y):
        """calculates the euclidian distance of a given x, y coordinate to the listener

        Args:
            x (int): x coordinate of the location 
            y (int): y coordinate of the location

        Returns:
            float: distance of the x, y coordinate to the listener
        """        
        listenerCoords = self.listener.position
        xDistance = abs(x - listenerCoords[0])
        yDistance = abs(y - listenerCoords[1])
        distance = math.sqrt((xDistance * xDistance) + (yDistance * yDistance))
        return distance
    
    def getListener(self):
        """getter function for the listener object

        Returns:
            listener: listener object
        """        
        return self.listener
            
        
    def quit(self):
        """ release resources (don't forget to use this)
        """        
        oalQuit()
    

if __name__ == "__main__":
    pass
        