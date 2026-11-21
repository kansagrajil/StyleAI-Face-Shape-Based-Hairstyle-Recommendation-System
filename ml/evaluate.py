"""
Model Evaluation and Confusion Matrix Generation Script.
Evaluates the trained TensorFlow face shape classifier on the held-out test set,
computes classification report (Precision, Recall, F1-Score), builds confusion matrix,
and exports visual confusion matrix plot to ml/models/confusion_matrix.png.
"""

import os
import argparse
import numpy as np
import tensorflow as tf

from ml.preprocess import FeatureScaler
from ml.feature_extractor import FACE_SHAPES, NUM_CLASSES


def compute_confusion_matrix(y_true, y_pred, num_classes=6):
    """Compute (num_classes, num_classes) confusion matrix using NumPy."""
    cm = np.zeros((num_classes, num_classes), dtype=int)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
    return cm


def generate_classification_report(y_true, y_pred, labels):
    """Generate precision, recall, f1-score report using NumPy."""
    try:
        from sklearn.metrics import classification_report
        return classification_report(y_true, y_pred, target_names=[s.capitalize() for s in labels], digits=4)
    except Exception:
        cm = compute_confusion_matrix(y_true, y_pred, len(labels))
        lines = []
        lines.append(f"{'Class':<12} {'Precision':>10} {'Recall':>10} {'F1-Score':>10} {'Support':>10}")
        lines.append("-" * 56)

        total_support = len(y_true)
        total_correct = np.trace(cm)

        for i, label in enumerate(labels):
            tp = cm[i, i]
            fp = np.sum(cm[:, i]) - tp
            fn = np.sum(cm[i, :]) - tp
            support = np.sum(cm[i, :])

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

            lines.append(f"{label.capitalize():<12} {precision:10.4f} {recall:10.4f} {f1:10.4f} {support:10d}")

        lines.append("-" * 56)
        accuracy = total_correct / total_support
        lines.append(f"{'Accuracy':<12} {'':>21} {accuracy:10.4f} {total_support:10d}")
        return "\n".join(lines)


def generate_confusion_matrix_plot(cm, labels, output_plot_path='ml/models/confusion_matrix.png'):
    """Generate and save a visual confusion matrix plot."""
    os.makedirs(os.path.dirname(output_plot_path), exist_ok=True)
    
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns

        plt.figure(figsize=(8, 6))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=[s.capitalize() for s in labels],
            yticklabels=[s.capitalize() for s in labels]
        )
        plt.title('Face Shape Classification Confusion Matrix', fontsize=14, fontweight='bold', pad=15)
        plt.xlabel('Predicted Face Shape', fontsize=12, fontweight='bold')
        plt.ylabel('True Face Shape', fontsize=12, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_plot_path, dpi=300)
        plt.close()
        print(f"Confusion matrix visual plot saved to: {output_plot_path}")
        return
    except Exception as e:
        print(f"Matplotlib heatmap notice ({e}). Using OpenCV image generator...")

    try:
        import cv2
        img_size = 600
        margin = 100
        cell_size = (img_size - 2 * margin) // len(labels)
        vis = np.ones((img_size, img_size, 3), dtype=np.uint8) * 255

        max_val = max(1, np.max(cm))
        for i in range(len(labels)):
            for j in range(len(labels)):
                val = cm[i][j]
                intensity = int(255 - (val / max_val) * 200)
                color = (255, intensity, intensity)
                x1 = margin + j * cell_size
                y1 = margin + i * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                cv2.rectangle(vis, (x1, y1), (x2, y2), color, -1)
                cv2.rectangle(vis, (x1, y1), (x2, y2), (200, 200, 200), 1)
                cv2.putText(vis, str(val), (x1 + cell_size // 3, y1 + cell_size // 2 + 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        cv2.putText(vis, "Confusion Matrix", (img_size // 3, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        cv2.imwrite(output_plot_path, vis)
        print(f"Confusion matrix OpenCV image saved to: {output_plot_path}")
    except Exception as err:
        print(f"Image generation skipped: {err}")


def evaluate_model(model_path='ml/models/face_shape_model.h5', data_dir='ml/data/processed',
                   scaler_path='ml/models/scaler.pkl', output_plot_path='ml/models/confusion_matrix.png'):
    """Run complete model evaluation on test set."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    # 1. Load trained TensorFlow model
    model = tf.keras.models.load_model(model_path)
    print(f"Loaded TensorFlow model from: {model_path}")

    # 2. Load held-out test data
    X_test = np.load(os.path.join(data_dir, 'X_test.npy'))
    y_test = np.load(os.path.join(data_dir, 'y_test.npy'))

    # Load scaler and transform test data
    scaler = FeatureScaler()
    if os.path.exists(scaler_path):
        scaler.load(scaler_path)
        X_test_scaled = scaler.transform(X_test)
    else:
        X_test_scaled = X_test

    # 3. Model Inference
    predictions = model.predict(X_test_scaled, verbose=0)
    y_pred = np.argmax(predictions, axis=1)

    # 4. Classification Report
    print("\n" + "=" * 60)
    print("TEST ACCURACY & EVALUATION REPORT")
    print("=" * 60)
    report = generate_classification_report(y_test, y_pred, FACE_SHAPES)
    print(report)

    overall_accuracy = float(np.mean(y_pred == y_test))
    print(f"\nOverall Test Accuracy: {overall_accuracy * 100:.2f}% ({np.sum(y_pred == y_test)}/{len(y_test)})")

    # 5. Confusion Matrix
    cm = compute_confusion_matrix(y_test, y_pred, len(FACE_SHAPES))
    print("\nCONFUSION MATRIX")
    print("-" * 55)

    header = f"{'True \\ Pred':<12}" + "".join(f"{s[:6]:>8}" for s in FACE_SHAPES)
    print(header)
    print("-" * 55)

    for i, shape in enumerate(FACE_SHAPES):
        row = f"{shape[:10]:<12}" + "".join(f"{cm[i][j]:>8}" for j in range(len(FACE_SHAPES)))
        print(row)

    print("-" * 55)

    # 6. Per-class Accuracy
    print("\nPER-CLASS ACCURACY:")
    for i, shape in enumerate(FACE_SHAPES):
        mask = y_test == i
        if np.sum(mask) > 0:
            class_acc = np.mean(y_pred[mask] == i)
            print(f"  {shape.capitalize():<10}: {class_acc * 100:6.2f}% ({np.sum(mask)} test samples)")

    # 7. Save plot
    generate_confusion_matrix_plot(cm, FACE_SHAPES, output_plot_path)

    return overall_accuracy, cm, report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Evaluate TensorFlow Face Shape Model')
    parser.add_argument('--model', type=str, default='ml/models/face_shape_model.h5')
    parser.add_argument('--data-dir', type=str, default='ml/data/processed')
    parser.add_argument('--scaler', type=str, default='ml/models/scaler.pkl')
    parser.add_argument('--plot-output', type=str, default='ml/models/confusion_matrix.png')
    args = parser.parse_args()

    evaluate_model(
        model_path=args.model,
        data_dir=args.data_dir,
        scaler_path=args.scaler,
        output_plot_path=args.plot_output
    )
