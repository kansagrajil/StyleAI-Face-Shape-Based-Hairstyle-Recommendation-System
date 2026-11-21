"""
Face Shape Classifier Training Script.
Trains a TensorFlow/Keras model to classify face shapes from
geometric feature vectors derived from MediaPipe landmarks.

Usage:
    python ml/train/train_model.py --data-dir ml/data/processed --epochs 50
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split

# Face shape labels
FACE_SHAPES = ['oval', 'round', 'square', 'heart', 'oblong', 'diamond', 'triangle']
NUM_CLASSES = len(FACE_SHAPES)


def build_feature_model(num_features=9):
    """
    Build a dense neural network for feature-based classification.
    Input: geometric feature vector (9 floats).
    Output: softmax probabilities over 7 face shapes.
    
    Args:
        num_features: Number of input features.
    
    Returns:
        keras.Model: Compiled model.
    """
    model = keras.Sequential([
        keras.layers.Input(shape=(num_features,)),
        keras.layers.Dense(128, activation='relu',
                          kernel_regularizer=keras.regularizers.l2(0.01)),
        keras.layers.BatchNormalization(),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(64, activation='relu',
                          kernel_regularizer=keras.regularizers.l2(0.01)),
        keras.layers.BatchNormalization(),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(32, activation='relu'),
        keras.layers.Dense(NUM_CLASSES, activation='softmax')
    ])

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    return model


def build_cnn_model(input_shape=(224, 224, 3)):
    """
    Build a CNN model using MobileNetV2 transfer learning.
    For direct image-based classification as an alternative approach.
    
    Args:
        input_shape: Image dimensions (H, W, C).
    
    Returns:
        keras.Model: Compiled model.
    """
    base_model = keras.applications.MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False  # Freeze base layers

    model = keras.Sequential([
        base_model,
        keras.layers.GlobalAveragePooling2D(),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(NUM_CLASSES, activation='softmax')
    ])

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.0001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    return model


def train(data_dir, output_path, epochs=50, batch_size=32, model_type='feature'):
    """
    Train the face shape classifier.
    
    Args:
        data_dir: Path to processed data (images.npy, labels.npy).
        output_path: Path to save the trained model.
        epochs: Training epochs.
        batch_size: Training batch size.
        model_type: 'feature' for dense network, 'cnn' for MobileNetV2.
    """
    # Load data
    images = np.load(os.path.join(data_dir, 'images.npy'))
    labels = np.load(os.path.join(data_dir, 'labels.npy'))

    print(f"Dataset: {images.shape[0]} samples, {NUM_CLASSES} classes")

    # One-hot encode labels
    labels_onehot = keras.utils.to_categorical(labels, NUM_CLASSES)

    # Split into train/validation
    X_train, X_val, y_train, y_val = train_test_split(
        images, labels_onehot, test_size=0.2, random_state=42, stratify=labels
    )

    print(f"Train: {X_train.shape[0]}, Validation: {X_val.shape[0]}")

    # Build model
    if model_type == 'cnn':
        model = build_cnn_model(input_shape=images.shape[1:])
    else:
        model = build_feature_model(num_features=images.shape[1])

    model.summary()

    # Callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='val_accuracy',
            patience=10,
            restore_best_weights=True
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-6
        ),
        keras.callbacks.ModelCheckpoint(
            output_path,
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        )
    ]

    # Train
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=1
    )

    # Final metrics
    val_loss, val_acc = model.evaluate(X_val, y_val, verbose=0)
    print(f"\nFinal Validation Accuracy: {val_acc:.4f}")
    print(f"Final Validation Loss: {val_loss:.4f}")
    print(f"Model saved to: {output_path}")

    return history


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Train face shape classifier')
    parser.add_argument('--data-dir', type=str, default='ml/data/processed')
    parser.add_argument('--output', type=str, default='ml/models/face_shape_cnn.h5')
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--batch-size', type=int, default=32)
    parser.add_argument('--model-type', type=str, default='feature',
                        choices=['feature', 'cnn'])
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    train(args.data_dir, args.output, args.epochs, args.batch_size, args.model_type)
