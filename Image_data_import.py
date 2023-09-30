import numpy as np
from matplotlib import pyplot as plt
from matplotlib import image as mpimg
from tqdm import tqdm

class Image:

    def __init__(self,path):
        self.path = path

    def Import(self):
        self.image = mpimg.imread(self.path) # Alto verso basso, sinistra verso destra (Dataset)
        self.X_dim = self.image.shape[1]
        self.Y_dim = self.image.shape[0]
        self.Attribute_for_pixel = self.image.shape[2]
        self.Pixel_Matrix = self.image.__array__()
        if self.Pixel_Matrix[0][0][0]>1:
            if self.Pixel_Matrix[0][0][0] != 0:
                self.RGB_Matrix = np.zeros((self.Y_dim,self.X_dim,3))
                progress_bar_1 = tqdm(total=self.Y_dim, desc="Formattazione da 255/0 a 1/0")
                for i in range(0,self.Y_dim):
                    progress_bar_1.update(1)
                    for j in range(0,self.X_dim):
                        for u in range(0,3):
                            self.RGB_Matrix[i][j][u] = self.Pixel_Matrix[i][j][u]/255
                progress_bar_1.close()
            else:
                self.RGB_Matrix = self.Pixel_Matrix
        else:
            self.RGB_Matrix = self.Pixel_Matrix

    def Plot(self):
        plt.imshow(self.image)
        #plt.show()