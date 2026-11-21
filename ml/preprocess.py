"""
Data Preprocessing & Augmentation Pipeline.
Handles feature scaling, standardization, and landmark vector jitter augmentation.
"""

import os
import pickle
import numpy as np

# Target face shape categories
FACE_SHAPES = ['oval', 'round', 'square', 'heart', 'diamond', 'oblong', 'triangle']


class FeatureScaler:
    """Standardization Scaler (Mean=0, Std=1) for 9 geometric features."""

    def __init__(self):
        self.mean = None
        self.std = None

    def fit(self, X):
        """Compute mean and standard deviation from training data."""
        self.mean = np.mean(X, axis=0)
        self.std = np.std(X, axis=0) + 1e-8  # Avoid zero division
        return self

    def transform(self, X):
        """Standardize features."""
        if self.mean is None or self.std is None:
            raise ValueError("Scaler has not been fitted yet!")
        return (X - self.mean) / self.std

    def fit_transform(self, X):
        """Fit and transform in one step."""
        return self.fit(X).transform(X)

    def save(self, filepath):
        """Save scaler parameters to pickle file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump({'mean': self.mean, 'std': self.std}, f)

    def load(self, filepath):
        """Load scaler parameters from pickle file."""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.mean = data['mean']
            self.std = data['std']
        return self


def augment_feature_vectors(X, y, noise_level=0.02, num_augments=2):
    """
    Apply Gaussian noise jitter augmentation to landmark feature vectors to prevent overfitting.
    
    Args:
        X: numpy array of features (N, 9).
        y: numpy array of labels (N,).
        noise_level: Noise scale multiplier relative to standard deviation.
        num_augments: Number of augmented copies per original sample.
    
    Returns:
        tuple: (X_augmented, y_augmented) numpy arrays.
    """
    X_list = [X]
    y_list = [y]

    feature_stds = np.std(X, axis=0) + 1e-8

    for _ in range(num_augments):
        noise = np.random.normal(loc=0.0, scale=noise_level * feature_stds, size=X.shape)
        X_aug = X + noise
        X_list.append(X_aug)
        y_list.append(y)

    X_out = np.vstack(X_list).astype(np.float32)
    y_out = np.concatenate(y_list).astype(np.int32)

    # Shuffle
    shuffle_idx = np.random.permutation(len(y_out))
    return X_out[shuffle_idx], y_out[shuffle_idx]


def preprocess_data(data_dir='ml/data/processed', scaler_path='ml/models/scaler.pkl', augment=True):
    """
    Load data splits, fit scaler on train set, transform val and test sets, and return scaled data.
    """
    X_train = np.load(os.path.join(data_dir, 'X_train.npy'))
    y_train = np.load(os.path.join(data_dir, 'y_train.npy'))
    X_val = np.load(os.path.join(data_dir, 'X_val.npy'))
    y_val = np.load(os.path.join(data_dir, 'y_val.npy'))
    X_test = np.load(os.path.join(data_dir, 'X_test.npy'))
    y_test = np.load(os.path.join(data_dir, 'y_test.npy'))

    if augment:
        X_train, y_train = augment_feature_vectors(X_train, y_train, noise_level=0.02, num_augments=2)

    # Fit and apply standardization scaler
    scaler = FeatureScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    # Save scaler for prediction pipeline
    scaler.save(scaler_path)
    print(f"Fit feature scaler on train set and saved to: {scaler_path}")

    return X_train_scaled, y_train, X_val_scaled, y_val, X_test_scaled, y_test, scaler


if __name__ == '__main__':
    X_tr, y_tr, X_v, y_v, X_te, y_te, scaler = preprocess_data()
    print(f"Preprocessed Train shape: {X_tr.shape}, Val shape: {X_v.shape}, Test shape: {X_te.shape}")
