

// The function to convert a single file from TIFF to JPEG
function convertToJpeg(inputDir, outputDir, filename) {
    open(inputDir + filename); // Open the image file
    saveAs("Jpeg", outputDir + filename + ".jpg"); // Save as JPEG
    close(); // Close the image
}

// Define input and output directories
inputDir = "C:/Users/najan/Downloads/tiffs/"; // Input directory path
outputDir = "C:/Users/najan/Downloads/tiffs/converted/"; // Output directory path

// Enable batch mode to speed up processing and prevent window flickering
setBatchMode(true);
list = getFileList(inputDir); // Get list of all files in the input directory
for (i = 0; i < list.length; i++) {
    // Check if the file is a TIFF file
    if (endsWith(list[i], ".tif") || endsWith(list[i], ".tiff")) {
        convertToJpeg(inputDir, outputDir, list[i]); // Convert the file
    }
}
setBatchMode(false); // Disable batch mode after processing

