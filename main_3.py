from main_2 import MIDI_ANIMATION
import os



def elenca_file_in_cartella(cartella):
    # Verifica se la cartella esiste
    if os.path.exists(cartella):
        # Utilizza list comprehension per creare una lista dei file nella cartella con percorso assoluto
        lista_file = [os.path.abspath(os.path.join(cartella, f)) for f in os.listdir(cartella) if os.path.isfile(os.path.join(cartella, f))]
        return lista_file
    else:
        print(f"La cartella '{cartella}' non esiste.")
        return []

folder_path = "D:\\Progetti\\NASA_SPACE_CHALLENGE_Sonification\\Image"
images_path = elenca_file_in_cartella(folder_path)

for n in range(len(images_path)):
    MIDI_ANIMATION(images_path[n],n)
    print("Image: "+str(n)+' done')
