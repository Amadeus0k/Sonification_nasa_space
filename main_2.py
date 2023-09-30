import Image_data_import as Img_dt
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from MIDI_tool import str2midi
from MIDI_tool import play_music
from midiutil import MIDIFile
import threading
from tqdm import tqdm

#########################################################################################
def map_value(value, min_value, max_value, min_result, max_result):
    '''maps value (or array of values) from one range to another'''
    result = min_result + (value - min_value) / (max_value - min_value) * (max_result - min_result)
    return result
#########################################################################################

##########################################################################################
# Funzione di inizializzazione dell'animazione
def init():
    line.set_data([], [])
    return line,
##########################################################################################

##########################################################################################
# Funzione chiamata ad ogni frame dell'animazione
def animate(t):
    x = 100*Color_sum[:,t]+x_data[t]
    y = range(0,a.Y_dim)
    line.set_data(x, y)
    return line,
##########################################################################################

##########################################################################################
def Rep_note(midi,i,j,nCol,rep,r_note,nRig):
    if i*nRig+j+rep < i*nRig+nCol:
        if midi[i][j+rep-1] == midi[i][j+rep]:
            r_note = r_note + 1
            rep = rep+1
            if rep == 100:
                return r_note
            if j+rep == nCol-j:
                return r_note
            r_note = Rep_note(midi,i,j,nCol,rep,r_note,nRig)
            return r_note
        else:
            return r_note
    else:
        return r_note
##########################################################################################

##########################################################################################
def rep_not_vert(matrix,nRig,nCol,i,j,rep,rep_v):
    if i+rep < nRig:
        if matrix[i+rep-1][j] == matrix[i+rep][j]:
            rep = rep+1
            rep_v = rep_v+1
            if rep == 100:
                return rep_v
            if i+rep == nRig-i:
                return rep_v
            rep_v = rep_not_vert(matrix,nRig,nCol,i,j,rep,rep_v)
            return rep_v
        else:
            return rep_v
    else:
        return rep_v
####################################################################################################

midi_filename = 'MIDI_IMG.mid'
path_img = "D:\\Progetti\\NASA_SPACE_CHALLENGE_Sonification\\Image\\webb.png"
a = Img_dt.Image(path_img)
a.Import()

x_data = np.array(range(0,a.X_dim))
xdata_per_beat = 20; # quanta x passa per ogni beat (1 beat = 1/4 di nota)
time_data = (x_data/xdata_per_beat)
duration_beats = max(time_data)
print('Duration:',duration_beats,'beats')

# calcolare durata in secondi
bpm = 60 # 1 bpm = 1, 1 beat = 1 sec
duration_sec = duration_beats*60/bpm
print('Duration:',duration_sec,'seconds')

# 4 octaves of major pentatonic scale
note_name_try1 = ['C2','D2','E2','G2','A2',
                  'C3','D3','E3','G3','A3',
                  'C4','D4','E4','G4','A4',
                  'C5','D5','E5','G5','A5']

note_midis_try1 = [str2midi(n) for n in note_name_try1]

# note set for mapping (or use a few octaves of a specific scale) a Cmaj13#11 chord, notes from C lydian
note_name_try2 = ['C1','C2','G2',
             'C3','E3','G3','A3','B3',
             'D4','E4','G4','A4','B4',
             'D5','E5','G5','A5','B5',
             'D6','E6','F#6','G6','A6']

note_midis_try2 = [str2midi(n) for n in note_name_try2]
n_notes = len(note_midis_try1)
print('Resolution:',n_notes,'notes')

# Create midi file object, add tempo
my_midi_file = MIDIFile(1)
my_midi_file.addTempo(track=0,time=0,tempo=bpm)

midi_matrix = np.zeros((n_notes,a.X_dim))
midi_data_matrix = np.zeros((a.Y_dim,a.X_dim))
midi_data_vect = np.zeros((a.Y_dim,1))

vel_matrix = np.zeros((n_notes,a.X_dim))
vel_data_matrix = np.zeros((a.Y_dim,a.X_dim))
vel_min,vel_max = 1,254   # minimum and maximum note velocity

Color_sum = np.zeros((a.Y_dim,a.X_dim))

rep_num_vect = np.zeros((n_notes,1))

# Map data to MIDI note numbers (Bianco a note alte, Velocità delle note: note vicine a uno velocità maggiori)

# Y_dim è il numero di righe e X_dim è il numero di colonne, nella matrice [riga][colonna]
progress_bar = tqdm(total=a.Y_dim, desc="Avanzamento")
for i in range(0,a.Y_dim):
    progress_bar.update(1)
    note_index = round(map_value(i,0,a.Y_dim,n_notes-1,0))
    midi_data_vect[i][0] = note_midis_try1[note_index]
    for j in range(0,a.X_dim):
        Color_sum[i][j] = map_value(sum(a.RGB_Matrix[i][j]), 0, 3, 0, 1)  # Normalize and scaling data
        note_velocity = round(map_value(Color_sum[i][j],0,1,vel_min,vel_max))
        vel_data_matrix[i][j] = note_velocity
progress_bar.close()

progress_bar_ott = tqdm(total=a.Y_dim+n_notes+n_notes, desc="Ottimizzazione dati")
u = 0
midi_matrix[u][0] = midi_data_vect[0][0]
for i in range(0,a.Y_dim):
    progress_bar_ott.update(1)
    if midi_matrix[u][0] != midi_data_vect[i]:
        u = u+1
        midi_matrix[u][0] = midi_data_vect[i][0]
    else:
        rep_num_vect[u][0] = int(rep_num_vect[u][0]+1)

add = 0
for u in range(0,n_notes):
    progress_bar_ott.update(1)
    for j in range(0,a.X_dim):
        vel_matrix[u][j] = int(sum(vel_data_matrix[add:add+int(rep_num_vect[u][0]),j])/int(rep_num_vect[u][0]))
    add = int(rep_num_vect[u][0])+add

repeted_note = np.zeros((a.Y_dim,1))

for u in range(0,n_notes):
    progress_bar_ott.update(1)
    for j in range(0,a.X_dim):
        if repeted_note[u][0] == 0:
            midi_matrix[u][j] = midi_matrix[u][0]
            repeted_note[u][0] = Rep_note(vel_matrix,u,j,a.X_dim,1,0,a.Y_dim)
        else:
            vel_matrix[u][j] = 0
            repeted_note[u][0] = repeted_note[u][0]-1
progress_bar_ott.close()

progress_bar_2 = tqdm(total=n_notes, desc="Memorizzo le note")
for u in range(0,n_notes):
    progress_bar_2.update(1)
    for j in range(0,a.X_dim):
        if midi_matrix[u][j] != 0:
            k = j+1
            if k<a.X_dim-1:
                while midi_matrix[u][k] == 0:
                    k = k+1
                    if k == a.X_dim-1:
                        break
                my_midi_file.addNote(track=0, channel=0, pitch=int(midi_matrix[u][j]), time=time_data[j],duration=time_data[k]-time_data[j], volume=int(vel_matrix[u][j]))
progress_bar_2.close()

# Create and save the midi file itself
with open(midi_filename,'wb') as f:
    my_midi_file.writeFile(f)

##ANIMAZIONE##
# Crea la figura e l'asse
fig, ax = plt.subplots()
a.Plot()
xdata = Color_sum[:,0]
ydata = range(0,a.Y_dim)
line, = ax.plot(xdata, ydata, color='white')

# Crea l'animazione
animation_speed = (duration_sec/len(time_data))*1000
ani = FuncAnimation(fig, animate,frames = len(time_data) ,init_func=init, blit=True,interval=animation_speed)

midi_thread = threading.Thread(target=play_music(midi_filename))
midi_thread.start()
# Visualizza l'animazione
plt.show()
####



