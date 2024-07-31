import pandas as pd
import os
from roboflow import Roboflow
import math
import shutil

#merge_keyence-olympus-parnell
# Initialize Roboflow with API key
rf = Roboflow(api_key="Hdgz6SQHEaK02L3AHHmH")
project = rf.workspace().project("merge_keyence-olympus-parnell")
model = project.version(1).model

def process_images(input_folder_path, output_folder_path):
    # Clear the output folder if it exists, otherwise create it
    if os.path.exists(output_folder_path):
        shutil.rmtree(output_folder_path)
    os.makedirs(output_folder_path)

    summary_data = []
    all_folders_data = []
    consolidated_analysis_data = []
    raw_analysis_data = []

    images_processed = False

    def process_image(image_path, output_dir, relative_path):
        nonlocal images_processed
        images_processed = True
        predictions = model.predict(image_path, confidence=40, overlap=30).json()

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

        df_predictions = pd.DataFrame(prediction_data)

        if not df_predictions.empty:
            df_predictions['Area'] = ((df_predictions['height'] + df_predictions['width']) / 4) ** 2 * math.pi
            avg_cyst_area = df_predictions['Area'].mean()
            std_dev_cyst_area = df_predictions['Area'].std()
            num_cysts = len(df_predictions)

            # Add individual cyst areas to raw analysis data
            for area in df_predictions['Area']:
                raw_analysis_data.append({
                    "folder name": relative_path,
                    "Image name": os.path.join(relative_path, os.path.basename(image_path)),
                    "cyst area": area
                })
        else:
            avg_cyst_area = 0
            std_dev_cyst_area = 0
            num_cysts = 0

        summary_data.append({
            "Image name": os.path.join(relative_path, os.path.basename(image_path)),
            "avg cyst area": avg_cyst_area,
            "std dev cyst area": std_dev_cyst_area,
            "number of cysts": num_cysts
        })

        # Save the output image with predictions
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_image_path = os.path.join(output_dir, f"prediction_{os.path.basename(image_path)}")
        model.predict(image_path, confidence=40, overlap=30).save(output_image_path)

        return df_predictions

    if os.path.isdir(input_folder_path):
        for root, dirs, files in os.walk(input_folder_path):
            relative_path = os.path.relpath(root, input_folder_path)
            
            # Skip creating a new folder for the root path
            if relative_path == '.':
                continue

            # Create the new folder name with '_prediction' suffix
            new_relative_path = f"{relative_path}_prediction"
            output_dir = os.path.join(output_folder_path, new_relative_path)

            folder_areas = []
            folder_cyst_counts = []

            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(root, file)
                    df_predictions = process_image(image_path, output_dir, new_relative_path)

                    if not df_predictions.empty:
                        folder_areas.extend(df_predictions['Area'].tolist())
                        folder_cyst_counts.append(len(df_predictions))
                    else:
                        folder_cyst_counts.append(0)

            # Store folder summary data if there are images
            if folder_areas:
                all_folders_data.append((folder_areas, folder_cyst_counts, new_relative_path, output_dir))

    elif os.path.isfile(input_folder_path) and input_folder_path.lower().endswith(('.jpg', '.jpeg', '.png')):
        relative_path = os.path.splitext(os.path.basename(input_folder_path))[0] + "_prediction"
        output_dir = os.path.join(output_folder_path, relative_path)
        df_predictions = process_image(input_folder_path, output_dir, relative_path)
        if not df_predictions.empty:
            all_folders_data.append((df_predictions['Area'].tolist(), [len(df_predictions)], relative_path, output_dir))

    else:
        print("Invalid path. Please provide a folder or an image file.")
        return False

    if not images_processed:
        print("Sorry, no valid images found in the provided path. Please try again.")
        return False

    # Save consolidated raw data
    df_summary = pd.DataFrame(summary_data)
    df_summary.to_csv(os.path.join(output_folder_path, "avg_cysts_per_image.csv"), index=False)
    
    # Save analysis for each folder and collect data for consolidated analysis only if it's folder input
    if os.path.isdir(input_folder_path):
        for folder_areas, folder_cyst_counts, new_relative_path, output_dir in all_folders_data:
            if folder_areas:
                overall_avg_cyst_area = sum(folder_areas) / len(folder_areas)
                overall_std_dev_cyst_area = pd.Series(folder_areas).std()
                avg_cysts_per_image = sum(folder_cyst_counts) / len(folder_cyst_counts)  # Including zeros
                total_cysts = sum(folder_cyst_counts)
            else:
                overall_avg_cyst_area = 0
                overall_std_dev_cyst_area = 0
                avg_cysts_per_image = 0
                total_cysts = 0
            
            analysis_data = {
                "folder name": new_relative_path,
                "Overall avg cyst area": overall_avg_cyst_area,
                "Overall std dev cyst area": overall_std_dev_cyst_area,
                "Avg cysts per image": avg_cysts_per_image,
                "Total cysts": total_cysts
            }
            consolidated_analysis_data.append(analysis_data)

        # Save consolidated analysis data
        df_consolidated_analysis = pd.DataFrame(consolidated_analysis_data)
        df_consolidated_analysis.to_csv(os.path.join(output_folder_path, "avg_cysts_per_folder.csv"), index=False)

    # Save raw analysis data
    df_raw_analysis = pd.DataFrame(raw_analysis_data)
    df_raw_analysis.to_csv(os.path.join(output_folder_path, "all_cysts.csv"), index=False)

    return True

def main():
    while True:
        # Prompt user for input folder path or image file path
        input_path = input("Copy and paste the path of the folder or image you want to analyze: ")
        input_path = input_path.strip().strip('"')  # Remove any quotation marks and strip whitespace
        input_path = os.path.normpath(input_path)  
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory where the script is located
        output_folder_path = os.path.join(script_dir, "predictions")  # Set output folder to be within the script directory

        if process_images(input_path, output_folder_path):
            print(f"Processing complete. Results saved in: {output_folder_path}")
            break

if __name__ == "__main__":
    main() 
