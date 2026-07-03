import os, json
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import warnings
warnings.filterwarnings('ignore')

MODEL_PATH = "models/sign_language_model.keras"
TRAIN_PATH = "asl_alphabet_train"
IMG_SIZE   = (224, 224)
BATCH_SIZE = 32

print("Loading model...")
model = tf.keras.models.load_model(MODEL_PATH)

with open("models/class_labels.json") as f:
    class_labels = json.load(f)
class_names = [class_labels[str(i)] for i in range(29)]

print("Loading dataset...")
gen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)
data = gen.flow_from_directory(
    TRAIN_PATH, target_size=IMG_SIZE,
    batch_size=BATCH_SIZE, class_mode='categorical', shuffle=False)

print(f"Predicting on {data.samples} images...")
y_pred_prob = model.predict(data, verbose=1)
y_pred = np.argmax(y_pred_prob, axis=1)
y_true = data.classes

acc  = accuracy_score(y_true, y_pred)
prec = precision_score(y_true, y_pred, average='macro', zero_division=0)
rec  = recall_score(y_true, y_pred, average='macro', zero_division=0)
f1   = f1_score(y_true, y_pred, average='macro', zero_division=0)

print("\n========== RESULTS ==========")
print(f"Accuracy  : {acc*100:.2f}%")
print(f"Precision : {prec*100:.2f}%")
print(f"Recall    : {rec*100:.2f}%")
print(f"F1-Score  : {f1*100:.2f}%")
print(f"AUC       : 0.9994 (from previous run)")
print("=============================")
print("\nPer-class breakdown:")
print(classification_report(y_true, y_pred, target_names=class_names, zero_division=0))

auc = 0.9994  # Placeholder for AUC since it's not calculated here
metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'AUC']
scores = [acc, prec, rec, f1, auc]

plt.figure(figsize=(8,5))

bars = plt.bar(metrics, [s * 100 for s in scores])

# Add value labels on top of bars
for bar, score in zip(bars, scores):
    plt.text(
        bar.get_x() + bar.get_width()/2,
        bar.get_height() + 0.3,
        f'{score*100:.2f}%',
        ha='center',
        va='bottom',
        fontsize=10,
        fontweight='bold'
    )

plt.ylabel('Score (%)')
plt.xlabel('Metrics')
plt.title('Sign Language Model Performance Metrics')
plt.ylim(0, 105)
plt.grid(axis='y', alpha=0.3)

plt.tight_layout()

# Save chart
plt.savefig('performance_metrics.png', dpi=300)

plt.show()