# e-Paper-Image-Display-Website
Raspberry Pi image display using Waveshare e-paper 2.7 inch display.

# Features

- Website where users can upload images
- Approve images before displaying on e-Paper Display
- Process images to correct height before displaying
- Use queues to ensure each image gets displayed
- Displays queue information on website

# Getting Started

## Prerequisites

(These instructions assume that your Raspberry Pi is already connected to the Internet, happily running `pip` and has `python3` installed)

If you are running the Pi headless, connect to your Raspberry Pi using `ssh`.

Connect to your Pi over ssh and update and install necessary packages 
```
sudo apt-get update
sudo apt-get install -y python3-pip mc git libopenjp2-7
sudo apt-get install -y libatlas-base-dev python3-pil
```

Now clone the required software (Waveshare libraries and this script)

```
cd ~
git clone https://github.com/waveshare/e-Paper
git clone https://github.com/foxzsz/e-Paper-Image-Display-Website
```
Move to the `e-Paper-Image-Display-Website` directory, copy the required part of waveshare epd to directory ` 
```
cd e-Paper-Image-Display-Website
cp -r /home/pi/e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd .
rm -rf /home/pi/e-Paper
```
Install the required Python3 modules
```
python3 -m pip install -r requirements.txt
```

## Running the code
Run the main.py file
``` 
python3 main.py
```
If run successfully it will output that the Flask Webapp is running. To visit the website open the browser and enter 0.0.0.0:5000

If approval of images is enabled ensure that you are connected via VNC Viewer or have the Tkinter window open to approve and decline images.


# Credits
[12-sridhar](https://github.com/12-sridhar) - Helping code the project with me 
