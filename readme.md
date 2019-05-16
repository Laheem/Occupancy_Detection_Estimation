# Urban Observatory Occupancy Detection

## MComp Dissertation Project 

This project is an attempt to create a form of low-cost and low profile form of accurate occupancy detection.
The project aims to estimate the number of users within a specific area based on the amount of CO2 within the room. 

### Requirements - 

 - A Raspberry Pi
 - A Raspberry Pi Camera Module.
 - An Azure API Key for Cognative Services - [https://azure.microsoft.com/en-gb/services/cognitive-services/directory/vision/](https://azure.microsoft.com/en-gb/services/cognitive-services/directory/vision/)
 - A Google Cloud account if you want to access data remotely without accessing the Pi. 
 - A MySQL/MariaDB database that with the schema as specified within the code.  

### Installation - 

 - Pull the project from this repo.
 - Ensure that any dependencies that need to be installed are installed.
 - Edit the global constants at the top of the Measurement.py script to point towards various services. 
 - Run the Measurement.py script on a Raspberry Pi with a PiCamera module installed.
 - The Pi will now run on a loop and gather data over a long period of time. 

### Utilising the Neural Network - 

 - Once data has been gathered, get a csv format file from your database. 
 - Change the global constant at the top of the NeuralNet.py interface to point towards your data.
 - Run the script on a device that isn't the Pi, and gather results! You may want to consider using a fixed seed to ensure replicable results. 
