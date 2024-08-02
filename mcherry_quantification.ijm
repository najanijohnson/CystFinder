// Function to enhance contrast, merge channels, and convert to JPEG
function processAndConvert(inputDir, outputDir, baseName) {
    // Open mCherry and BF images
    open(inputDir + baseName + "_TX Red.tiff");
    run("Enhance Contrast", "saturated=0.35");
    selectWindow(baseName + "_TX Red.tiff");
    rename("Red");

    open(inputDir + baseName + "_TRANS.tiff");
    run("Enhance Contrast", "saturated=0.35");
    selectWindow(baseName + "_TRANS.tiff");
    rename("Trans");

    // Merge channels
    run("Merge Channels...", "c1=Red c4=Trans create keep");

    // Save the merged image as JPEG
    saveAs("Jpeg", outputDir + baseName + ".jpg");

    // Close all images
    close("Red");
    close("Trans");
    close("Composite");
}

// Define input and output directories
inputDir = "C:/Users/najan/Downloads/tiffs/"; // Input directory path
outputDir = "C:/Users/najan/Downloads/tiffs/converted/"; // Output directory path

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
