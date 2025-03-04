# Brain Tumor Detection Using Deep Learning

## Overview
This project presents a comparative analysis of high-performance deep learning models for the early detection of brain tumors using MRI (Magnetic Resonance Imaging) scans. The models evaluated include:
- **Xception**: 97.10% accuracy
- **VGG16**: 98.48% accuracy
- **InceptionV3**: 98.48% accuracy
- **DenseNet121**: 98.63% accuracy (Best Performing Model)

A **GridSearch optimization** approach was applied to the InceptionV3 model, optimizing parameters such as batch size, dropout rate, epochs, and learning rate for improved performance.

## Dataset
The dataset, obtained from **Kaggle**, consists of **7022 brain MRI images**, categorized into four classes:
- **Glioma**
- **Meningioma**
- **Pituitary**
- **Healthy**

### Preprocessing Steps
To enhance model generalization, the following preprocessing techniques were applied:
- **Rescaling**
- **Brightness augmentation**

## Model Optimization
A **GridSearch approach** was applied to optimize **InceptionV3**, with the best parameters identified as:
- **Batch Size:** 32
- **Dropout Rate:** 0.3
- **Epochs:** 10
- **Learning Rate:** 0.0001

## Results
Statistical analysis shows that deep learning models, particularly **DenseNet121**, significantly improve brain tumor classification accuracy. These models can aid in:
- **Early diagnosis** of brain tumors
- **Reducing diagnosis time**
- **Minimizing human-induced errors** in clinical decision-making



## Future Work
- Extend the dataset for improved generalization.
- Implement explainable AI techniques to provide insights into model decisions.
- Deploy as a web-based application for real-world usability.



---
### References
- Kaggle Dataset: [Brain MRI Images Dataset]([https://www.kaggle.com](https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset))

