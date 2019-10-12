import os

dataset_path = "processed_data"

token_counter = 0
token_ocurrance = {}

vocabs = {}

wait_counter = 0
wait_ocurrance = {}

rest_counter = 0
rest_ocurrance = {}

for encoding in os.listdir(dataset_path):
    encoding_path = f"{dataset_path}/{encoding}"

    vocabs[encoding] = {}
    token_ocurrance[encoding] = {}

    for subset in os.listdir(encoding_path):
        subset_path = f"{encoding_path}/{subset}"

        vocabs[encoding][subset] = {}

        for fname in os.listdir(subset_path):

            fname_path = f"{subset_path}/{fname}"
            with open(f"{fname_path}", "r") as fn:
                tokens = fn.read().split(" ")

                for token in tokens:

                    token_counter += 1

                    if encoding == "notewise":
                        if "wait" in token:
                            wait_counter += 1
                            if token in wait_ocurrance:
                                wait_ocurrance[token] += 1
                            else:
                                wait_ocurrance[token] = 1
                    elif encoding == "chordwise":
                        if "0" not in token:
                            rest_counter += 1
                            if token in rest_ocurrance:
                                rest_ocurrance[token] += 1
                            else:
                                rest_ocurrance[token] = 1

                    if token in vocabs[encoding][subset]:
                        vocabs[encoding][subset][token] += 1
                    else:
                        vocabs[encoding][subset][token] = 1

                    if token in token_ocurrance[encoding]:
                        token_ocurrance[encoding][token] += 1
                    else:
                        token_ocurrance[encoding][token] = 1


dataset_vocab_counter = 0
for encoding in vocabs:
    for subset in vocabs[encoding]:
        dataset_vocab_counter += len(vocabs[encoding][subset])

notewise_vocab_counter = 0
for subset in vocabs["notewise"]:
    notewise_vocab_counter += len(vocabs["notewise"][subset])

chordwise_vocab_counter = 0
for subset in vocabs["chordwise"]:
    chordwise_vocab_counter += len(vocabs["chordwise"][subset])



print(f"\nNumber of tokens in dataset vocab: {dataset_vocab_counter}")
print(f"Number of tokens in notewise vocab: {notewise_vocab_counter}")
print(f"Number of tokens in chordwise vocab: {chordwise_vocab_counter}\n")

print(f"Total number of tokens in dataset: {token_counter}\n")

print(f"Total number of wait tokens in dataset: {wait_counter}")
print(f"Total number of rest tokens in dataset: {rest_counter}\n")

print(f"Percantage wait tokens: {(wait_counter / token_counter) * 100}")
print(f"Percantage rest tokens: {(rest_counter / token_counter) * 100}\n")