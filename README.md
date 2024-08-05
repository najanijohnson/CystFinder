This project contains various scripts and ImageJ macros for processing and analyzing image files related to cyst and tubule identification and quantification.

## Scripts and Macros

### `cyst_finder.py`
This script processes images to identify and quantify cysts.

Usage:
python cyst_finder.py [input_path] [output_directory]
- `input_path`: Path to a single image file or a directory containing multiple images.
- `output_directory`: Path to the directory where the processed images and results will be saved.

### `ltl-dba-quantification.py`
This script quantifies images using the LTL-DBA method.

python ltl-dba-quantification.py [input_path] [output_directory]
- `input_path`: Path to a single image file or a directory containing multiple images.
- `output_directory`: Path to the directory where the processed images and results will be saved.

### `Macro.ijm`
This ImageJ macro takes a folder full of TIFF images and converts them to JPEG format.

Usage:
1. Open ImageJ.
2. Run the macro by opening `Macro.ijm` in ImageJ.
3. Follow the prompts to select the input folder containing TIFF images.
4. The macro will process the images and save the converted JPEGs in the specified output folder.

### `mcherry_quantification.ijm`
This ImageJ macro processes a folder full of TIFF images specific to mcherry quantification. It adjusts the saturation and merges two images.

Usage:
1. Open ImageJ.
2. Run the macro by opening `mcherry_quantification.ijm` in ImageJ.
3. Follow the prompts to select the input folder containing TIFF images.
4. The macro will adjust the saturation, merge the images, and save the results in the specified output folder.

### `mcherry_quantification.py`
This Python script is designed to automate mcherry quantification similar to the `mcherry_quantification.ijm` macro.

Usage:
python mcherry_quantification.py [input_path] [output_directory]
- `input_path`: Path to a single image file or a directory containing multiple images.
- `output_directory`: Path to the directory where the processed images and results will be saved.

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

**Note:** The output directory will be created within the location where you have the repository downloaded.
