import os
import csv
from roboflow import Roboflow
import shutil

# Initialize the Roboflow with your API key
rf = Roboflow(api_key="y9we51qZweag8DJcdu4g")  # Replace with your actual API key

# Access the specific project and version
project = rf.workspace().project("20240729_invivo18_miriam")
model = project.version(1).model

# Define the classes as used in the API
api_classes = ["mCherry-neg", "mCherry-pos"]

# Corresponding names for the CSV output
csv_classes = ["mCherry- Tubules", "mCherry+ Tubules"]

def process_images(input_path, output_folder):
    # Ensure the output folder is clear
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder, exist_ok=True)

    image_summary = []
    folder_summary = {}

    def process_image(image_path, output_dir, relative_path):
        # Predict on the image and save the annotated image
        results = model.predict(image_path, confidence=45).json()
        predictions = results.get('predictions', [])
        annotated_image_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(image_path))[0]}_annotated.jpg")
        model.predict(image_path, confidence=45).save(annotated_image_path)
        
        # Initialize counts for each class
        class_counts = {cls: 0 for cls in api_classes}
        
        # Count predictions per class
        for prediction in predictions:
            detected_class = prediction['class']
            if detected_class in class_counts:
                class_counts[detected_class] += 1
        
        # Calculate totals
        total_tubules = sum(class_counts.values())
        avg_mCherry_pos_percentage = (class_counts['mCherry-pos'] / total_tubules * 100) if total_tubules > 0 else 0

        # Prepare the row for image summary
        row = {csv_classes[i]: class_counts[api_classes[i]] for i in range(len(api_classes))}
        row.update({
            'Image': os.path.basename(image_path), 
            'Folder': relative_path, 
            'Total Tubules': total_tubules,
            'Avg % mCherry+ tubules': avg_mCherry_pos_percentage
        })
        image_summary.append(row)
        
        # Update folder summary
        if relative_path not in folder_summary:
            folder_summary[relative_path] = {
                'mCherry- Tubules': 0, 
                'mCherry+ Tubules': 0, 
                'Total Tubules': 0, 
                'Image Count': 0
            }
        for cls in csv_classes:
            folder_summary[relative_path][cls] += row[cls]
        folder_summary[relative_path]['Total Tubules'] += total_tubules
        folder_summary[relative_path]['Image Count'] += 1

    # Check if input is a directory or a single file
    if os.path.isdir(input_path):
        for root, dirs, files in os.walk(input_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp')):
                    image_path = os.path.join(root, file)
                    relative_dir = os.path.relpath(root, input_path)
                    output_dir = os.path.join(output_folder, relative_dir)
                    os.makedirs(output_dir, exist_ok=True)
                    process_image(image_path, output_dir, relative_dir)
    elif os.path.isfile(input_path) and input_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp')):
        process_image(input_path, output_folder, '')

    else:
        print("Invalid path. Please provide a valid folder or image file.")
        return False

    # Output the image summary CSV
    image_summary_csv_path = os.path.join(output_folder, "image_summary.csv")
    with open(image_summary_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Folder', 'Image'] + csv_classes + ['Total Tubules', 'Avg % mCherry+ tubules']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(image_summary)

    # Calculate additional statistics for the folder summary
    folder_summary_data = []
    for folder, counts in folder_summary.items():
        avg_mCherry_neg = counts['mCherry- Tubules'] / counts['Image Count']
        avg_mCherry_pos = counts['mCherry+ Tubules'] / counts['Image Count']
        avg_total_tubules = counts['Total Tubules'] / counts['Image Count']
        avg_mCherry_pos_percentage = (counts['mCherry+ Tubules'] / counts['Total Tubules'] * 100) if counts['Total Tubules'] > 0 else 0
        folder_summary_data.append({
            'Folder': folder,
            'mCherry- Tubules': counts['mCherry- Tubules'],
            'mCherry+ Tubules': counts['mCherry+ Tubules'],
            'Total Tubules': counts['Total Tubules'],
            'Avg mCherry+ tubules': avg_mCherry_pos,
            'Avg mCherry- tubules': avg_mCherry_neg,
            'Avg Total Tubules': avg_total_tubules,
            'Avg % mCherry+ tubules': avg_mCherry_pos_percentage
        })

    # Output the folder summary CSV
    folder_summary_csv_path = os.path.join(output_folder, "folder_summary.csv")
    with open(folder_summary_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'Folder', 'mCherry- Tubules', 'mCherry+ Tubules', 'Total Tubules',
            'Avg mCherry+ tubules', 'Avg mCherry- tubules',
            'Avg Total Tubules', 'Avg % mCherry+ tubules'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(folder_summary_data)
    
    return True

def main():
    while True:
        # Prompt user for input folder path or image file path
        input_path = input("Copy and paste the path of the folder or image you want to analyze: ").strip().strip('"')
        input_path = os.path.normpath(input_path)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_folder_path = os.path.join(script_dir, "mcherry_quantification_predictions")

        if process_images(input_path, output_folder_path):
            print(f"Processing complete. Results saved in: {output_folder_path}")
            break

if __name__ == "__main__":
    main()
