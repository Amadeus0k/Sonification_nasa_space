import numpy as np
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from astropy.visualization import make_lupton_rgb

fits_image_filename = "JWST/jw02731-o001_t017_nircam_clear-f200w/jw02731-o001_t017_nircam_clear-f200w_i2d.fits"

hdul = fits.open(fits_image_filename)

file_r = fits.open('r.fits')
file_g = fits.open('g.fits')
file_i = fits.open('i.fits')
file_r.info()
r = file_r[0].data
g = file_g[0].data
i = file_i[0].data
hdul.info()

image = make_lupton_rgb(r,g,i,stretch=0.5)
plt.imshow(image)
#prova = hdul[3].data[:,:,1]
#image_g = hdul[3].data[:,:,2]
#image_b = hdul[3].data[:,:,3]
#image = make_lupton_rgb(prova, image_g, image_b, stretch=0.5)
r = [1,2,4,5,6,7]

#for i in r:
#    prova = hdul[i].data
#    image = make_lupton_rgb(prova,prova,prova,stretch=0.5)
#    plt.figure(i)
#    plt.imshow(image)

plt.show()
hdul.close()
file_r.close()
file_g.close()
file_i.close()
