import os
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2 
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

print("TensorFlow version:", tf.__version__)

# Paths
DATASET_PATH = "asl_alphabet_train"
MODEL_SAVE_PATH = "models/sign_language_model.keras"

# Settings
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10
NUM_CLASSES = 29

# Data augmentation for training, just rescaling for validation
train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=10,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True
)

print("Loading training data...")
train_generator = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'
)

print("Loading validation data...")
val_generator = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation'
)

# Save class labels
import json
class_indices = train_generator.class_indices
class_labels = {v: k for k, v in class_indices.items()}
with open("models/class_labels.json", "w") as f:
    json.dump(class_labels, f)
print(f"Classes: {class_indices}")

# Build model using MobileNetV2 transfer learning
print("Building model...")
base_model = MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False  # Freeze base model

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dropout(0.3)(x)
x = Dense(128, activation='relu')(x)
output = Dense(NUM_CLASSES, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=output)

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# Train
print("\nStarting training...")
history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=EPOCHS,
    callbacks=[
        tf.keras.callbacks.ModelCheckpoint(
            MODEL_SAVE_PATH,
            save_best_only=True,
            monitor='val_accuracy'
        ),
        tf.keras.callbacks.EarlyStopping(
            patience=3,
            monitor='val_accuracy',
            restore_best_weights=True
        )
    ]
)

print("\nTraining complete!")
print(f"Model saved to: {MODEL_SAVE_PATH}")