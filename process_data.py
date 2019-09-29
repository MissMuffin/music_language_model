import os
import shutil

data_raw = "data"
data_processed = "processed_data"


def clear_folder(fpath):
    for the_file in os.listdir(fpath):
        file_path = os.path.join(fpath, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

def create_folders():
    # create processed data dir
    if not os.path.exists(data_processed):
        os.makedirs(data_processed)
    else:
        clear_folder(data_processed)

    # for each folder in data create folder with same name in processed data
    datasets = os.listdir(data_raw)
    for dataset in datasets:
        
        folder_processed = f"{data_processed}/{folder}"
        os.makedirs(folder_processed)

        # create notewise and chordwise dirs with test, train, valid in each
        notewise = f"{folder_processed}/notewise"
        chordwise = f"{folder_processed}/chordwise"

        os.makedirs(f"{notewise}/train")
        os.makedirs(f"{notewise}/test")
        os.makedirs(f"{notewise}/valid")

        os.makedirs(f"{chordwise}/train")
        os.makedirs(f"{chordwise}/test")
        os.makedirs(f"{chordwise}/valid")

for dataset in os.listdir(data_raw):
    # we assume a dataset always has only train, test, valid folders
    dataset_path = f"{data_raw}/{dataset}"
    for folder in os.listdir(dataset_path):
        folder_path = f"{dataset_path}/{folder}"
        for fname in os.listdir(folder_path):
            file_path = f"{folder_path}/{fname}"
            # TODO do things here
            print(file_path)


# if __name__ == "__main__":
    # create_folders()