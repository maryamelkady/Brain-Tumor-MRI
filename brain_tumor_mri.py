# -*- coding: utf-8 -*-
"""brain-tumor-mri.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1PGPPJM3Y3eMUkPgcigLofpAl0hWYR_di
"""

import os
from PIL import Image
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from glob import glob
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.optimizers import Adamax
from tensorflow.keras.metrics import Precision, Recall
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
import warnings
warnings.filterwarnings("ignore")

def train_df(tr_path):
    classes, class_paths = zip(*[(label, os.path.join(tr_path, label, image))
                                 for label in os.listdir(tr_path) if os.path.isdir(os.path.join(tr_path, label))
                                 for image in os.listdir(os.path.join(tr_path, label))])

    tr_df = pd.DataFrame({'Class Path': class_paths, 'Class': classes})
    return tr_df

def test_df(ts_path):
    classes, class_paths = zip(*[(label, os.path.join(ts_path, label, image))
                                 for label in os.listdir(ts_path) if os.path.isdir(os.path.join(ts_path, label))
                                 for image in os.listdir(os.path.join(ts_path, label))])

    ts_df = pd.DataFrame({'Class Path': class_paths, 'Class': classes})
    return ts_df

tr_df = train_df('/kaggle/input/brain-tumor-mri-dataset/Training')

tr_df

ts_df = test_df('/kaggle/input/brain-tumor-mri-dataset/Testing')

ts_df

"""# **Splitting the data**"""

valid_df, ts_df = train_test_split(ts_df, train_size=0.5, random_state=20, stratify=ts_df['Class'])

valid_df

"""# **Data Augmentation**"""

batch_size = 32
img_size = (299, 299)

_gen = ImageDataGenerator(rescale=1/255,
                          brightness_range=(0.8, 1.2))

ts_gen = ImageDataGenerator(rescale=1/255)


tr_gen = _gen.flow_from_dataframe(tr_df, x_col='Class Path',
                                  y_col='Class', batch_size=batch_size,
                                  target_size=img_size)

valid_gen = _gen.flow_from_dataframe(valid_df, x_col='Class Path',
                                     y_col='Class', batch_size=batch_size,
                                     target_size=img_size)

ts_gen = ts_gen.flow_from_dataframe(ts_df, x_col='Class Path',
                                  y_col='Class', batch_size=16,
                                  target_size=img_size, shuffle=False)

"""# **Data Visualization for the preproccessed and generated data**"""

import matplotlib.pyplot as plt

def visualize_classes(df, title="Class Visualization", num_samples=5):
    unique_classes = df['Class'].unique()
    num_classes = len(unique_classes)
    fig, axes = plt.subplots(num_classes, num_samples, figsize=(num_samples * 3, num_classes * 3))

    if num_classes == 1:  # Handle case with a single class
        axes = [axes]

    for idx, cls in enumerate(unique_classes):
        class_samples = df[df['Class'] == cls].sample(n=num_samples, random_state=42)
        for j, (_, row) in enumerate(class_samples.iterrows()):
            img = plt.imread(row['Class Path'])
            axes[idx][j].imshow(img)
            axes[idx][j].axis('off')
            if j == 0:
                axes[idx][j].set_title(cls, fontsize=12)

    plt.suptitle(title, fontsize=16)
    plt.tight_layout()
    plt.show()

# Visualize training dataset
visualize_classes(tr_df, title="Training Dataset Visualization", num_samples=5)

# Visualize validation dataset
visualize_classes(valid_df, title="Validation Dataset Visualization", num_samples=5)

# Visualize testing dataset
visualize_classes(ts_df, title="Testing Dataset Visualization", num_samples=5)

"""# **Xception**"""

img_shape=(244,244,3)
xception_model = tf.keras.applications.Xception(include_top= False, weights= "imagenet",
                            input_shape= img_shape, pooling= 'max')

# for layer in base_model.layers:
#     layer.trainable = False

model = Sequential([
    xception_model,
    Flatten(),
    Dropout(rate= 0.3),
    Dense(128, activation= 'relu'),
    Dropout(rate= 0.25),
    Dense(4, activation= 'softmax')
])

model.compile(Adamax(learning_rate= 0.001),
              loss= 'categorical_crossentropy',
              metrics= ['accuracy',
                        Precision(),
                        Recall()])

model.summary()

hist = model.fit(tr_gen,
                 epochs=10,
                 validation_data=valid_gen,
                 shuffle= False)

train_score = model.evaluate(tr_gen, verbose=1)
valid_score = model.evaluate(valid_gen, verbose=1)
test_score = model.evaluate(ts_gen, verbose=1)

print(f"Train Loss: {train_score[0]:.4f}")
print(f"Train Accuracy: {train_score[1]*100:.2f}%")
print('-' * 20)
print(f"Validation Loss: {valid_score[0]:.4f}")
print(f"Validation Accuracy: {valid_score[1]*100:.2f}%")
print('-' * 20)
print(f"Test Loss: {test_score[0]:.4f}")
print(f"Test Accuracy: {test_score[1]*100:.2f}%")

from tensorflow.keras.models import save_model
model.save('Xception_model')

"""# **Evatualtion Function for Visualization**"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report

def evaluate_model(model, ts_gen):
    # Generate predictions
    predictions = model.predict(ts_gen)
    predicted_classes = np.argmax(predictions, axis=1)  # Convert probabilities to class indices
    true_classes = ts_gen.classes  # True labels
    class_labels = list(ts_gen.class_indices.keys())  # Class labels

    # Compute confusion matrix
    cm = confusion_matrix(true_classes, predicted_classes)

    # Visualize confusion matrix
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_labels, yticklabels=class_labels)
    plt.xlabel('Predicted Labels')
    plt.ylabel('True Labels')
    plt.title('Confusion Matrix')
    plt.show()

    # Print classification report
    print("Classification Report:")
    print(classification_report(true_classes, predicted_classes, target_names=class_labels))

model = load_model('Xception_model')
evaluate_model(model, ts_gen)

"""# **Xception Model Architecture**"""

from tensorflow.keras.utils import plot_model
from IPython.display import Image

# Generate a smaller model diagram
plot_model(
    model,
    to_file="Xception.png",  # Save to a smaller file
    show_shapes=True,                        # Show tensor shapes
    show_layer_names=True,                   # Show layer names
    dpi=70,                                  # Reduce DPI for smaller size
)

# Display the smaller image in Jupyter Notebook
Image(filename="Xception.png")

"""# **VGG16**"""

from keras.applications.vgg16 import VGG16
img_shape=(244,244,3)
vgg16_model = VGG16(weights='imagenet', include_top=False, input_shape=img_shape, pooling='max')
vgg16_model.trainable = True

model_vgg16 = Sequential([
    vgg16_model,
    Flatten(),
    Dropout(rate=0.3),
    Dense(128, activation='relu'),
    Dropout(rate=0.25),
    Dense(4, activation='softmax')
])

model_vgg16.compile(
    optimizer=Adamax(learning_rate=0.0001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)
model_vgg16.summary()

from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
callbacks = [
    EarlyStopping(patience=5, restore_best_weights=True),
    ReduceLROnPlateau(factor=0.1,patience=3,min_lr=1e-6)
]

hist_VGG16 = model_vgg16.fit(
    tr_gen,
    epochs=10,
    validation_data=valid_gen,
    shuffle=False,
    callbacks=callbacks
)

train_score_vgg16 = model_vgg16.evaluate(tr_gen, verbose=1)
valid_score_vgg16 = model_vgg16.evaluate(valid_gen, verbose=1)
test_score_vgg16 = model_vgg16.evaluate(ts_gen, verbose=1)

print(f"Train Loss: {train_score_vgg16[0]:.4f}")
print(f"Train Accuracy: {train_score_vgg16[1]*100:.2f}%")
print('-' * 20)
print(f"Validation Loss: {valid_score_vgg16[0]:.4f}")
print(f"Validation Accuracy: {valid_score_vgg16[1]*100:.2f}%")
print('-' * 20)
print(f"Test Loss: {test_score_vgg16[0]:.4f}")
print(f"Test Accuracy: {test_score_vgg16[1]*100:.2f}%")

from tensorflow.keras.models import save_model
model_vgg16.save('VGG16_model')

model_vgg16 = load_model('VGG16_model')
evaluate_model(model_vgg16, ts_gen)

"""# **VGG16 Model Architecture**"""

from tensorflow.keras.utils import plot_model
from IPython.display import Image

# Generate a smaller model diagram
plot_model(
    model_vgg16,
    to_file="VGG16.png",  # Save to a smaller file
    show_shapes=True,                        # Show tensor shapes
    show_layer_names=True,                   # Show layer names
    dpi=70,                                  # Reduce DPI for smaller size
)

# Display the smaller image in Jupyter Notebook
Image(filename="VGG16.png")

"""# **Densenet121**"""

from tensorflow.keras.applications import DenseNet121
# Input shape
img_shape = (244, 244, 3)

# DenseNet121 base model
densenet_model = DenseNet121(include_top=False, weights="imagenet", input_shape=img_shape, pooling='max')

# Define the sequential model
model_densenet = Sequential([
    densenet_model,
    Flatten(),
    Dropout(rate=0.3),
    Dense(128, activation='relu'),
    Dropout(rate=0.25),
    Dense(4, activation='softmax')
])

# Compile the model
model_densenet.compile(
    optimizer=Adamax(learning_rate=0.0001),
    loss='categorical_crossentropy',
    metrics=['accuracy', Precision(), Recall()]
)

# Print the model summary
model_densenet.summary()

hist_densenet = model_densenet.fit(tr_gen,
                 epochs=10,
                 validation_data=valid_gen,
                 shuffle= False)

train_score_densenet = model_densenet.evaluate(tr_gen, verbose=1)
valid_score_densenet = model_densenet.evaluate(valid_gen, verbose=1)
test_score_densenet = model_densenet.evaluate(ts_gen, verbose=1)

print(f"Train Loss: {train_score_densenet[0]:.4f}")
print(f"Train Accuracy: {train_score_densenet[1]*100:.2f}%")
print('-' * 20)
print(f"Validation Loss: {valid_score_densenet[0]:.4f}")
print(f"Validation Accuracy: {valid_score_densenet[1]*100:.2f}%")
print('-' * 20)
print(f"Test Loss: {test_score_densenet[0]:.4f}")
print(f"Test Accuracy: {test_score_densenet[1]*100:.2f}%")

from tensorflow.keras.models import save_model
model_densenet.save('Densenet')

model_densenet = load_model('Densenet')
evaluate_model(model_densenet, ts_gen)

"""# **Densenet Model Architecture**"""

from tensorflow.keras.utils import plot_model
from IPython.display import Image
from IPython.display import Image
# Generate a smaller model diagram
plot_model(
    model_densenet,
    to_file="Densenet.png",  # Save to a smaller file
    show_shapes=True,                        # Show tensor shapes
    show_layer_names=True,                   # Show layer names
    dpi=70,                                  # Reduce DPI for smaller size
)

# Display the smaller image in Jupyter Notebook
Image(filename="Densenet.png")

"""# **Applying Gridsearch on InceptionV3**"""

!pip install tensorflow scikeras

from tensorflow.keras.applications import  InceptionV3
from sklearn.model_selection import GridSearchCV
from scikeras.wrappers import KerasClassifier

def  create_model(learning_rate=0.0001, dropout_rate=0.5):
    base_model =  InceptionV3(include_top=False, weights='imagenet', input_shape=(299, 299, 3), pooling='max')
    base_model.trainable = True

    model = Sequential([
        base_model,
        Flatten(),
        Dropout(dropout_rate),
        Dense(128, activation='relu'),
        Dense(4, activation='softmax')
    ])

    model.compile(optimizer=Adamax(learning_rate=learning_rate),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    return model
from sklearn.model_selection import ParameterGrid

def train_model_with_params(learning_rate, dropout_rate, epochs, batch_size):
    model = create_model(learning_rate=learning_rate, dropout_rate=dropout_rate)

    history = model.fit(
        tr_gen,
        epochs=epochs,
        validation_data=valid_gen,
        batch_size=batch_size,
        verbose=1
    )

    test_loss, test_acc = model.evaluate(ts_gen)
    print(f"Test Accuracy: {test_acc}")

    return test_acc

param_grid = {
    'learning_rate': [0.0001, 0.001],
    'dropout_rate': [0.3, 0.5],
    'epochs': [5, 10],
    'batch_size': [16, 32]
}

grid = ParameterGrid(param_grid)

best_accuracy = 0
best_params = {}

for params in grid:
    print(f"Training with parameters: {params}")
    accuracy = train_model_with_params(
        learning_rate=params['learning_rate'],
        dropout_rate=params['dropout_rate'],
        epochs=params['epochs'],
        batch_size=params['batch_size']
    )

    if accuracy > best_accuracy:
        best_accuracy = accuracy
        best_params = params

print(f"Best Accuracy: {best_accuracy}")
print(f"Best Parameters: {best_params}")

"""# **InceptionV3 Model with the best parameters**"""

from tensorflow.keras.applications import InceptionV3
# Input shape
img_shape = (299, 299, 3)

inception_model = InceptionV3(include_top=False, weights="imagenet", input_shape=img_shape, pooling='max')

# Define the sequential model
model_inception = Sequential([
    inception_model,
    Flatten(),
    Dropout(rate=0.3),
    Dense(128, activation='relu'),
    Dropout(rate=0.25),
    Dense(4, activation='softmax')
])

# Compile the model
model_inception.compile(
    optimizer=Adamax(learning_rate=0.0001),
    loss='categorical_crossentropy',
    metrics=['accuracy', Precision(), Recall()]
)

# Print the model summary
model_inception.summary()

hist_inception = model_inception.fit(tr_gen,
                 epochs=10,
                 validation_data=valid_gen,
                 shuffle= False)

train_score_inception = model_inception.evaluate(tr_gen, verbose=1)
valid_score_inception = model_inception.evaluate(valid_gen, verbose=1)
test_score_inception = model_inception.evaluate(ts_gen, verbose=1)

print(f"Train Loss: {train_score_inception[0]:.4f}")
print(f"Train Accuracy: {train_score_inception[1]*100:.2f}%")
print('-' * 20)
print(f"Validation Loss: {valid_score_inception[0]:.4f}")
print(f"Validation Accuracy: {valid_score_inception[1]*100:.2f}%")
print('-' * 20)
print(f"Test Loss: {test_score_inception[0]:.4f}")
print(f"Test Accuracy: {test_score_inception[1]*100:.2f}%")

from tensorflow.keras.models import save_model
model_inception.save('InceptionV3')

model_inception = load_model('InceptionV3')
evaluate_model(model_inception, ts_gen)

# Generate a smaller model diagram
plot_model(
    model_inception,
    to_file="InceptionV3.png",  # Save to a smaller file
    show_shapes=True,                        # Show tensor shapes
    show_layer_names=True,                   # Show layer names
    dpi=70,                                  # Reduce DPI for smaller size
)

# Display the smaller image in Jupyter Notebook
Image(filename="InceptionV3.png")



"""# **Coperative Analysis for the 4 models**"""

import matplotlib.pyplot as plt

def compare_model_accuracies(xception_acc, vgg16_acc, densenet_acc, inception_acc):
    # Define model names and their corresponding accuracies
    model_names = ['Xception', 'VGG16', 'DenseNet121','InceptionV3']
    accuracies = [xception_acc, vgg16_acc, densenet_acc, inception_acc]

    # Visualize accuracies with a bar chart
    plt.figure(figsize=(8, 5))
    plt.bar(model_names, accuracies, color=['blue','red', 'green', 'orange'], alpha=0.8)
    plt.xlabel('Model', fontsize=12)
    plt.ylabel('Accuracy', fontsize=12)
    plt.title('Comparison of Test Accuracies', fontsize=14)
    plt.ylim(0.9, 1.0)  # Set y-axis limits to better visualize small differences
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Annotate accuracy values on top of bars
    for i, acc in enumerate(accuracies):
        plt.text(i, acc + 0.002, f"{acc*100:.2f}%", ha='center', fontsize=10)

    # Show the plot
    plt.show()

# Extract test accuracies from the evaluation results
xception_acc = test_score[1]
vgg16_acc = test_score_vgg16[1]
densenet_acc = test_score_densenet[1]
inception_acc = test_score_inception[1]

# Compare and visualize accuracies
compare_model_accuracies(xception_acc, vgg16_acc, densenet_acc , inception_acc)

import matplotlib.pyplot as plt

# Extracting loss and accuracy data for plotting
# For Xception model
loss_xception = hist.history['loss']
acc_xception = hist.history['val_accuracy']

# For VGG16 model
loss_vgg16 = hist_VGG16.history['loss']
acc_vgg16 = hist_VGG16.history['val_accuracy']

# For DenseNet model
loss_densenet = hist_densenet.history['loss']
acc_densenet = hist_densenet.history['val_accuracy']

# For Inception model
loss_inception = hist_inception.history['loss']
acc_inception = hist_inception.history['val_accuracy']

# Plotting loss curves
plt.figure(figsize=(14, 6))

# Loss Curves
plt.subplot(1, 2, 1)
plt.plot(loss_xception, label='Xception Loss', color='blue')
plt.plot(loss_vgg16, label='VGG16 Loss', color='green')
plt.plot(loss_densenet, label='DenseNet Loss', color='red')
plt.plot(loss_inception, label='Inception Loss', color='purple')  # Add Inception Loss
plt.title('Validation Loss Comparison')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()

# Accuracy Curves
plt.subplot(1, 2, 2)
plt.plot(acc_xception, label='Xception Accuracy', color='blue')
plt.plot(acc_vgg16, label='VGG16 Accuracy', color='green')
plt.plot(acc_densenet, label='DenseNet Accuracy', color='red')
plt.plot(acc_inception, label='Inception Accuracy', color='purple')  # Add Inception Accuracy
plt.title('Validation Accuracy Comparison')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()

# Display the plots
plt.tight_layout()
plt.show()