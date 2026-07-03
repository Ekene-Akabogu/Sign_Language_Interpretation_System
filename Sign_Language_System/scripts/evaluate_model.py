import os
import json
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns

# Load model and class labels
model = tf.keras.models.load_model("models/sign_language_model.keras")

with open("models/class_labels.json", "r") as f:
    class_labels = json.load(f)

print("Model loaded successfully")
print(f"Classes: {class_labels}")

# Load test data
test_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)

test_generator = test_datagen.flow_from_directory(
    "asl_alphabet_train",
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    shuffle=False,
    subset=None
)

# Evaluate
print("\nEvaluating model...")
loss, accuracy = model.evaluate(test_generator)
print(f"\nTest Accuracy: {accuracy * 100:.2f}%")
print(f"Test Loss: {loss:.4f}")

# Predictions
print("\nGenerating predictions...")
predictions = model.predict(test_generator)
predicted_classes = np.argmax(predictions, axis=1)
true_classes = test_generator.classes
class_names = list(test_generator.class_indices.keys())

# Classification report
print("\nClassification Report:")
print(classification_report(true_classes, predicted_classes, target_names=class_names))

# Confusion matrix
print("Saving confusion matrix...")
cm = confusion_matrix(true_classes, predicted_classes)
plt.figure(figsize=(20, 16))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=class_names, yticklabels=class_names)
plt.title('Confusion Matrix')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.tight_layout()
plt.savefig("models/confusion_matrix.png")
print("Confusion matrix saved to models/confusion_matrix.png")