"""
Data Preprocessing Pipeline.
Handles data augmentation and preprocessing for the face shape dataset.
Prepares training data for the TensorFlow classifier.
"""

import os
import cv2
import numpy as np
from pathlib import Path


# Face shape categories
FACE_SHAPES = ['oval', 'round', 'square', 'heart', 'oblong', 'diamond', 'triangle']
TARGET_SIZE = (224, 224)


def load_dataset(data_dir, target_size=TARGET_SIZE):
    """
    Load images from a directory structure:
        data_dir/
            oval/
                img001.jpg
                img002.jpg
            round/
                img001.jpg
            ...
    
    Args:
        data_dir: Path to the dataset root.
        target_size: (width, height) to resize images to.
    
    Returns:
        tuple: (images array, labels array, label_names list)
    """
    images = []
    labels = []

    for idx, shape in enumerate(FACE_SHAPES):
        shape_dir = os.path.join(data_dir, shape)
        if not os.path.exists(shape_dir):
            print(f"Warning: Directory not found: {shape_dir}")
            continue

        for img_name in os.listdir(shape_dir):
            img_path = os.path.join(shape_dir, img_name)
            img = cv2.imread(img_path)
            if img is None:
                continue

            # Preprocess
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
            img = img.astype(np.float32) / 255.0

            images.append(img)
            labels.append(idx)

    return np.array(images), np.array(labels), FACE_SHAPES


def augment_image(image):
    """
    Apply random augmentation to a single image for training variety.
    
    Augmentations applied:
        - Random horizontal flip (50% chance)
        - Random brightness adjustment (±20%)
        - Random rotation (±15 degrees)
        - Random zoom (90-110%)
    
    Args:
        image: numpy array (H × W × 3), float32, range [0, 1].
    
    Returns:
        numpy.ndarray: Augmented image.
    """
    h, w = image.shape[:2]

    # Random horizontal flip
    if np.random.random() > 0.5:
        image = cv2.flip(image, 1)

    # Random brightness
    brightness = np.random.uniform(0.8, 1.2)
    image = np.clip(image * brightness, 0, 1)

    # Random rotation (-15 to +15 degrees)
    angle = np.random.uniform(-15, 15)
    matrix = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    image = cv2.warpAffine(image, matrix, (w, h), borderMode=cv2.BORDER_REFLECT)

    # Random zoom (90% - 110%)
    scale = np.random.uniform(0.9, 1.1)
    new_h, new_w = int(h * scale), int(w * scale)
    image = cv2.resize(image, (new_w, new_h))

    # Crop/pad back to original size
    if scale > 1:
        start_y = (new_h - h) // 2
        start_x = (new_w - w) // 2
        image = image[start_y:start_y + h, start_x:start_x + w]
    else:
        pad_y = (h - new_h) // 2
        pad_x = (w - new_w) // 2
        padded = np.zeros((h, w, 3), dtype=np.float32)
        padded[pad_y:pad_y + new_h, pad_x:pad_x + new_w] = image
        image = padded

    return image


def create_augmented_dataset(images, labels, augmentations_per_image=5):
    """
    Create an augmented version of the dataset.
    
    Args:
        images: numpy array of images.
        labels: numpy array of labels.
        augmentations_per_image: Number of augmented copies per original.
    
    Returns:
        tuple: (augmented_images, augmented_labels)
    """
    aug_images = list(images)
    aug_labels = list(labels)

    for img, label in zip(images, labels):
        for _ in range(augmentations_per_image):
            aug_img = augment_image(img.copy())
            aug_images.append(aug_img)
            aug_labels.append(label)

    # Shuffle
    combined = list(zip(aug_images, aug_labels))
    np.random.shuffle(combined)
    aug_images, aug_labels = zip(*combined)

    return np.array(aug_images), np.array(aug_labels)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Preprocess face shape dataset')
    parser.add_argument('--data-dir', type=str, default='ml/data/raw',
                        help='Path to raw dataset')
    parser.add_argument('--output-dir', type=str, default='ml/data/processed',
                        help='Path to save processed data')
    parser.add_argument('--augment', type=int, default=5,
                        help='Augmentations per image')
    args = parser.parse_args()

    print(f"Loading dataset from {args.data_dir}...")
    images, labels, names = load_dataset(args.data_dir)
    print(f"Loaded {len(images)} images across {len(set(labels))} classes")

    print(f"Augmenting with {args.augment}x per image...")
    aug_images, aug_labels = create_augmented_dataset(images, labels, args.augment)
    print(f"Augmented dataset: {len(aug_images)} images")

    # Save processed data
    os.makedirs(args.output_dir, exist_ok=True)
    np.save(os.path.join(args.output_dir, 'images.npy'), aug_images)
    np.save(os.path.join(args.output_dir, 'labels.npy'), aug_labels)
    print(f"Saved to {args.output_dir}/")
