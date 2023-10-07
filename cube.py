import time
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from matplotlib.animation import FuncAnimation
from PIL import Image
import os
from tqdm import tqdm
import webbrowser

#def init():
#    im.set_data(a[0])
#    return [im]

#def update(frame):
#    im.set_data(a[frame])
#    return [im]

cube = fits.open("jw02732-o003_t002_nirspec_prism-clear_s3d.fits")
cube.info()
a = cube[1].data
cube.close()
siz = a.shape

valore_massimo = float('-inf')
valore_minimo = float('inf')

for i in range(499,siz[0]):
    for riga in a[i]:
        for elemento in riga:
            if elemento > valore_massimo:
                valore_massimo = elemento
            if elemento < valore_minimo:
                valore_minimo = elemento
    a[i] = (a[i]-valore_minimo)/(valore_massimo-valore_minimo)*255
    valore_massimo = float('-inf')
    valore_minimo = float('inf')

nomi_immagini = [f'immagine_{i}.png' for i in range(a.shape[0])]

cartella_output = 'immagini_salvate'
os.makedirs(cartella_output, exist_ok=True)

progress_bar = tqdm(total=a.shape[0], desc="Avanzamento")

imm = []

for i in range(a.shape[0]):
    progress_bar.update(1)
    immagine = Image.fromarray(a[i])
    immagine = immagine.convert("L")
    immagine = immagine.resize((a.shape[1]*10,a.shape[2]*10))
    imm.append(immagine)
    nome_immagine = os.path.join(cartella_output, nomi_immagini[i])
    immagine.save(nome_immagine)

progress_bar.close()

# Imposta il percorso e il nome del file di output dell'animazione
nome_animazione = "animazione.gif"

# Crea una lista di oggetti immagine PIL
immagini = imm
#immagini = [Image.open(os.path.join(cartella_output, img)) for img in nomi_immagini]

# Salva le immagini come un file GIF animato
immagini[0].save(
    nome_animazione,
    save_all=True,
    append_images=immagini[1:],
    duration=500,  # Durata di ciascuna immagine in millisecondi (0,5 secondi)
    loop=1  # Numero di volte che l'animazione verrà riprodotta (0 per ripetizione infinita)
)

print(f"Animazione salvata come {nome_animazione}")

# Apre l'animazione GIF nel browser predefinito
webbrowser.open(nome_animazione, new=2)  # 'new=2' apre in una nuova finestra/tab del browser

#fig, ax = plt.subplots()
#im = ax.imshow(a[0], cmap='gray')
#ani = FuncAnimation(fig, update, frames=range(len(a)), init_func=init,interval=1,repeat=True)
#plt.show()