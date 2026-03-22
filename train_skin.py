import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
import json
import os

# Configuration
DATASET_PATH = 'datasets/skin'
MODEL_SAVE_PATH = 'models/skin_cancer_model.h5'
HISTORY_SAVE_PATH = 'json_files/skin cancer/training_history.json'
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 5

def train():
    # Check if dataset has enough data
    classes = ['malignant', 'benign']
    for c in classes:
        p = os.path.join(DATASET_PATH, c)
        if not os.path.exists(p) or len(os.listdir(p)) < 2:
            print(f"Error: Not enough data in {p}. Need at least 2 images per class.")
            return

    # Data Augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        validation_split=0.2
    )

    train_generator = train_datagen.flow_from_directory(
        DATASET_PATH,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training'
    )

    val_generator = train_datagen.flow_from_directory(
        DATASET_PATH,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation'
    )

    # Model
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    base_model.trainable = False

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    predictions = Dense(2, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # Training
    print("Starting training...")
    history = model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=EPOCHS
    )

    # Save Model
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    model.save(MODEL_SAVE_PATH)
    print(f"Model saved to {MODEL_SAVE_PATH}")

    # Save History
    history_dict = {
        "accuracy": [float(x) for x in history.history['accuracy']],
        "val_accuracy": [float(x) for x in history.history['val_accuracy']],
        "loss": [float(x) for x in history.history['loss']],
        "val_loss": [float(x) for x in history.history['val_loss']]
    }
    
    os.makedirs(os.path.dirname(HISTORY_SAVE_PATH), exist_ok=True)
    with open(HISTORY_SAVE_PATH, 'w') as f:
        json.dump(history_dict, f)
    print(f"History saved to {HISTORY_SAVE_PATH}")

if __name__ == "__main__":
    train()
