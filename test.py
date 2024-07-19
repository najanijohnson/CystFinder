import pandas as pd
import os
from roboflow import Roboflow
import math

# Initialize Roboflow with API key
rf = Roboflow(api_key="Hdgz6SQHEaK02L3AHHmH")
project = rf.workspace().project("4x_olympus_v1")
model = project.version(3).model

# Define the folder containing the images
input_folder_path = "C:\\Users\\najan\\Downloads\\test_images"
output_folder_path = "C:\\Users\\najan\\OneDrive - University at Albany - SUNY\\codez python\\test roboflow\\predictions"

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)
else:
    # Clear the output folder
    for file in os.listdir(output_folder_path):
        file_path = os.path.join(output_folder_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

# List all files in the input folder
image_files = [f for f in os.listdir(input_folder_path) if os.path.isfile(os.path.join(input_folder_path, f))]

# Initialize an empty list to collect all predictions
summary_data = []

# Loop through each image file and make predictions
for index, image_file in enumerate(image_files, start=1):
    image_path = os.path.join(input_folder_path, image_file)
    
    # Infer on the image
    predictions = model.predict(image_path, confidence=40, overlap=30).json()
    
    # Extract relevant data for calculations
    prediction_data = []
    for prediction in predictions['predictions']:
        prediction_data.append({
            "class": prediction['class'],
            "confidence": prediction['confidence'],
            "x": prediction['x'],
            "y": prediction['y'],
            "width": prediction['width'],
            "height": prediction['height']
        })
    
    # Convert to DataFrame
    df_predictions = pd.DataFrame(prediction_data)
    
    # Calculate average cyst size and number of cysts
    if not df_predictions.empty:
        df_predictions['Area'] = ((df_predictions['height'] + df_predictions['width']) / 4) ** 2 * math.pi
        avg_cyst_area = df_predictions['Area'].mean()
        num_cysts = len(df_predictions)
    else:
        avg_cyst_area = 0
        num_cysts = 0
    
    # Append summary data
    summary_data.append({
        "Image name": image_file,
        "avg cyst area": avg_cyst_area,
        "number of cysts": num_cysts
    })
    
    # Save the prediction image with a unique name
    output_image_path = os.path.join(output_folder_path, f"prediction_{image_file}.jpg")
    model.predict(image_path, confidence=40, overlap=30).save(output_image_path)

# Create a summary DataFrame
df_summary = pd.DataFrame(summary_data)

# Save the summary DataFrame to CSV
df_summary.to_csv(os.path.join(output_folder_path, "predictions_summary.csv"), index=False)
