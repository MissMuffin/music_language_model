import os
import shutil
from util_midi import *


def clear_folder(fpath):
    for the_file in os.listdir(fpath):
        file_path = os.path.join(fpath, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

def create_folders(data_raw, data_processed):
    # create processed data dir
    if not os.path.exists(data_processed):
        os.makedirs(data_processed)
    else:
        clear_folder(data_processed)

    # for each folder in data create folder with same name in processed data
    datasets = os.listdir(data_raw)
    for dataset in datasets:

        folder_processed = f"{data_processed}/{dataset}"

        # create notewise and chordwise dirs with test, train, valid in each
        notewise = f"{folder_processed}/notewise"
        chordwise = f"{folder_processed}/chordwise"

        os.makedirs(f"{notewise}/train")
        os.makedirs(f"{notewise}/test")
        os.makedirs(f"{notewise}/valid")

        os.makedirs(f"{chordwise}/train")
        os.makedirs(f"{chordwise}/test")
        os.makedirs(f"{chordwise}/valid")

def create_merged_folders(data_raw, data_processed):
    # create processed data dir
    if not os.path.exists(data_processed):
        os.makedirs(data_processed)
    else:
        clear_folder(data_processed)

        # create notewise and chordwise dirs with test, train, valid in each
        notewise = f"{data_processed}/notewise"
        chordwise = f"{data_processed}/chordwise"

        os.makedirs(f"{notewise}/train")
        os.makedirs(f"{notewise}/test")
        os.makedirs(f"{notewise}/valid")

        os.makedirs(f"{chordwise}/train")
        os.makedirs(f"{chordwise}/test")
        os.makedirs(f"{chordwise}/valid")

def encode_data(data_raw, merged=True):
    # TODO add progress bar
    # we assume a dataset always has only train, test, valid folders
    for dataset in os.listdir(data_raw):
        dataset_path = f"{data_raw}/{dataset}"

        for folder in os.listdir(dataset_path):
            folder_path = f"{dataset_path}/{folder}"

            for fname in os.listdir(folder_path):
                file_path = f"{folder_path}/{fname}"

                fname = os.path.splitext(fname)[0]
                chords, notes = translate_piece(file_path)

                write_location = f"{data_processed}"
                if not merged:
                    write_location = f"{data_processed}/{dataset}"

                with open(f"{write_location}/chordwise/{folder}/{fname}.txt", "w") as fn:
                    fn.write(chords)
                with open(f"{write_location}/notewise/{folder}/{fname}.txt", "w") as fn:
                    fn.write(notes)

if __name__ == "__main__":

    data_raw = "data"
    data_processed = "processed_data"

    create_merged_folders(data_raw, data_processed)
    encode_data(data_raw, merged=True)

    print("All files encoded")