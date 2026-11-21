"""
TensorFlow Face Shape Classifier Training Pipeline.
Trains the neural network on MediaPipe geometric landmark features,
uses validation data for hyperparameter tuning and checkpointing,
and saves the trained model to ml/models/face_shape_model.h5.
"""

import os
import argparse
import numpy as np
import tensorflow as tf
from tensorflow import keras

from ml.preprocess import preprocess_data
from ml.model import build_feature_model, build_cnn_model, FACE_SHAPES, NUM_CLASSES


def train_model(data_dir='ml/data/processed', output_path='ml/models/face_shape_model.h5',
                epochs=50, batch_size=32, model_type='feature'):
    """
    Execute training and validation pipeline.
    
    Args:
        data_dir: Path to processed dataset splits directory.
        output_path: Path where trained .h5 model will be saved.
        epochs: Maximum training epochs.
        batch_size: Mini-batch size.
        model_type: 'feature' for landmark MLP, 'cnn' for MobileNetV2.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print("=" * 60)
    print("STARTING TENSORFLOW MODEL TRAINING")
    print("=" * 60)

    # 1. Load preprocessed and scaled dataset splits
    X_train, y_train_raw, X_val, y_val_raw, X_test, y_test_raw, scaler = preprocess_data(
        data_dir=data_dir,
        scaler_path=os.path.join(os.path.dirname(output_path), 'scaler.pkl'),
        augment=True
    )

    # One-hot encode targets
    y_train = keras.utils.to_categorical(y_train_raw, NUM_CLASSES)
    y_val = keras.utils.to_categorical(y_val_raw, NUM_CLASSES)
    y_test = keras.utils.to_categorical(y_test_raw, NUM_CLASSES)

    print(f"Train samples: {X_train.shape[0]}, Validation samples: {X_val.shape[0]}")

    # 2. Build model architecture
    if model_type == 'cnn':
        model = build_cnn_model(input_shape=X_train.shape[1:])
    else:
        model = build_feature_model(num_features=X_train.shape[1])

    model.summary()

    # 3. Configure Training Callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='val_accuracy',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-6,
            verbose=1
        ),
        keras.callbacks.ModelCheckpoint(
            output_path,
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        )
    ]

    # 4. Fit Model on Training set with Validation monitoring
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=1
    )

    # 5. Evaluate final validation performance
    val_loss, val_acc = model.evaluate(X_val, y_val, verbose=0)
    print("\n" + "=" * 60)
    print("TRAINING SUMMARY")
    print("=" * 60)
    print(f"Best Validation Accuracy: {val_acc * 100:.2f}%")
    print(f"Best Validation Loss:     {val_loss:.4f}")
    print(f"Trained model saved to:  {output_path}")

    # Save extra copy to legacy location for backward compatibility
    legacy_path = 'ml/models/face_shape_cnn.h5'
    os.makedirs(os.path.dirname(legacy_path), exist_ok=True)
    model.save(legacy_path)
    print(f"Legacy model copy saved to: {legacy_path}")

    return model, history


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train TensorFlow Face Shape Model')
    parser.add_argument('--data-dir', type=str, default='ml/data/processed')
    parser.add_argument('--output', type=str, default='ml/models/face_shape_model.h5')
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--batch-size', type=int, default=32)
    parser.add_argument('--model-type', type=str, default='feature', choices=['feature', 'cnn'])
    args = parser.parse_args()

    train_model(
        data_dir=args.data_dir,
        output_path=args.output,
        epochs=args.epochs,
        batch_size=args.batch_size,
        model_type=args.model_type
    )
