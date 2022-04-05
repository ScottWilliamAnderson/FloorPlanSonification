
class Opening():
    """Opening Class
        Can be a window or a door
        contains a list of pixels that make up the shape of the opening
        has a center pixel
        has a sound source
    """    
    
    def __init__(self, listedPixels):
        self.listedPixels = listedPixels
        self.centerPixel = self.averagePixel()
        self.soundSource = None
        
        
    
    def averagePixel(self):
        """returns the center pixel of a this opening shape (a list of pixels)
            Does not assume that the returned pixel is part of the opening
            
        Returns:
            tuple: the pixel closest to the center of that opening
        """        
        x = []
        y = []
        for pixel in self.listedPixels:
            x.append(pixel[0])
            y.append(pixel[1])
        avgX = sum(x)/len(x)
        avgY = sum(y)/len(y)
        
        return (int(avgX), int(avgY))
    
    def getLocation(self):
        """returns the center pixel of a this opening shape (a list of pixels)

        Returns:
            tuple: the pixel closest to the center of that opening
        """        
        return self.centerPixel
        
        
    def getPixels(self):
        """returns the pixels of this opening shape (a list of pixels)

        Returns:
            list: the pixels of this opening shape (a list of pixels)
        """        
        return self.listedPixels
    
    def setSoundSource(self, source):
        """sets the sound source of this opening

        Args:
            source (openal.Source): the sound source of this opening
        """        
        self.soundSource = source
    
    def getSoundSource(self):
        """returns the sound source of this opening

        Returns:
            source (openal.Source): the sound source of this opening
        """        
        return self.soundSource
        
    