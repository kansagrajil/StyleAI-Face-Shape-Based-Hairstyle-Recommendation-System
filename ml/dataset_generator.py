"""
Dataset Generator & Dataset Preparation Module.
Generates balanced feature datasets for Oval, Round, Square, Heart, Diamond, and Oblong face shapes,
splits data into Train (70%), Validation (15%), and Test (15%) sets, and saves numpy arrays.
"""

import os
import argparse
import numpy as np

# 7 Target Face Shape Classes
FACE_SHAPES = ['oval', 'round', 'square', 'heart', 'diamond', 'oblong', 'triangle']
LABEL_TO_IDX = {shape: idx for idx, shape in enumerate(FACE_SHAPES)}
IDX_TO_LABEL = {idx: shape for idx, shape in enumerate(FACE_SHAPES)}

# Statistical distribution parameters (mean, std) for 9 geometric features per face shape
# Feature order: [jaw_w, forehead_w, length, cheek_w, w_l_ratio, f_j_ratio, c_j_ratio, jaw_angle, chin_roundness]
CLASS_DISTRIBUTIONS = {
    'oval': {
        'mean': [0.45, 0.44, 0.63, 0.48, 0.71, 0.98, 1.07, 125.0, 0.58],
        'std':  [0.02, 0.02, 0.03, 0.02, 0.03, 0.04, 0.03, 5.0,   0.05]
    },
    'round': {
        'mean': [0.50, 0.48, 0.58, 0.53, 0.86, 0.96, 1.06, 135.0, 0.75],
        'std':  [0.02, 0.02, 0.02, 0.02, 0.04, 0.04, 0.03, 6.0,   0.06]
    },
    'square': {
        'mean': [0.51, 0.50, 0.62, 0.52, 0.82, 0.98, 1.02, 102.0, 0.32],
        'std':  [0.02, 0.02, 0.03, 0.02, 0.04, 0.04, 0.03, 5.0,   0.05]
    },
    'heart': {
        'mean': [0.38, 0.52, 0.64, 0.48, 0.59, 1.37, 1.26, 118.0, 0.48],
        'std':  [0.02, 0.02, 0.03, 0.02, 0.03, 0.05, 0.04, 5.0,   0.05]
    },
    'diamond': {
        'mean': [0.40, 0.41, 0.63, 0.53, 0.63, 1.02, 1.32, 114.0, 0.42],
        'std':  [0.02, 0.02, 0.03, 0.02, 0.03, 0.04, 0.05, 5.0,   0.05]
    },
    'oblong': {
        'mean': [0.42, 0.42, 0.74, 0.44, 0.57, 1.00, 1.05, 122.0, 0.52],
        'std':  [0.02, 0.02, 0.03, 0.02, 0.03, 0.04, 0.03, 5.0,   0.05]
    },
    'triangle': {
        'mean': [0.53, 0.41, 0.63, 0.48, 0.76, 0.77, 0.91, 108.0, 0.38],
        'std':  [0.02, 0.02, 0.03, 0.02, 0.03, 0.04, 0.04, 5.0,   0.05]
    }
}


def numpy_stratified_split(X, y, test_size=0.15, val_size=0.15, random_seed=42):
    """Pure NumPy implementation of stratified Train/Val/Test split."""
    np.random.seed(random_seed)

    train_indices = []
    val_indices = []
    test_indices = []

    unique_classes = np.unique(y)
    for c in unique_classes:
        c_idx = np.where(y == c)[0]
        np.random.shuffle(c_idx)

        n_samples = len(c_idx)
        n_test = int(round(n_samples * test_size))
        n_val = int(round(n_samples * val_size))

        test_indices.extend(c_idx[:n_test])
        val_indices.extend(c_idx[n_test:n_test + n_val])
        train_indices.extend(c_idx[n_test + n_val:])

    np.random.shuffle(train_indices)
    np.random.shuffle(val_indices)
    np.random.shuffle(test_indices)

    return (
        X[train_indices], y[train_indices],
        X[val_indices], y[val_indices],
        X[test_indices], y[test_indices]
    )


def generate_synthetic_dataset(samples_per_class=600, random_seed=42):
    """Generate synthetic landmark feature dataset based on facial geometry statistics."""
    np.random.seed(random_seed)
    X = []
    y = []

    for label_idx, shape in enumerate(FACE_SHAPES):
        params = CLASS_DISTRIBUTIONS[shape]
        mean = np.array(params['mean'])
        std = np.array(params['std'])

        samples = np.random.normal(loc=mean, scale=std, size=(samples_per_class, len(mean)))

        samples[:, 0] = np.clip(samples[:, 0], 0.25, 0.65)
        samples[:, 1] = np.clip(samples[:, 1], 0.25, 0.65)
        samples[:, 2] = np.clip(samples[:, 2], 0.45, 0.85)
        samples[:, 3] = np.clip(samples[:, 3], 0.30, 0.70)
        samples[:, 4] = np.clip(samples[:, 4], 0.45, 1.00)
        samples[:, 5] = np.clip(samples[:, 5], 0.70, 1.60)
        samples[:, 6] = np.clip(samples[:, 6], 0.85, 1.55)
        samples[:, 7] = np.clip(samples[:, 7], 85.0, 150.0)
        samples[:, 8] = np.clip(samples[:, 8], 0.15, 0.95)

        X.append(samples)
        y.extend([label_idx] * samples_per_class)

    X = np.vstack(X).astype(np.float32)
    y = np.array(y, dtype=np.int32)

    shuffle_idx = np.random.permutation(len(y))
    return X[shuffle_idx], y[shuffle_idx]


def prepare_dataset_splits(X, y, output_dir='ml/data/processed', test_size=0.15, val_size=0.15, random_seed=42):
    """Split dataset into Train (70%), Validation (15%), and Test (15%) sets, and save."""
    os.makedirs(output_dir, exist_ok=True)

    X_train, y_train, X_val, y_val, X_test, y_test = numpy_stratified_split(
        X, y, test_size=test_size, val_size=val_size, random_seed=random_seed
    )

    print("=" * 60)
    print("DATASET PREPARATION COMPLETE")
    print("=" * 60)
    print(f"Total Samples: {len(y)}")
    print(f"Train Set:      {X_train.shape[0]} samples ({(len(X_train)/len(y))*100:.1f}%)")
    print(f"Validation Set: {X_val.shape[0]} samples ({(len(X_val)/len(y))*100:.1f}%)")
    print(f"Test Set:       {X_test.shape[0]} samples ({(len(X_test)/len(y))*100:.1f}%)")
    print(f"Number of Features: {X_train.shape[1]}")
    print(f"Target Classes: {FACE_SHAPES}")

    np.save(os.path.join(output_dir, 'X_train.npy'), X_train)
    np.save(os.path.join(output_dir, 'y_train.npy'), y_train)
    np.save(os.path.join(output_dir, 'X_val.npy'), X_val)
    np.save(os.path.join(output_dir, 'y_val.npy'), y_val)
    np.save(os.path.join(output_dir, 'X_test.npy'), X_test)
    np.save(os.path.join(output_dir, 'y_test.npy'), y_test)

    # Legacy compatibility files
    X_train_val = np.vstack([X_train, X_val])
    y_train_val = np.concatenate([y_train, y_val])
    np.save(os.path.join(output_dir, 'images.npy'), X_train_val)
    np.save(os.path.join(output_dir, 'labels.npy'), y_train_val)

    print(f"Saved processed dataset splits to: {output_dir}/")
    return X_train, y_train, X_val, y_val, X_test, y_test


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prepare Face Shape Dataset')
    parser.add_argument('--output-dir', type=str, default='ml/data/processed', help='Path to save processed splits')
    parser.add_argument('--samples-per-class', type=int, default=600, help='Synthetic samples per class')
    args = parser.parse_args()

    print(f"Generating synthetic feature dataset ({args.samples_per_class} samples/class)...")
    X, y = generate_synthetic_dataset(samples_per_class=args.samples_per_class)
    prepare_dataset_splits(X, y, output_dir=args.output_dir)
