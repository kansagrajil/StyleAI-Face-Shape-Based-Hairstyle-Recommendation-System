"""
Model Evaluation Script.
Evaluates the trained face shape classifier with classification report,
confusion matrix, and per-class metrics.

Usage:
    python ml/train/evaluate.py --model ml/models/face_shape_cnn.h5 --data-dir ml/data/processed
"""

import os
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix

FACE_SHAPES = ['oval', 'round', 'square', 'heart', 'oblong', 'diamond', 'triangle']


def evaluate(model_path, data_dir):
    """
    Load model and evaluate on the dataset.
    
    Args:
        model_path: Path to the saved Keras model.
        data_dir: Path to processed data directory.
    """
    # Load model
    model = tf.keras.models.load_model(model_path)
    print(f"Loaded model from: {model_path}")

    # Load test data
    images = np.load(os.path.join(data_dir, 'images.npy'))
    labels = np.load(os.path.join(data_dir, 'labels.npy'))

    # Use 20% as test set (same split as training)
    from sklearn.model_selection import train_test_split
    _, X_test, _, y_test = train_test_split(
        images, labels, test_size=0.2, random_state=42, stratify=labels
    )

    # Predict
    if len(X_test.shape) == 2:
        # Feature-based model
        predictions = model.predict(X_test, verbose=0)
    else:
        # CNN model
        predictions = model.predict(X_test, verbose=0)

    y_pred = np.argmax(predictions, axis=1)

    # Classification Report
    print("\n" + "=" * 60)
    print("CLASSIFICATION REPORT")
    print("=" * 60)
    print(classification_report(y_test, y_pred, target_names=FACE_SHAPES, digits=4))

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    print("\nCONFUSION MATRIX")
    print("-" * 40)

    # Header
    header = "          " + "  ".join(f"{s[:5]:>5}" for s in FACE_SHAPES)
    print(header)

    for i, shape in enumerate(FACE_SHAPES):
        row = f"{shape[:8]:>8} |" + "  ".join(f"{cm[i][j]:>5}" for j in range(len(FACE_SHAPES)))
        print(row)

    # Overall accuracy
    accuracy = np.sum(y_pred == y_test) / len(y_test)
    print(f"\nOverall Accuracy: {accuracy:.4f} ({np.sum(y_pred == y_test)}/{len(y_test)})")

    # Per-class accuracy
    print("\nPER-CLASS ACCURACY:")
    for i, shape in enumerate(FACE_SHAPES):
        mask = y_test == i
        if np.sum(mask) > 0:
            acc = np.sum(y_pred[mask] == i) / np.sum(mask)
            print(f"  {shape:>10}: {acc:.4f} ({np.sum(mask)} samples)")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Evaluate face shape classifier')
    parser.add_argument('--model', type=str, default='ml/models/face_shape_cnn.h5')
    parser.add_argument('--data-dir', type=str, default='ml/data/processed')
    args = parser.parse_args()

    evaluate(args.model, args.data_dir)
