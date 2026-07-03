import os
import json
import numpy as np
import tensorflow as tf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report
import warnings
warnings.filterwarnings('ignore')

os.makedirs('results', exist_ok=True)

MODEL_PATH = "models/sign_language_model.keras"
TRAIN_PATH = "asl_alphabet_train"
IMG_SIZE   = (224, 224)
BATCH_SIZE = 32

print("Loading model...")
model = tf.keras.models.load_model(MODEL_PATH)

with open("models/class_labels.json") as f:
    class_labels = json.load(f)
class_names = [class_labels[str(i)] for i in range(29)]

gen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)
data = gen.flow_from_directory(
    TRAIN_PATH, target_size=IMG_SIZE,
    batch_size=BATCH_SIZE, class_mode='categorical', shuffle=False)

print(f"Predicting on {data.samples} images...")
y_pred_prob = model.predict(data, verbose=1)
y_pred = np.argmax(y_pred_prob, axis=1)
y_true = data.classes

report = classification_report(y_true, y_pred,
                                target_names=class_names,
                                output_dict=True, zero_division=0)

f1_scores = [report[c]['f1-score'] * 100 for c in class_names]

# Plot
colors = ['#2ecc71' if f >= 95 else '#e67e22' if f >= 90 else '#e74c3c' for f in f1_scores]
fig, ax = plt.subplots(figsize=(16, 6))
bars = ax.bar(class_names, f1_scores, color=colors, edgecolor='white', linewidth=0.5)
ax.axhline(y=95, color='green', linestyle='--', linewidth=1.2, label='95% threshold')
ax.axhline(y=90, color='orange', linestyle='--', linewidth=1.2, label='90% threshold')
for bar, val in zip(bars, f1_scores):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f'{val:.1f}', ha='center', va='bottom', fontsize=7.5, fontweight='bold')
ax.set_xlabel('ASL Class', fontsize=12)
ax.set_ylabel('F1-Score (%)', fontsize=12)
ax.set_title('Per-Class F1-Score – Full Dataset (29 Classes)', fontsize=14, fontweight='bold')
ax.set_ylim(80, 102)
ax.legend(fontsize=10)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('results/f1_per_class.png', dpi=150)
plt.close()
print("Saved → results/f1_per_class.png")

# Print values
print("\nPer-class F1 scores:")
for c, f in zip(class_names, f1_scores):
    print(f"  {c}: {f:.2f}%")