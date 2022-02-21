# Importing the needed modules
from flask import Flask, render_template, redirect, request, Response
from PIL import ImageTk, Image as img
import time
import threading
import queue
import json
import os
import sys
from waveshare_epd import epd2in7
from datetime import datetime, timedelta
from tkinter import *
from tkinter import messagebox


class ImageDisplayWeb:
    ## All the variables that can be modified  
    def __init__(self, host="0.0.0.0", approval=False, port=80,
                 ALLOWED_EXTENSIONS=set(['png', 'jpg', 'jpeg'])):
        self.approval = approval
        self.queue = queue.Queue()
        self.currentimagename = ""
        self.approvalqueue = queue.Queue()
        self.ALLOWED_EXTENSIONS = ALLOWED_EXTENSIONS
        self.epd = epd2in7.EPD()
        self.epd.init()
        self.total = 0
        self.pressed = False

        threading.Thread(target=self.queue_handler).start(
        if self.approval:
            threading.Thread(target=self.intitiate_approval_queue).start()

        application = Flask(__name__)

        # Create application route which returns the html template index.html 
        # Import the html templates and return them as a response 
        @application.route('/')
        def index():
            return render_template('index.html')

        ## This application route returns the queue data ( queuelength, queue time etc.) 
        @application.route('/queue-data')
        def queue_data():
            def update_queue_data():
                while True:
                    queuesize = self.queue.qsize()
                    sec = timedelta(seconds=(queuesize * 10))
                    d = datetime(1, 1, 1) + sec
                    timedata = "%d:%d:%d:%d" % (
                        d.day - 1, d.hour, d.minute, d.second)
                    if self.approval:
                        approvalqueuesize = self.approvalqueue.qsize()
                        json_data = json.dumps(
                            {"queuedata": f"Queue Length: {queuesize}, Estimated Queue Time: {timedata}, Total images Displayed: {self.total}, Approval Queue Length: {approvalqueuesize}"})
                    else:
                        json_data = json.dumps(
                            {"queuedata": f"Queue Length: {queuesize}, Estimated Queue Time: {timedata}, Total images Displayed: {self.total}"})
                    yield f"data:{json_data}\n\n"
            return Response(update_queue_data(), mimetype='text/event-stream')

        ## This application route is used for submitting images 
        @application.route('/', methods=['POST'])
        def imagesubmit():
            if 'file' not in request.files:
                print("No image in request")
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                return redirect(request.url)
                print("No file selected")
            if file and self.allowed_file(file.filename):
                file.save(os.path.join("images/", file.filename))
                if self.approval:
                    self.approvalqueue.put("images/" + file.filename)
                    print(f"Added image {file.filename} to approval queue")
                else:
                    self.queue.put("images/" + file.filename)
                    print(f"Added image {file.filename} to queue")
                return redirect(request.url)
            else:
                return redirect(request.url)
                print("Invalid file type")
        application.run(host=host, port=port)

    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    # Creating small tkinter app where we can Approve or Decline Images 
    def intitiate_approval_queue(self):
        # Start the approval_queue_handler thread
        threading.Thread(target=self.approval_queue_handler).start()

        # Create tkinter window with its tile and size of the window
        self.root = Tk()
        self.root.title("Approving images")
        self.root.geometry("1000x1000")

        # Create a label where an Image can be placed
        self.label = Label(self.root)
        self.label.grid(row=2, column=0, sticky=NSEW)

        # Create Buttons
        self.btn1 = Button(self.root, text="Approve image", command=self.add_queue)
        self.btn1.grid(row=0, column=0, sticky=NSEW)
        self.btn2 = Button(self.root, text="Decline image", command=self.declineimage)
        self.btn2.grid(row=1, column=0, sticky=NSEW)

        # Control the close button at the top-right of the window by assigning a command 'check'
        self.root.protocol("WM_DELETE_WINDOW", self.check)

        # Mainloop makes the tkinter window stay
        self.root.mainloop()
    
    # A function to check if the user really wants to quit tkinter window  
    def check(self):
        # If user says yes then it will close the window
        if messagebox.askyesno("Quit", "Do you want to quit?"):
            self.root.destroy()

    # These both functions are used for when you press a button on the tkinter window  
    def add_queue(self):
        self.queue.put(self.currentimagename)
        # Remove the image on the window
        self.label.config(image='')
        # Set self.pressed as true
        self.pressed = True
    
    # Remove the image and not add to the queue
    def declineimage(self):
        self.label.config(image='')
        self.pressed = True
    
    ## This function will handle all the images in the approval queue 
    def approval_queue_handler(self):
        while True:
            # Handle errors
            try:
                # Get the image
                imagename = self.approvalqueue.get()
                self.currentimagename = imagename
                # Open the image with PIL and resize it to 400x300
                ApprovalImage = img.open(imagename).resize((400, 300))
                test = ImageTk.PhotoImage(ApprovalImage)
                # Add the image on the label
                self.label.config(image=test)
                # Set self.pressed as false 
                self.pressed = False
                # Do nothing till a person approves the image
                while self.pressed == False:
                    pass
            except Exception as e:
                continue

    ## This function will display all the images in the image queue
    def queue_handler(self):
        while True:
            # Handle errors
            try:
                # Get the image
                imagename = self.queue.get()
                # Open the image with PIL
                DisplayImage = img.open(imagename)
                # Get the width(w) and height(h) of the Image
                w, h = DisplayImage.size
                # If the width is bigger than height it means the image is landscape oriented
                if w > h:
                    # Resize to the resolution of 264x176 (landscape)
                    DisplayImage = DisplayImage.resize((264, 176))
                    # Rotate the image so the resolution becomes (portrait)
                    DisplayImage = DisplayImage.transpose(img.ROTATE_90)
                    # Display the Image
                    self.epd.display(self.epd.getbuffer(DisplayImage))
                # If the width is smaller or the same as height it is considered as portrait
                elif w <= h:
                    # Resize the Image to 176x264 (portrait)
                    DisplayImage = DisplayImage.resize((176, 264))
                    # Display the image
                    self.epd.display(self.epd.getbuffer(DisplayImage))
                # Remove the image
                os.remove(imagename)
                # Add to the total images displayed
                self.total += 1
                # Rest the E-Paper for 10 seconds
                time.sleep(10)
                # Just to check if the program tried to display the image
                print(f"Successfully displayed image {imagename}")
            except Exception as e:
                continue


# Run the class and configure application
InitiateApp = ImageDisplayWeb(host="0.0.0.0", port=5000, approval=True)