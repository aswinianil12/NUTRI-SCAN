import os

train_anemic = len(os.listdir("dataset_eye/train/anemic"))
train_non_anemic = len(os.listdir("dataset_eye/train/non_anemic"))
test_anemic = len(os.listdir("dataset_eye/test/anemic"))
test_non_anemic = len(os.listdir("dataset_eye/test/non_anemic"))

print("Train anemic:", train_anemic)
print("Train non_anemic:", train_non_anemic)
print("Test anemic:", test_anemic)
print("Test non_anemic:", test_non_anemic)