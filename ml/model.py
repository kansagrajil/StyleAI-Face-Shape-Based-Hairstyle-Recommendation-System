"""
TensorFlow / Keras Model Architectures for Face Shape Classification.
Includes:
  1. Dense Feature Neural Network (MLP) for landmark-derived geometric features.
  2. MobileNetV2 Transfer Learning CNN for image-based classification.
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, regularizers

# 7 Face shape categories
FACE_SHAPES = ['oval', 'round', 'square', 'heart', 'diamond', 'oblong', 'triangle']
NUM_CLASSES = len(FACE_SHAPES)


def build_feature_model(num_features=9, learning_rate=0.001, l2_reg=0.01):
    """
    Build a Deep Neural Network (MLP) for geometric landmark feature classification.
    
    Architecture:
        - Input: 9 normalized facial geometric ratios & angles
        - Dense(128, activation='relu') + BatchNormalization + Dropout(0.3) + L2(0.01)
        - Dense(64, activation='relu') + BatchNormalization + Dropout(0.3) + L2(0.01)
        - Dense(32, activation='relu') + BatchNormalization
        - Dense(6, activation='softmax')
    
    Args:
        num_features: Number of input features (default 9).
        learning_rate: Initial learning rate for Adam optimizer.
        l2_reg: L2 regularization strength.
    
    Returns:
        keras.Model: Compiled TensorFlow Keras model.
    """
    model = keras.Sequential([
        layers.Input(shape=(num_features,), name='geometric_features'),
        
        layers.Dense(128, activation='relu', kernel_regularizer=regularizers.l2(l2_reg), name='dense_1'),
        layers.BatchNormalization(name='bn_1'),
        layers.Dropout(0.3, name='dropout_1'),
        
        layers.Dense(64, activation='relu', kernel_regularizer=regularizers.l2(l2_reg), name='dense_2'),
        layers.BatchNormalization(name='bn_2'),
        layers.Dropout(0.3, name='dropout_2'),
        
        layers.Dense(32, activation='relu', name='dense_3'),
        layers.BatchNormalization(name='bn_3'),
        
        layers.Dense(NUM_CLASSES, activation='softmax', name='classification_output')
    ], name="FaceShapeFeatureClassifier")

    optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    return model


def build_cnn_model(input_shape=(224, 224, 3), learning_rate=0.0001):
    """
    Build a Transfer Learning CNN using MobileNetV2 backbone for direct image input.
    
    Args:
        input_shape: Image shape tuple (H, W, C).
        learning_rate: Learning rate for Adam optimizer.
    
    Returns:
        keras.Model: Compiled TensorFlow Keras model.
    """
    base_model = keras.applications.MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False

    model = keras.Sequential([
        layers.Input(shape=input_shape, name='image_input'),
        base_model,
        layers.GlobalAveragePooling2D(name='global_pooling'),
        layers.Dense(128, activation='relu', name='dense_1'),
        layers.Dropout(0.5, name='dropout_1'),
        layers.Dense(NUM_CLASSES, activation='softmax', name='classification_output')
    ], name="FaceShapeMobileNetV2")

    optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    return model


if __name__ == '__main__':
    model = build_feature_model(num_features=9)
    model.summary()
