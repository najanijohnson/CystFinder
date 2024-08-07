This project contains various scripts and ImageJ macros for processing and analyzing image files related to cyst and tubule identification and quantification.

## Scripts and Macros

### `cyst_finder.py`
This script processes images to identify and quantify cysts.

Usage:
python cyst_finder.py 
- After you run the file, it will prompt you for an input_path
- `input_path`: Path to a single image file or a directory containing multiple images.
- `output_directory`: Path to the directory where the processed images and results will be saved. Note this will be where the repo is saved on your device.

### `ltl-dba-quantification.py`
 This script is designed to quantify LTL+ and DBA+ kidney tubules in microscopy slides stained with LTL (GFP), DBA (Cy5), and mCherry (injected cargo of interest). DAPI is also shown in blue.

python ltl-dba-quantification.py 
- After you run the file, it will prompt you for an input_path
- `input_path`: Path to a single image file or a directory containing multiple images.
- `output_directory`: Path to the directory where the processed images and results will be saved. Note this will be where the repo is saved on your device.

### `mcherry_quantification.py`
This script is designed to quantify mCherry+ kidney tubules in microscopy slides. Themcherry_quantification.ijm macro should be used to create the images to run with this script.

Usage:
python mcherry_quantification.py
- After you run the file, it will prompt you for an input_path
- `input_path`: Path to a single image file or a directory containing multiple images.
- `output_directory`: Path to the directory where the processed images and results will be saved. Note this will be where the repo is saved on your device.

### `Macro.ijm`
This ImageJ macro converts all TIFF images in a folder into JPEG format.

Usage:
1. Open ImageJ.
2. Navigate to File -> Open, and then open this file on your device
3. Navigate to where it says "// Define input and output directories" and replace my directories with the ones on your device that you want to convert.
4. Run the macro by pressing the run button in ImageJ.
5. The macro will process the images and save the converted JPEGs in the specified output folder.

### `mcherry_quantification.ijm`
This ImageJ macro merges the mCherry and brightfield channels for given code and sets the saturation to a given value for use with quantification in mCherry_quantification.py.

Usage:
1. Open ImageJ.
2. Navigate to File -> Open, and then open this file on your device
3. Navigate to where it says "// Define input and output directories" and replace my directories with the ones on your device that you want to convert.
4. Run the macro by pressing the run button in ImageJ.
5. The macro will adjust the saturation, merge the images, and save the results in the specified output folder.

### `requirements.txt`
This file lists the Python dependencies required for the project. Install them using:
-pip install -r requirements.txt

## Installation

1. Clone the repository.
2. Install the required Python packages using `requirements.txt`.
3. Ensure ImageJ is installed for running the `.ijm` macros.

## Running the Scripts

1. Prepare the input path with the necessary TIFF images.
2. Run the desired script or macro as outlined above.
3. Check the output directory for the processed images and results.

**Note:** You must have the Desktop version of ImageJ installed to run the macros. Do not use the browser version. Also, reminder that the output directory will be created within the location where you have the repository downloaded.

