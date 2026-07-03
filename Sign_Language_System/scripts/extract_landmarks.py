import os

DATASET_PATH = "asl_alphabet_train"

classes = sorted(os.listdir(DATASET_PATH))
classes = [c for c in classes if os.path.isdir(os.path.join(DATASET_PATH, c))]

print(f"Number of classes: {len(classes)}")
print(f"Classes: {classes}")

total = 0
for label in classes:
    folder = os.path.join(DATASET_PATH, label)
    count = len(os.listdir(folder))
    print(f"  {label}: {count} images")
    total += count

print(f"\nTotal images: {total}");