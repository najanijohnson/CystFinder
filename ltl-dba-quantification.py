import os
import csv
from roboflow import Roboflow
import shutil

# Initialize the Roboflow client with your API key
rf = Roboflow(api_key="y9we51qZweag8DJcdu4g")

# Access the specific project and version
project = rf.workspace().project("merge_0515-07222024_confocal")
model = project.version(1).model

# Define the classes as used in the API
api_classes = [
    "DBA- mCherry-", 
    "DBA-  mCherry-", 
    "LTL-  mCherry-", 
    "LTL- mCherry-", 
    "mCherry-  LTL- DBA-"
]

# Corresponding names for the CSV output
csv_classes = [
    "# DBA+ mCherry+ tubules",
    "# DBA+ mCherry- tubules",
    "# LTL+ mCherry+ tubules",
    "# LTL+ mCherry- tubules",
    "# mCherry+ LTL- DBA- tubules"
]

# Define which classes are mCherry+ for LTL and DBA
mCherry_LTL = ["LTL-  mCherry-", "mCherry-  LTL- DBA-"]
mCherry_DBA = ["DBA-  mCherry-", "mCherry-  LTL- DBA-"]

def process_images(input_path, output_folder):
    # Ensure the output folder is clear
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder, exist_ok=True)

    image_summary = []
    folder_summary = {}

    def process_image(image_path, output_dir, relative_path):
        # Predict on the image and save the annotated image
        results = model.predict(image_path, confidence=35).json()
        predictions = results.get('predictions', [])
        annotated_image_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(image_path))[0]}_annotated.jpg")
        model.predict(image_path, confidence=35).save(annotated_image_path)
        
        # Initialize counts for each class
        class_counts = {cls: 0 for cls in api_classes}
        LTL_mCherry_count = 0
        DBA_mCherry_count = 0
        LTL_DBA_mCherry_count = 0
        total_DBA_tubules = 0
        total_LTL_tubules = 0
        
        # Count predictions per class
        for prediction in predictions:
            detected_class = prediction['class']
            if detected_class in class_counts:
                class_counts[detected_class] += 1
                if detected_class in mCherry_LTL:
                    LTL_mCherry_count += 1
                if detected_class in mCherry_DBA:
                    DBA_mCherry_count += 1
                if detected_class == "mCherry-  LTL- DBA-":
                    LTL_DBA_mCherry_count += 1
                if 'DBA' in detected_class:
                    total_DBA_tubules += 1
                if 'LTL' in detected_class:
                    total_LTL_tubules += 1
        
        # Calculate totals
        total_tubules = sum(class_counts.values())
        LTL_percentage = (class_counts["LTL- mCherry-"] / total_tubules * 100) if total_tubules > 0 else 0
        DBA_percentage = (class_counts["DBA- mCherry-"] / total_tubules * 100) if total_tubules > 0 else 0
        LTL_DBA_percentage = (LTL_DBA_mCherry_count / total_tubules * 100) if total_tubules > 0 else 0
        
        # Prepare the row for image summary
        row = {csv_classes[i]: class_counts[api_classes[i]] for i in range(len(api_classes))}
        row.update({
            'Image': os.path.basename(image_path),
            'Folder': relative_path,
            'Total tubules': total_tubules,
            '# DBA tubules': total_DBA_tubules,
            '# LTL tubules': total_LTL_tubules,
            '% mCherry+ LTL+ tubules': LTL_percentage,
            '% mCherry+ DBA+ tubules': DBA_percentage,
            '% mCherry+ LTL- DBA- tubules': LTL_DBA_percentage
        })
        image_summary.append(row)
        
        # Update folder summary
        if relative_path not in folder_summary:
            folder_summary[relative_path] = {cls: 0 for cls in csv_classes}
            folder_summary[relative_path]['Total tubules'] = 0
            folder_summary[relative_path]['LTL mCherry Count'] = 0
            folder_summary[relative_path]['DBA mCherry Count'] = 0
            folder_summary[relative_path]['LTL DBA mCherry Count'] = 0
            folder_summary[relative_path]['# DBA tubules'] = 0
            folder_summary[relative_path]['# LTL tubules'] = 0
        for cls in api_classes:
            csv_class = csv_classes[api_classes.index(cls)]
            folder_summary[relative_path][csv_class] += class_counts[cls]
        folder_summary[relative_path]['Total tubules'] += total_tubules
        folder_summary[relative_path]['LTL mCherry Count'] += LTL_mCherry_count
        folder_summary[relative_path]['DBA mCherry Count'] += DBA_mCherry_count
        folder_summary[relative_path]['LTL DBA mCherry Count'] += LTL_DBA_mCherry_count
        folder_summary[relative_path]['# DBA tubules'] += total_DBA_tubules
        folder_summary[relative_path]['# LTL tubules'] += total_LTL_tubules

    # Check if input is a directory or a single file
    if os.path.isdir(input_path):
        for root, dirs, files in os.walk(input_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg','.bmp', '.webp')):
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
        fieldnames = ['Folder', 'Image'] + csv_classes + [
            'Total tubules', '# DBA tubules', '# LTL tubules', '% mCherry+ LTL+ tubules', '% mCherry+ DBA+ tubules', '% mCherry+ LTL- DBA- tubules'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(image_summary)

    # Calculate percentages for folder summary
    folder_summary_data = []
    for folder, counts in folder_summary.items():
        total_tubules = counts['Total tubules']
        LTL_percentage = (counts['# LTL+ mCherry+ tubules'] / total_tubules * 100) if total_tubules > 0 else 0
        DBA_percentage = (counts['# DBA+ mCherry+ tubules'] / total_tubules * 100) if total_tubules > 0 else 0
        LTL_DBA_percentage = (counts['# mCherry+ LTL- DBA- tubules'] / total_tubules * 100) if total_tubules > 0 else 0
        row = {
            'Folder': folder,
            '% mCherry+ LTL+ tubules': LTL_percentage,
            '% mCherry+ DBA+ tubules': DBA_percentage,
            '% mCherry+ LTL- DBA- tubules': LTL_DBA_percentage,
            'Total tubules': total_tubules,
            '# DBA tubules': counts['# DBA tubules'],
            '# LTL tubules': counts['# LTL tubules']
        }
        row.update({cls: counts[cls] for cls in csv_classes})
        folder_summary_data.append(row)

    # Output the folder summary CSV
    folder_summary_csv_path = os.path.join(output_folder, "folder_summary.csv")
    with open(folder_summary_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Folder'] + csv_classes + [
            'Total tubules', '# DBA tubules', '# LTL tubules', '% mCherry+ LTL+ tubules', '% mCherry+ DBA+ tubules', '% mCherry+ LTL- DBA- tubules'
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
        output_folder_path = os.path.join(script_dir, "ltl-dba_quantification_predictions")

        if process_images(input_path, output_folder_path):
            print(f"Processing complete. Results saved in: {output_folder_path}")
            break

if __name__ == "__main__":
    main()
