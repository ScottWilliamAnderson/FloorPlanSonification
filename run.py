from math import floor
from tkinter.ttk import Progressbar
from map import mapGenerator
from sound import *
from PIL import ImageTk,Image
import tkinter as tk
from tkinter import filedialog
import demo as m

class Gui():
    
    def __init__(self):
        self.facing = {(0.0, -1.0, 0.0, 0.0, 0.0, -1.0): "HatUp.png", 
                (1.0, 0.0, 0.0, 0.0, 0.0, -1.0): "HatRight.png",
                (0.0, 1.0, 0.0, 0.0, 0.0, -1.0): "HatDown.png",
                (-1.0, 0.0, 0.0, 0.0, 0.0, -1.0): "HatLeft.png"}
        
        self.orientations = {v: k for k, v in self.facing.items()}
        self.hatOrientation = "HatUp.png"
        self.startup()
        
    def rotateHat(self, hat, buttonPressed):
        """sets and returns the new hat after rotating it

        Args:
            hat (string): the hat icon representing the direction faced (e.g. "HatUp.png")
            buttonPressed (string): "e" if rotating clockwise, "q" if rotating counterclockwise
            
        Returns:
            newHat (string): the hat icon representing the new direction the hat is facing (e.g. "HatRight.png")
        """
        print("rotating hat")
        
        if buttonPressed == "e":
            if hat == "HatLeft.png":
                newHat = "HatUp.png"
            elif hat == "HatUp.png":
                newHat = "HatRight.png"
            elif hat == "HatRight.png":
                newHat = "HatDown.png"
            elif hat == "HatDown.png":
                newHat = "HatLeft.png"
        elif buttonPressed == "q":
            if hat == "HatLeft.png":
                newHat = "HatDown.png"
            elif hat == "HatUp.png":
                newHat = "HatLeft.png"
            elif hat == "HatRight.png":
                newHat = "HatUp.png"
            elif hat == "HatDown.png":
                newHat = "HatRight.png"
                
        self.hatOrientation = newHat
        self.audio.listener.orientation = self.orientations[self.hatOrientation]
        self.audio.sayOrientationChange(newHat)
        
        
    def quit(self):
        """shut down the software
        """        
        self.root.destroy()
        sys.exit(0)

    def startup(self):
        """starts up the GUI, loads the buttons and waits for the user's choice
        """        
        self.root = tk.Tk()  
        self.root.title('Deep Floor Plan Sonification')
        self.root.bind("<Escape>", lambda x: self.quit())
        self.root.attributes('-fullscreen', True)  
        self.canvas = tk.Canvas(self.root, bg='white', highlightthickness=0)
        # canvas fills the whole window
        self.uploadButton = tk.Button(self.canvas, text='Upload a Floor Plan', bg='white', font=('arial', 20, 'bold'), command=self.uploadFloorPlan)
        self.uploadButton.place(relx=0.4, rely=0.5, anchor=tk.CENTER)
        
        self.useExampleButton = tk.Button(self.canvas, text='Use Example Floor Plan', bg='white', font=('arial', 20, 'bold'), command=self.useExample)
        self.useExampleButton.place(relx=0.6, rely=0.5, anchor=tk.CENTER)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.update()
        self.root.mainloop() 
        
    def useExample(self):
        """called when the user clicks on the use example button, and loads the example floor plan
        """        
        print('clicked example Floor Plan')
        self.canvas.destroy()
        self.root.update()
        self.exampleGui()
        
    def uploadFloorPlan(self):
        """called when the user clicks on the upload button, and loads the upload file tool
            once the floor plan is uploaded, the DeepFloorPlan model is run with the provided image as input
            the result is saved, and the uploadedGui method is called to display it
        """        
        print('clicked upload Floor Plan')
        # root.withdraw()

        self.floorPlanPath=filedialog.askopenfilename(filetypes=[("JPG file", "*.jpg"), ("JPEG file", "*.jpeg")])
        self.canvas.destroy()
        self.root.update()
        
        self.canvas = tk.Canvas(self.root, bg='white', highlightthickness=0)
        running = self.canvas.create_text(self.root.winfo_width()/2, self.root.winfo_height()/2, text="Running Model...", font=('arial', 20, 'bold'))
        timed = self.canvas.create_text(self.root.winfo_width()/2, (self.root.winfo_height()/9) * 5, text="Average expected runtime: 25 seconds", font=('arial', 10, 'italic'))
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.update()
        m.main(self.floorPlanPath)
        self.prepareUploadedSoundStage()
        self.canvas.destroy()
        self.uploadedGui()
        
    def uploadedGui(self):
        """loads the GUI for the uploaded floor plan after it has been processed and sets the keybindings
        """        
        self.canvas = tk.Canvas(self.root, bg='white', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        mapDir = os.path.join(os.getcwd(), "map", "saved.png")
        img = Image.open(mapDir)
        fullscreenImg = ImageTk.PhotoImage(self.resize_PIL(img, min(int(self.root.winfo_height()), int(self.root.winfo_width()/2))))
        self.canvas.create_image(0, 0, image=fullscreenImg, anchor="nw") 
        
        global scale
        scale = fullscreenImg.width()/img.size[0]
        
        original = Image.open(self.floorPlanPath)
        originalImage = ImageTk.PhotoImage(self.resize_PIL(original, min(int(self.root.winfo_height()), int(self.root.winfo_width()/2))))
        reference = self.canvas.create_image(self.root.winfo_width(), self.root.winfo_height(), image=originalImage, anchor="se")
        self.canvas.tag_raise(reference)
        
        self.canvas.bind("<Button-1>", self.mouseClick)
        self.root.bind('q', self.rotateCounterClockwise)
        self.root.bind('e', self.rotateClockwise)
        self.canvas.update()
        self.root.mainloop()
        
    def rotateCounterClockwise(self, event):
        """rotates the hat/user orientation counterclockwise

        Args:
            event (event): the click event
        """        
        print("rotate counterclockwise")
        self.rotateHat(self.hatOrientation, "q")
        self.audio.sayOrientationChange(self.hatOrientation)
        
    def rotateClockwise(self, event):
        """rotates the hat/user orientation clockwise

        Args:
            event (event): the click event
        """        
        print("rotate clockwise")
        self.rotateHat(self.hatOrientation, "e")
        

    def exampleGui(self):
        """loads the GUI for the example floor plan and sets the keybindings
        """        
        self.prepareExampleSoundStage()
        self.canvas = tk.Canvas(self.root, bg='white', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        mapDir = os.path.join(os.getcwd(), "map", "example.png")
        img = Image.open(mapDir)
        fullscreenImg = ImageTk.PhotoImage(self.resize_PIL(img, min(int(self.root.winfo_height()), int(self.root.winfo_width()/2))))
        self.canvas.create_image(0, 0, image=fullscreenImg, anchor="nw") 
        self.canvas.bind("<Button-1>", self.mouseClick)
        self.root.bind('q', self.rotateCounterClockwise)
        self.root.bind('e', self.rotateClockwise)
        
        global scale
        scale = fullscreenImg.width()/img.size[0]
        
        
        originalDir = os.path.join(os.getcwd(), "demo", "exampleSquare.jpg")
        original = Image.open(originalDir)
        originalImage = ImageTk.PhotoImage(self.resize_PIL(original, min(int(self.root.winfo_height()), int(self.root.winfo_width()/2))))
        reference = self.canvas.create_image(self.root.winfo_width(), self.root.winfo_height(), image=originalImage, anchor="se")
        self.canvas.tag_raise(reference)
        self.canvas.update()
        self.root.mainloop() 
        
    def loadHat(self, event):
        """loads the hat icon in the location of the click and returns the hat tkinter image object

        Args:
            event (event): the click event

        Returns:
            hat (tkinter image object): the hat image
        """        
        print("preparing opening sources")
        self.listener = self.audio.prepareOpeningSources(math.floor(event.x / scale), math.floor(event.y / scale))
        print("listener position: " + str(self.listener.position))
        print(self.listener.get(AL_ORIENTATION))
        try:
            self.facing[self.listener.get(AL_ORIENTATION)]
        except:
            self.listener.set_orientation(self.orientations[self.hatOrientation])
            
        hatDir = Image.open(os.path.join(os.getcwd(), "map", self.hatOrientation))
        if self.facing[self.listener.get(AL_ORIENTATION)] == "HatUp.png" or self.facing[self.listener.get(AL_ORIENTATION)] == "HatDown.png":
            hatWidth = 30
            ratio = (hatWidth / float(hatDir.size[0]))
            hatHeight = int((float(hatDir.size[1]) * float(ratio)))
            hatIcon = ImageTk.PhotoImage(hatDir.resize((hatWidth,hatHeight)))
        else:
            hatHeight = 30
            ratio = (hatHeight / float(hatDir.size[1]))
            hatWidth = int((float(hatDir.size[0]) * float(ratio)))
            hatIcon = ImageTk.PhotoImage(hatDir.resize((hatWidth,hatHeight)))
        hat = self.canvas.create_image(event.x, event.y, image=hatIcon, anchor="center")
        # hat = 
        self.canvas.tag_raise(hat)
        self.canvas.update()
        return hat
        
    # is not used
    def loadPlayIcons(self):
        """loads playing icon into the location of the click.
            Currently unused
        """        
        playDir = Image.open(os.path.join(os.getcwd(), "sound", "playing.png"))
        self.playIcons = self.audio.getOpeningSources(int(self.listener.position[0]), int(self.listener.position[1]))
        for opening in self.playIcons:
            opening.playIcon = self.canvas.create_image(math.floor(opening.getLocation()[0] * scale), math.floor(opening.getLocation()[1] * scale), image=ImageTk.PhotoImage(playDir), anchor="center")
            self.canvas.tag_raise(opening.playIcon)
        self.canvas.update()

    def mouseClick(self, event):
        """event handler for the click event.
            Plays the sound and loads the hat icon

        Args:
            event (event): the click event
        """        
        print ("clicked at", math.floor(event.x / scale), math.floor(event.y / scale))
        hat = self.loadHat(event)
        # self.loadPlayIcons()
        self.soundStage(math.floor(event.x / scale), math.floor(event.y / scale))
        self.canvas.delete(hat)
        self.canvas.delete

    # resize Image to fit the fullscreen, taken from https://stackoverflow.com/questions/52234971/how-do-i-make-imageops-fit-not-crop
    def resize_PIL(self, im, output_edge):
        """resized the image to fit the output_edge without changing its aspect ratio

        Args:
            im (image): the image to be resized
            output_edge (int): the size that the output image's largest side should be 

        Returns:
            image: the resized image
        """        
        scale = output_edge / max(im.size)
        new = Image.new(im.mode, (output_edge, output_edge), (255, 255, 255))
        paste = im.resize((int(im.width * scale), int(im.height * scale)), resample=Image.NEAREST)
        new.paste(paste, (0, 0))
        return new

    def prepareUploadedSoundStage(self):
        """creates the MapGenerator object and the SoundGenerator object, 
            then loads the map and the sound stage for the uploaded and processed floor plan
        """        
        self.newMap = mapGenerator.MapGenerator()
        # newMap.create()
        self.newMap.create()
        
        self.newMap.grid.findOpenings()
        # print(newMap.grid.getOpenings())
        
        self.audio = soundGenerator.SoundGenerator(self.newMap.grid, self.newMap.grid.getOpenings())
        self.listener = self.audio.getListener()
        
    def prepareExampleSoundStage(self):
        """creates the MapGenerator object and the SoundGenerator object,
            then loads the map and the sound stage for the example floor plan
        """        
        self.newMap = mapGenerator.MapGenerator()
        # newMap.create()
        self.newMap.createFromSaveFile(example=True)
        
        self.newMap.grid.findOpenings()
        # print(newMap.grid.getOpenings())
        
        self.audio = soundGenerator.SoundGenerator(self.newMap.grid, self.newMap.grid.getOpenings())
        self.listener = self.audio.getListener()
        

    def soundStage(self,x, y):
        """prepares and plays the audio for an event at x, y on the sound stage

        Args:
            x (int): the x coordinate of the event
            y (int): the y coordinate of the event
        """        
        if x < self.newMap.grid.getSizeX() and y < self.newMap.grid.getSizeY():
            self.audio.prepareOpeningSources(x, y)
            self.audio.sayLocation(x, y)
            print("playing sources")
            self.audio.playOpeningSources(x, y)
        

if __name__ == "__main__":
    gui = Gui()
    