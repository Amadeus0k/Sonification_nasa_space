from sonification_functions import list_files_in_folder, create_midi_animation


def main():
    folder_path = "C:\\Users\\fedeb\\OneDrive\\Desktop\\Sonification_nasa_space\\Image"
    images_path = list_files_in_folder(folder_path)

    for index, image_path in enumerate(images_path):
        create_midi_animation(image_path, index)
        print(f"Image {index}: Processed")


if __name__ == "__main__":
    main()
