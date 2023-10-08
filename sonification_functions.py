import time
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import Image_data_import as Img_dt
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from MIDI_tool import str2midi
from midiutil import MIDIFile
import threading
from tqdm import tqdm
import os


def list_files_in_folder(folder_path):
    # Returns a list of files in the specified folder with absolute paths.
    if os.path.exists(folder_path):
        files_list = [os.path.abspath(os.path.join(folder_path, file_name)) for file_name in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file_name))]
        return files_list
    else:
        print(f"The folder '{folder_path}' does not exist.")
        return []


def map_value(value, min_value, max_value, min_result, max_result):
    # Maps value (or array of values) from one range to another
    result = min_result + (value - min_value) / (max_value - min_value) * (max_result - min_result)
    return result


def repeat_note(midi, i, j, n_col, rep, r_note, n_row):
    if i * n_row + j + rep < i * n_row + n_col:
        if midi[i][j + rep - 1] == midi[i][j + rep]:
            r_note += 1
            rep += 1
            # Uncomment the line below if you want to limit repetitions to 100
            if rep == 100:
                return r_note
            if j + rep == n_col - j:
                return r_note
            r_note = repeat_note(midi, i, j, n_col, rep, r_note, n_row)
            return r_note
        else:
            return r_note
    else:
        return r_note

midi_filename = 'MIDI_IMG.mid'
path_img = "Image/jw02731-o001_t017_nircam_clear-f335m_i2d.png"

def create_midi_animation(image_path, number):
    def initialize_animation():
        line.set_data([], [])
        return line,

    def animate_frame(t):
        x = 100 * Color_sum[:, t] + x_data[t]
        y = range(0, image_height)
        line.set_data(x, y)
        return line,

    def process_data_range(start, end):
        for i in range(start, end):
            note_index = round(map_value(i, 0, image_height, num_notes - 1, 0))
            midi_data_vect[i][0] = note_midis[note_index]
            for j in range(image_width):
                Color_sum[i][j] = map_value(sum(image.RGB_Matrix[i][j]), 0, 3, 0, 1)
                note_velocity = round(map_value(Color_sum[i][j], 0, 1, velocity_min, velocity_max))
                vel_data_matrix[i][j] = note_velocity
            with progress_lock:
                progress_bar.update(1)

    animation_filename = f'animation_{number}.gif'
    midi_filename = f'MIDI_IMG_{number}.mid'
    image = Img_dt.Image(image_path)
    image.Import()

    image_width = image.X_dim
    image_height = image.Y_dim

    x_data = np.array(range(0, image_width))
    xdata_per_beat = 50  # how much x changes per beat (1 beat = 1/4 note)
    time_data = (x_data / xdata_per_beat)
    duration_beats = max(time_data)
    print('Duration:', duration_beats, 'beats')

    # calculate duration in seconds
    bpm = 100  # 1 bpm = 1, 1 beat = 1 sec
    duration_seconds = duration_beats * 60 / bpm
    print('Duration:', duration_seconds, 'seconds')

    note_names = [['D3', 'F3', 'A3', 'C3', 'D5', 'F5', 'A5', 'C5'],
                       ['E3', 'G3', 'B3', 'D3', 'E5', 'G5', 'B5', 'D5'],
                       ['A3', 'C3', 'E3', 'G3', 'A5', 'C5', 'E5', 'G5'],
                       ['C3', 'E3', 'G3', 'B3', 'C5', 'E5', 'G5', 'B5'],
                       ['F3', 'A3', 'C3', 'E3', 'F5', 'A5', 'C5', 'E5'],
                       ['G3', 'B3', 'D3', 'F3', 'G5', 'B5', 'D5', 'F5']]

    note_midis = [str2midi(n) for n in note_names[number]]
    num_notes = len(note_midis)
    print('Resolution:', num_notes, 'notes')
    time.sleep(0.02)

    # Create midi file object, add tempo
    my_midi_file = MIDIFile(1)
    my_midi_file.addTempo(track=0, time=0, tempo=bpm)

    midi_matrix = np.zeros((num_notes, image_width))
    midi_data_vect = np.zeros((image_height, 1))

    vel_matrix = np.zeros((num_notes, image_width))
    vel_data_matrix = np.zeros((image_height, image_width))
    velocity_min, velocity_max = 1, 254  # minimum and maximum note velocity

    Color_sum = np.zeros((image_height, image_width))

    rep_num_vect = np.zeros((num_notes, 1))

    image_height = image_height  # Replace with the actual value of image_height
    num_threads = 4
    chunk_size = image_height // num_threads

    progress_bar = tqdm(total=image_height, desc="Progress")

    progress_lock = threading.Lock()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for i in range(num_threads):
            start = i * chunk_size
            end = (i + 1) * chunk_size if i < num_threads - 1 else image_height
            futures.append(executor.submit(process_data_range, start, end))

        for future in concurrent.futures.as_completed(futures):
            pass

    progress_bar.close()

    progress_bar_ott = tqdm(total=image_height + num_notes + num_notes, desc="Data Optimization")
    u = 0
    midi_matrix[u][0] = midi_data_vect[0][0]
    for i in range(0, image_height):
        progress_bar_ott.update(1)
        if midi_matrix[u][0] != midi_data_vect[i]:
            u = u + 1
            midi_matrix[u][0] = midi_data_vect[i][0]
        else:
            rep_num_vect[u][0] = int(rep_num_vect[u][0] + 1)

    add = 0
    for u in range(0, num_notes):
        progress_bar_ott.update(1)
        for j in range(0, image_width):
            vel_matrix[u][j] = int(sum(vel_data_matrix[add:add + int(rep_num_vect[u][0]), j]) / int(
                rep_num_vect[u][0]))
        add = int(rep_num_vect[u][0]) + add

    repeated_note = np.zeros((image_height, 1))

    for u in range(0, num_notes):
        progress_bar_ott.update(1)
        for j in range(0, image_width):
            if repeated_note[u][0] == 0:
                midi_matrix[u][j] = midi_matrix[u][0]
                repeated_note[u][0] = repeat_note(vel_matrix, u, j, image_width, 1, 0, image_height)
            else:
                vel_matrix[u][j] = 0
                repeated_note[u][0] = repeated_note[u][0] - 1
    progress_bar_ott.close()

    progress_bar_2 = tqdm(total=num_notes, desc="Storing Notes")
    for u in range(0, num_notes):
        progress_bar_2.update(1)
        for j in range(0, image_width):
            if midi_matrix[u][j] != 0:
                k = j + 1
                if k < image_width - 1:
                    while midi_matrix[u][k] == 0:
                        k = k + 1
                        if k == image_width - 1:
                            break
                    my_midi_file.addNote(track=0, channel=0, pitch=int(midi_matrix[u][j]), time=time_data[j],
                                        duration=time_data[k] - time_data[j], volume=int(vel_matrix[u][j]))
    progress_bar_2.close()

    with open(midi_filename, 'wb') as f:
        my_midi_file.writeFile(f)

    fig, ax = plt.subplots()
    image.Plot()
    xdata = Color_sum[:, 0]
    ydata = range(0, image_height)
    line, = ax.plot(xdata, ydata, color='white')

    animation_speed = (duration_seconds / len(time_data)) * 1000
    ani = FuncAnimation(fig, animate_frame,frames = len(time_data) ,init_func=initialize_animation, blit=True,interval=animation_speed)
    plt.show()