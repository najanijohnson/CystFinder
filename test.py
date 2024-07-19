import pandas as pd
import os
from roboflow import Roboflow
import math
import shutil

# Initialize Roboflow with API key
rf = Roboflow(api_key="Hdgz6SQHEaK02L3AHHmH")
project = rf.workspace().project("4x_olympus_v1")
model = project.version(3).model

def process_images(input_folder_path, output_folder_path):
    # Clear the output folder if it exists, otherwise create it
    if os.path.exists(output_folder_path):
        shutil.rmtree(output_folder_path)
    os.makedirs(output_folder_path)

    summary_data = []
    all_folders_data = []
    consolidated_analysis_data = []

    for root, dirs, files in os.walk(input_folder_path):
        relative_path = os.path.relpath(root, input_folder_path)
        output_dir = os.path.join(output_folder_path, relative_path)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        folder_areas = []
        folder_cyst_counts = []
        folder_summary_data = []

        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(root, file)
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
                    folder_areas.extend(df_predictions['Area'].tolist())
                    folder_cyst_counts.append(num_cysts)
                else:
                    avg_cyst_area = 0
                    std_dev_cyst_area = 0
                    num_cysts = 0
                    folder_cyst_counts.append(0)
                
                summary_data.append({
                    "Image name": os.path.join(relative_path, file),
                    "avg cyst area": avg_cyst_area,
                    "std dev cyst area": std_dev_cyst_area,
                    "number of cysts": num_cysts
                })
                
                folder_summary_data.append({
                    "Image name": os.path.join(relative_path, file),
                    "avg cyst area": avg_cyst_area,
                    "std dev cyst area": std_dev_cyst_area,
                    "number of cysts": num_cysts
                })
                
                output_image_path = os.path.join(output_dir, f"prediction_{file}")
                model.predict(image_path, confidence=40, overlap=30).save(output_image_path)
        
        # Store folder summary data
        if folder_summary_data:
            all_folders_data.append((folder_areas, folder_cyst_counts, relative_path, output_dir))

    # Save consolidated raw data
    df_summary = pd.DataFrame(summary_data)
    df_summary.to_csv(os.path.join(output_folder_path, "raw_data.csv"), index=False)
    
    # Save analysis for each folder and collect data for consolidated analysis
    for folder_areas, folder_cyst_counts, relative_path, output_dir in all_folders_data:
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
            "folder name": relative_path,
            "Overall avg cyst area": overall_avg_cyst_area,
            "Overall std dev cyst area": overall_std_dev_cyst_area,
            "Avg cysts per image": avg_cysts_per_image,
            "Total cysts": total_cysts
        }
        consolidated_analysis_data.append(analysis_data)

    # Save consolidated analysis data
    df_consolidated_analysis = pd.DataFrame(consolidated_analysis_data)
    df_consolidated_analysis.to_csv(os.path.join(output_folder_path, "analysis.csv"), index=False)

def main():
    input_folder_path = "C:\\Users\\najan\\Downloads\\Archive"
    output_folder_path = "C:\\Users\\najan\\OneDrive - University at Albany - SUNY\\codez python\\cyst_finder\\predictions"
    process_images(input_folder_path, output_folder_path)

if __name__ == "__main__":
    main()
