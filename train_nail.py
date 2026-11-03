import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout, BatchNormalization
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import RMSprop

# Folders 
train_dir = "dataset_nail/train"
test_dir = "dataset_nail/test"

# Data Augmentation
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    zoom_range=0.3,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True,
    fill_mode='nearest'
)

test_datagen = ImageDataGenerator(rescale=1./255)

# Load Data
train_data = train_datagen.flow_from_directory(
    train_dir, target_size=(160, 160), batch_size=4, class_mode='binary', shuffle=True
)

test_data = test_datagen.flow_from_directory(
    test_dir, target_size=(160, 160), batch_size=4, class_mode='binary', shuffle=False
)

print("Nail Class Indices:", train_data.class_indices)

# Model Building
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(160, 160, 3))
base_model.trainable = True 
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = BatchNormalization()(x)
x = Dense(64, activation='relu')(x)
x = Dropout(0.3)(x)
predictions = Dense(1, activation='sigmoid')(x)

model = Model(inputs=base_model.input, outputs=predictions)

# Compile
model.compile(optimizer=RMSprop(learning_rate=0.00001), loss='binary_crossentropy', metrics=['accuracy'])

# Train
print("Nail Training started...")
model.fit(train_data, validation_data=test_data, epochs=50)

# Save
os.makedirs("model", exist_ok=True)
model.save("model/nail_model.h5")
print("Nail model saved successfully at 'model/nail_model.h5' ✅")