// Define input and output directories
inputDir = "C:/Users/najan/Downloads/tiffs/"; // Input directory path
outputDir = "C:/Users/najan/Downloads/tiffs/converted/"; // Output directory path

// Function to enhance contrast, merge channels, and convert to JPEG
function processAndConvert(inputDir, outputDir, baseName) {
    // Open the TX Red image
    open(inputDir + baseName + "_TX Red.tiff");
    // Set the minimum and maximum intensity values
    setMinAndMax(0, 150);
    // Rename the window to "Red" 
    selectWindow(baseName + "_TX Red.tiff");
    rename("Red");

    // Open the TRANS image
    open(inputDir + baseName + "_TRANS.tiff");
    // Set the minimum and maximum intensity values
    setMinAndMax(0, 150);
    // Rename the window to "Trans" for easy reference
    selectWindow(baseName + "_TRANS.tiff");
    rename("Trans");

    // Merge the Red and Trans channels into a single composite image
    run("Merge Channels...", "c1=Red c4=Trans create keep");

    // Save the merged image as a JPEG
    saveAs("Jpeg", outputDir + baseName + ".jpg");

    // Close the windows to free up memory and keep the workspace clean
    close("Red");
    close("Trans");
    close("Composite");
}


// Enable batch mode to speed up processing and prevent window flickering
setBatchMode(true);
list = getFileList(inputDir); // Get list of all files in the input directory

// Iterate over all files to find pairs and process them
for (i = 0; i < list.length; i++) {
    if (endsWith(list[i], "_TX Red.tiff")) {
        baseName = replace(list[i], "_TX Red.tiff", "");
        if (File.exists(inputDir + baseName + "_TRANS.tiff")) {
            processAndConvert(inputDir, outputDir, baseName); // Process the file pair
        }
    }
}

setBatchMode(false); // Disable batch mode after processing
