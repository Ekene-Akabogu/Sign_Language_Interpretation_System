import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator # type: ignore

print("Loading model...")
model = tf.keras.models.load_model("models/sign_language_model.keras")

DATASET_PATH = "asl_alphabet_train"
MODEL_SAVE_PATH = "models/sign_language_model_finetuned.keras"

# Unfreeze top 30 layers of MobileNetV2
model.trainable = True
for layer in model.layers[:-30]:
    layer.trainable = False

print(f"Trainable layers: {sum([l.trainable for l in model.layers])}")

# Recompile with lower learning rate
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# More aggressive augmentation this time
train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True,
    brightness_range=[0.5, 1.5],
    zoom_range=0.2,
    shear_range=0.2,
    channel_shift_range=30.0
)

print("Loading data...")
train_generator = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    subset='training'
)

val_generator = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    subset='validation'
)

print("Fine-tuning model...")
history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=5,
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

print(f"\nFine-tuning complete!")
print(f"Model saved to: {MODEL_SAVE_PATH}")