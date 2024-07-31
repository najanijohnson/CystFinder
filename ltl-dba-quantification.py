import os
import csv
from roboflow import Roboflow

rf = Roboflow(api_key="y9we51qZweag8DJcdu4g")

project = rf.workspace().project("merge_0515-07222024_confocal")
model = project.version(1).model

# Define the classes as used in the API
api_classes = [
    "DBA-  mCherry-", 
    "DBA mCherry", 
    "LTL-  mCherry-", 
    "LTL- mCherry-", 
    "mCherry-  LTL- DBA-"
]

# Corresponding names for the CSV output
csv_classes = [
    "DBA+ mCherry+",
    "DBA+ mCherry-",
    "LTL+ mCherry+",
    "LTL+ mCherry-",
    "mCherry- LTL- DBA-"
]

# Define which classes are mCherry+ for LTL and DBA, NOT SURE IF THIS IS RIGHT bc had to change names of classes will ask about later
mCherry_LTL = ["LTL-  mCherry-", "mCherry-  LTL- DBA-"]
mCherry_DBA = ["DBA mCherry", "mCherry-  LTL- DBA-"]

# Define the folder containing images
#I'm going to make this a command input later this is just for troubleshooting purpises
image_folder = r"C:\Users\najan\OneDrive - University at Albany - SUNY\nephrogen\invivo folder"
output_folder = r"C:\Users\najan\OneDrive - University at Albany - SUNY\codez python\cyst_finder\output"
os.makedirs(output_folder, exist_ok=True)

# Initialize a summary list for the folder
folder_summary = []

# Process each image in the folder
for image_file in os.listdir(image_folder):
    if image_file.endswith(('.png', '.jpg', '.jpeg')):  # Add other image extensions if needed
        image_path = os.path.join(image_folder, image_file)
        
        # Predict on the image and save the annotated image
        results = model.predict(image_path, confidence=20).json()
        predictions = results.get('predictions', [])
        annotated_image_path = os.path.join(output_folder, f"{os.path.splitext(image_file)[0]}_annotated.jpg")
        model.predict(image_path, confidence=20).save(annotated_image_path)
        
        # Debugging 
        print(f"Full predictions for {image_file}: {predictions}")
        
        # Initialize counts for each class
        class_counts = {cls: 0 for cls in api_classes}
        LTL_mCherry_count = 0
        DBA_mCherry_count = 0
        
        # Count predictions per class
        for prediction in predictions:
            detected_class = prediction['class']
            if detected_class in class_counts:
                class_counts[detected_class] += 1
                if detected_class in mCherry_LTL:
                    LTL_mCherry_count += 1
                if detected_class in mCherry_DBA:
                    DBA_mCherry_count += 1
        
        # Calculate totals
        total_cells = sum(class_counts.values())
        LTL_percentage = (LTL_mCherry_count / total_cells * 100) if total_cells > 0 else 0
        DBA_percentage = (DBA_mCherry_count / total_cells * 100) if total_cells > 0 else 0
        
        # Append to folder summary
        row = {csv_classes[i]: class_counts[api_classes[i]] for i in range(len(api_classes))}
        row.update({'Image': image_file, 'LTL_percentage': LTL_percentage, 'DBA_percentage': DBA_percentage})
        folder_summary.append(row)

# Output the summary CSV for the entire folder
summary_csv_path = os.path.join(output_folder, "folder_summary.csv")
with open(summary_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Image'] + csv_classes + ['LTL_percentage', 'DBA_percentage']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(folder_summary)
