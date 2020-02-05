# Record and plot colour - based on record and plot profile and convert_to_Lab scripts
# This program allows the user to record 0D, 1D, and 2D profiles of image sequences.
# The 0D option just takes the average colour (or intensity if greyscale) within a drawn rectangle for each image.
# The 1D option records the 1D profile along a drawn line for each image in the sequence. The line thickness option 
# is only important for the 1D profile measurement - the pixel values are average across the thickness of the line.
# The 2D profile option essentially cuts out a piece of the image and saves those pixel values in an array.
# There are three "colour" modes - RGB to Lab, RGB, and greyscale. RGB to Lab is the default as that's what I'm using.
# Two files will be saved after the analysis - one .npy binary numpy file and a log file (.txt)
# The .npy file allows you to load the array into another script using np.load. The log file is there in case you want
# to reuse precisely the same measurement (in terms of the box or line location and line thickness when relevant)
# on a different image sequence.
# The script has one or two "bugs". It works very well if there are no other files in the directory that contains the
# image sequence, but sometimes messes up if there are other files in there - I've tried to fix it, but it still has 
# issues. Also, make sure the only images files in the directory are the ones you want in your image sequence. I haven't
# added an option to pick a particular string sequence (I may do that at some point)

###############################################
# Author: Keith Bromley                       #
# Department: School of Physics and Astronomy #
# Location: University of Edinburgh           #
# Year: 2019                                  #
###############################################

import numpy as np
from skimage import color, io, measure
import os
from PIL import Image, ImageTk
import tkinter as tk
import tkinter.filedialog as filedialog
import scipy.signal as sig
import imghdr
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import math as m
import csv
from pathlib import Path

# The first part of the program opens a GUI. In the GUI, the user can select the directory that their image 
# sequence is in, open a typical image and draw the area (currently line or rectangle) of interest.
# I'm making this program be able to give three basic outputs in three different colour modes (so 9 ways)
# Rectangle average area: Simply average the pixel values in the area for each image (should be quick)
# Rectangle 2D profile: Create numpy array of pixel values at each pixel for all images.
# Line 1D profile: Create numpy array of pixel values along the line (averaged across thickness of line)

class Image_Preview(object):
    def __init__(self, parent):
        self.myParent = parent
        self.startx = self.starty = 0
        self.endx = self.endy = 100
        self.upperFrame = tk.Frame(parent)
        self.upperFrame.pack(side=tk.TOP)
        self.middleFrame = tk.Frame(parent)
        self.middleFrame.pack(side=tk.TOP)
        self.filedialogButton = tk.Button(self.upperFrame, command=self.filedialogButtonClick)
        self.filedialogButton.config(text="Open preview image", background = "white", foreground="black")
        self.filedialogButton.pack(side=tk.LEFT)
        # Dropdown to choose between modes - line profile, rectangle 2D profile, rectangle average area?
        self.mode = tk.StringVar(parent)
        self.mode.set("Rectangle area average")
        self.modeselectDropdown = tk.OptionMenu(self.upperFrame, self.mode, "Rectangle area average",\
            "Rectangle 2D profile", "Line 1D profile") # Three options
        self.modeselectDropdown.pack(side=tk.LEFT)
        self.colourmode = tk.StringVar(parent) # Start with three colour options - so nine options overall
        self.colourmode.set("RGB to Lab")
        self.colourmodeselectDropdown = tk.OptionMenu(self.upperFrame, self.colourmode, \
            "RGB to Lab", "RGB", "Greyscale")
        self.colourmodeselectDropdown.pack(side=tk.LEFT)
        self.linethicknessLabel = tk.Label(self.upperFrame, text = "Profile line thickness: ")
        self.linethicknessLabel.pack(side=tk.LEFT)
        self.line_thickness = tk.IntVar(parent)
        self.line_thickness.set(1)
        self.linethicknessDropdown = tk.OptionMenu(self.upperFrame, self.line_thickness, 1, 2, 3, 4, 5, 6, 7, 8, 9, \
            10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100)
        self.linethicknessDropdown.pack(side=tk.LEFT)
        self.line_colour_label = tk.Label(self.upperFrame, text = "Profile line colour: ")
        self.line_colour_label.pack(side=tk.LEFT)
        self.line_colour = tk.StringVar(parent)
        self.line_colour.set("black")
        self.line_colour_dropdown = tk.OptionMenu(self.upperFrame, self.line_colour, "black", "white", "red", \
            "green", "yellow", "orange", "blue", "pink", "purple", "grey")
        self.line_colour_dropdown.pack(side=tk.LEFT)
        self.filenameLabel = tk.Label(self.middleFrame, text="File name:")
        self.filenameLabel.pack(side=tk.LEFT)
        self.filename = tk.StringVar(parent)
        self.filename.set("test")
        self.filenameEntry = tk.Entry(self.middleFrame, textvariable=self.filename)
        self.filenameEntry.pack(side=tk.LEFT)
        self.filesavedialogButton = tk.Button(self.middleFrame, command=self.filesavedialogButtonClick)
        self.filesavedialogButton.config(text="Choose file save directory", background = "white", foreground="black")
        self.filesavedialogButton.pack(side=tk.LEFT)
        self.startcoordsLabel = tk.Label(self.middleFrame, text = "y0, x0 = (0,0)")
        self.startcoordsLabel.pack(side=tk.LEFT)
        self.endcoordsLabel = tk.Label(self.middleFrame, text = "y1, x1 = (1,1)")
        self.endcoordsLabel.pack(side=tk.LEFT)
        self.loadlogfiledataButton = tk.Button(self.middleFrame, command=self.loadlogfileButtonClick)
        self.loadlogfiledataButton.config(text="Load data from log file", background = "yellow", foreground = "black")
        self.loadlogfiledataButton.pack(side=tk.RIGHT)
        self.lowerFrame = tk.Frame(parent)
        self.lowerFrame.pack(side=tk.BOTTOM)
        self.image_directory = os.getcwd()
        self.image_file = "{}/190411_CPC_heat_trial_0001.png".format(self.image_directory)
        self.image = Image.open(self.image_file)
        piw, pih = self.image.size
        self.preview_image = ImageTk.PhotoImage(self.image)
        self.xscroll = tk.Scrollbar(self.lowerFrame, orient=tk.HORIZONTAL)
        self.xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.yscroll = tk.Scrollbar(self.lowerFrame, orient=tk.VERTICAL)
        self.yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.imageCanvas = tk.Canvas(self.lowerFrame, width = 800, height = 600, scrollregion = (0,0,piw,pih))
        self.imageCanvas.config(xscrollcommand=self.xscroll.set, yscrollcommand=self.yscroll.set)
        self.imageCanvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.xscroll.config(command=self.imageCanvas.xview)
        self.yscroll.config(command=self.imageCanvas.yview)       
        self.imageCanvas.create_image(0,0,image=self.preview_image,anchor="nw")
        self.imageCanvas.bind('<ButtonPress-1>', self.savestartcoords)
        self.imageCanvas.bind('<ButtonRelease-1>', self.saveendcoords)
        self.shape = self.imageCanvas.create_line(0,0,1,1)
        self.save_directory = os.path.dirname(self.image_file)
    
    def filedialogButtonClick(self):
        start_directory = r"C:\Users\Keith_Bromley\\Desktop\\190207_Images"
        self.image_file = filedialog.askopenfilename(initialdir = start_directory, title = "Select file", \
            filetypes = (("PNG files","*.png"), ("TIFF files","*.tif"),("JPEG files","*.jpg"),("all files","*.*")))
        self.image = Image.open(self.image_file)
        iw, ih = self.image.size
        self.image_shown = ImageTk.PhotoImage(self.image)
        self.imageCanvas.destroy()
        self.xscroll.destroy()
        self.yscroll.destroy()
        self.xscroll = tk.Scrollbar(self.lowerFrame, orient=tk.HORIZONTAL)
        self.xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.yscroll = tk.Scrollbar(self.lowerFrame, orient=tk.VERTICAL)
        self.yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.imageCanvas = tk.Canvas(self.lowerFrame, width = 800, height = 600, scrollregion = (0,0,iw,ih))
        self.imageCanvas.config(xscrollcommand=self.xscroll.set, yscrollcommand=self.yscroll.set)
        self.imageCanvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.xscroll.config(command=self.imageCanvas.xview)
        self.yscroll.config(command=self.imageCanvas.yview)       
        self.imageCanvas.create_image(0,0,image=self.image_shown,anchor="nw")
        self.imageCanvas.bind('<ButtonPress-1>', self.savestartcoords)
        self.imageCanvas.bind('<ButtonRelease-1>', self.saveendcoords)
        if self.mode.get() == "Rectangle area average" or "Rectangle 2D profile":
            self.shape = self.imageCanvas.create_rectangle(0,0,2,2)
        elif self.mode.get() == "Line 1D profile":
            self.shape = self.imageCanvas.create_line(0,0,1,1)
    
    def filesavedialogButtonClick(self):
        start_directory = r"C:\Users\Keith_Bromley\\Desktop\\190207_Images"
        self.save_directory = filedialog.askdirectory(initialdir = start_directory, title = "Choose save directory")
    
    def loadlogfileButtonClick(self):
        start_directory = r"C:\Users\Keith_Bromley\\Desktop\\190207_Images"
        self.log_file = filedialog.askopenfilename(initialdir = start_directory, title = "Select log file", \
            filetypes = (("TXT files","*.txt"),("all files","*.*")))
        with open (self.log_file, 'r') as f:
            reader = csv.reader(f,delimiter='\t')
            next(reader, None)
            log_data_list = [row[1] for row in reader] # This works! Just add the startcoordsLabel destroy and rewrite lines below!
            self.mode.set(log_data_list[0])
            self.colourmode.set(log_data_list[1])
            self.starty = int(log_data_list[2])
            self.startx = int(log_data_list[3])
            self.endy = int(log_data_list[4])
            self.endx = int(log_data_list[5])
            self.line_thickness.set(int(log_data_list[6]))
            self.startcoordsLabel.destroy()
            self.startcoordsLabel = tk.Label(self.middleFrame, text = "y0, x0 = ({},{})".format(self.starty,self.startx))
            self.startcoordsLabel.pack(side=tk.LEFT)
            self.endcoordsLabel.destroy()
            self.endcoordsLabel = tk.Label(self.middleFrame, text = "y1, x1 = ({},{})".format(self.endy,self.endx))
            self.endcoordsLabel.pack(side=tk.LEFT)
            self.imageCanvas.delete(self.shape)
            if self.mode.get() == "Rectangle area average" or self.mode.get() == "Rectangle 2D profile":
                self.shape = self.imageCanvas.create_rectangle(self.startx,self.starty,self.endx,self.endy, \
                width=self.line_thickness.get(), outline=self.line_colour.get())
            elif self.mode.get() == "Line 1D profile":
                self.shape = self.imageCanvas.create_line(self.startx,self.starty,self.endx,self.endy, \
                width=self.line_thickness.get(), fill=self.line_colour.get())
    
    def savestartcoords(self, event):
        self.startx = self.imageCanvas.canvasx(event.x) # The canvasx (and canvasy) methods allow you to access the
        self.starty = self.imageCanvas.canvasy(event.y) # canvas coordinates instead of just window coordinates
        self.startcoordsLabel.destroy()
        self.startcoordsLabel = tk.Label(self.middleFrame, text = "y0, x0 = ({},{})".format(int(self.starty), int(self.startx)))
        self.startcoordsLabel.pack(side=tk.LEFT)
        #print(self.startx, self.starty) # Debugging line
        
    def saveendcoords(self, event):
        self.endx = self.imageCanvas.canvasx(event.x)
        self.endy = self.imageCanvas.canvasy(event.y)
        self.endcoordsLabel.destroy()
        self.endcoordsLabel = tk.Label(self.middleFrame, text = "y1, x1 = ({},{})".format(int(self.endy), int(self.endx)))
        self.endcoordsLabel.pack(side=tk.LEFT)
        self.imageCanvas.delete(self.shape)
        if self.mode.get() == "Rectangle area average" or self.mode.get() == "Rectangle 2D profile":
            self.shape = self.imageCanvas.create_rectangle(self.startx,self.starty,self.endx,self.endy, \
            width=self.line_thickness.get(), outline=self.line_colour.get())
        elif self.mode.get() == "Line 1D profile":
            self.shape = self.imageCanvas.create_line(self.startx,self.starty,self.endx,self.endy, \
            width=self.line_thickness.get(), fill=self.line_colour.get())
        

root = tk.Tk()
window = Image_Preview(root)
root.title("Load image and draw profile line or rectangle. To draw the line just click, hold, drag, and release. Then close window.")
root.mainloop()

def colour_convert(colour_mode, im_dir, im_dir_list, im_index):
    if colour_mode == "Greyscale":
        image = Image.open("{}\{}".format(im_dir, im_dir_list[im_index])) # Consider using io.imread
        image = image.convert('L')
        imdata = np.array(image)
        return imdata
    elif colour_mode == "RGB":
        rgba_array = io.imread("{}\{}".format(im_dir, im_dir_list[im_index])) # Assumes image is in RGBA format
        rgb_array = color.rgba2rgb(rgba_array)
        return rgb_array
    elif colour_mode == "RGB to Lab":
        rgba_array = io.imread("{}\{}".format(im_dir, im_dir_list[im_index])) # Assumes image is in RGBA format
        rgb_array = color.rgba2rgb(rgba_array)
        lab_array = color.rgb2lab(rgb_array)
        return lab_array

def skip_non_images(im_dir,im_dir_list):
    image_suffixes = ['.rgb','.gif','.pbm','.pgm','.ppm','.tif','.rast','.xbm','.jpg','.bmp','.png']
    # Iterate through the directory to skip non-image files at the start. It breaks when it finds an image file
    im_index = 0
    for im in image_directory_list:
        filename = Path("{}/{}".format(im_dir, im))
        if filename.suffix not in image_suffixes or os.path.isdir(filename) == True:
            im_index +=1 
        else:
            break
    return im_index

def iterate_through_image_dir(mode,colour_mode,im_dir,im_dir_list,y1,x1,y2,x2,line_thick):
    imghdr_filetypes = ['rgb','gif','pbm','pgm','ppm','tiff','rast','xbm','jpeg','bmp','png']
    image_suffixes = ['.rgb','.gif','.pbm','.pgm','.ppm','.tif','.rast','.xbm','.jpg','.bmp','.png']
    im_index = skip_non_images(im_dir,im_dir_list)
    print(im_index)
    if mode == "Line 1D profile":
        image_array = colour_convert(colour_mode,im_dir,im_dir_list,im_index)
        if colour_mode == "Greyscale":
            intensity_profile_array = measure.profile_line(image_array,(window.starty, window.startx),(window.endy, window.endx), window.line_thickness.get())
        else:
            intensity_profile_array = np.array([measure.profile_line(image_array,(y1, x1),(y2, x2), line_thick)])
        #print(intensity_profile_array.shape)
        i=im_index+1 # Set to one as we're going to skip the first file in image_directory_list as we used that one to set up
        # intensity_profile_array which has the correct array shape
        for im_dir_file in im_dir_list[im_index+1:]: # Iterate through files in directory missing first one (done already)
            filename = Path("{}/{}".format(im_dir, im_dir_file))
            if filename.suffix not in image_suffixes or os.path.isdir(filename) == True:
                i+=1 # Count non-image files
            elif i<len(im_dir_list): # Obviously stop at the end of the directory
                image_array = colour_convert(colour_mode,im_dir,im_dir_list,i)
                intensity_profile = measure.profile_line(image_array,(y1,x1),(y2,x2), line_thick)
                # We use the start and end coordinates we recorded by clicking on the image in the GUI
                if colour_mode == "Greyscale":
                    intensity_profile_array = np.c_[intensity_profile_array,intensity_profile]
                else:
                    intensity_profile_array = np.r_[intensity_profile_array,np.array([intensity_profile])]
                # Add latest column of data to array - wrong shape for RGB - work this out!
                # np.c_ is a nice way of adding a column to a numpy array (np.r_ adds a row)
                sys.stdout.write("\rProcessed images: {} of {} (at most). Array shape: {}".format(i+1,len(im_dir_list),intensity_profile_array.shape))
                sys.stdout.flush()
                # Report progress to terminal
                # The stdout statement above is handy if you are processing large images online and it takes a while
                i+=1
        return intensity_profile_array
    elif mode == "Rectangle area average":
        image_array = colour_convert(colour_mode,im_dir,im_dir_list,im_index)
        if colour_mode == "Greyscale":
            cropped_image_array = image_array[x1:x2,y1:y2]
            average_pixel_value = np.mean(cropped_image_array)
            pixel_average_array = np.array([average_pixel_value]) # Will be an array with shape (1,)
        else:
            cropped_image_array = image_array[y1:y2,x1:x2,:] # create array of selected area
            # Then take the average of each R,G,B (or L,a,b) value of all pixels in array
            average_RorL_value, average_Gora_value, average_Borb_value = np.mean(cropped_image_array[:,:,0]),\
                np.mean(cropped_image_array[:,:,1]), np.mean(cropped_image_array[:,:,2])
            pixel_average_array = np.array([average_RorL_value, average_Gora_value, \
                average_Borb_value])
            # Then turn those three values into an array - will be an array with shape (3,)
        i=0
        for im_dir_file in im_dir_list[im_index+1:]: # Iterate through files in directory missing first one (done already)
            #if imghdr.what("{}\{}".format(im_dir,im_dir_file)) not in imghdr_filetypes:
            filename = Path("{}/{}".format(im_dir, im_dir_file))
            if filename.suffix not in image_suffixes or os.path.isdir(filename) == True: # There's something fishy about the .npy file that I save...
                print(filename.suffix)
                print("{}\{} is not an image!".format(im_dir, im_dir_file))
                i+=1 # Ignore non-image files
            elif i<len(im_dir_list[im_index+1:]):
                image_array = colour_convert(colour_mode,im_dir,im_dir_list[im_index+1:],i) ###HERE###
                if colour_mode == "Greyscale":
                    cropped_image_array = image_array[y1:y2,x1:x2]
                    pixel_average = np.mean(cropped_image_array)
                    pixel_average_array = np.append(pixel_average_array,pixel_average)
                    # Add latest data value to array
                else:
                    cropped_image_array = image_array[y1:y2,x1:x2,:]
                    average_RorL_value, average_Gora_value, average_Borb_value = np.mean(cropped_image_array[:,:,0]),\
                    np.mean(cropped_image_array[:,:,1]), np.mean(cropped_image_array[:,:,2])
                    pixel_average_array = np.vstack((pixel_average_array, np.array([average_RorL_value,\
                        average_Gora_value,average_Borb_value])))
                sys.stdout.write("\rProcessed images: {} of {} (at most). Array shape: {}".format(i+1,len(im_dir_list),pixel_average_array.shape))
                sys.stdout.flush()
                i+=1
        return pixel_average_array
    elif mode == "Rectangle 2D profile":
        # Missing bit that processes first image...
        image_array = colour_convert(colour_mode,im_dir,im_dir_list,im_index)
        pixel_2d_array = image_array[y1:y2,x1:x2,:]
        i=1
        for im_dir_file in im_dir_list[im_index+1:]: # Iterate through files in directory missing first one (done already)
            if imghdr.what("{}\{}".format(im_dir,im_dir_file)) not in imghdr_filetypes:
                pass # Ignore non-image files
            elif i<=len(im_dir_list): 
                image_array = colour_convert(colour_mode,im_dir,im_dir_list,i)
                intensity_profile = image_array[y1:y2,x1:x2,:]
                if colour_mode == "Greyscale": # WILL THE BELOW WORK - DOUBT IT...
                    intensity_profile_array = np.c_[intensity_profile_array,intensity_profile]
                else:
                    intensity_profile_array = np.r_[intensity_profile_array,np.array([intensity_profile])]
                sys.stdout.write("\rProcessed images: {} of {} (at most). Array shape: {}".format(i+1,len(im_dir_list),intensity_profile_array.shape))
                sys.stdout.flush()
                i+=1
        return intensity_profile_array 
        # Final shape should be (x2-x1,y2-y1,image_amount,3) for rgb

# This bit saves the directory that was chosen in the GUI and also makes it a list
window.image_directory = Path(os.path.dirname(window.image_file)) # This gets the directory from the image file location
image_directory_list = os.listdir(window.image_directory) # Turns directory into list for easy iteration

# Let's apply the functions we wrote above...
data_array = iterate_through_image_dir(window.mode.get(), window.colourmode.get(),window.image_directory,\
    image_directory_list,int(window.starty),int(window.startx),int(window.endy),int(window.endx),window.line_thickness.get())

# Save numpy array file for later use in Python
np_array_save_dir = window.save_directory # Add specific file dialogue
if window.colourmode.get() == "Greyscale":
    np.save("{}/{}_greyscale_array".format(np_array_save_dir, window.filename.get()),data_array)
    np.savetxt("{}/{}_greyscale_array.csv".format(np_array_save_dir, window.filename.get()), data_array, delimiter=',')
elif window.colourmode.get() == "RGB":
    np.save("{}/{}_RGB_array".format(np_array_save_dir, window.filename.get()),data_array)
    np.savetxt("{}/{}_RGB_array.csv".format(np_array_save_dir, window.filename.get()), data_array, delimiter=',')
elif window.colourmode.get() == "RGB to Lab":
    np.save("{}/{}_Lab_array".format(np_array_save_dir, window.filename.get()),data_array)
    np.savetxt("{}/{}_Lab_array.csv".format(np_array_save_dir, window.filename.get()), data_array, delimiter=',')

# Save log file so analyses can be repeated exactly as previously performed (including coordinates) if necessary
text_file = open("{}/{}_log.txt".format(np_array_save_dir, window.filename.get()), "w+")
text_file.write("Record profile information for {}\n".format(window.filename.get()))
text_file.write("Measurement mode:\t{}\nColour mode:\t{}\n".format(window.mode.get(),window.colourmode.get()))
text_file.write("Start Y:\t{}\nStart X:\t{}\nEnd Y:\t{}\nEnd X:\t{}\n\
    Line thickness (only relevant for line profile):\t{}".format(int(window.starty), int(window.startx), \
    int(window.endy), int(window.endx), window.line_thickness.get()))
text_file.close()

# After this point is some script for initial graphing specific to my work - feel free to change it or delete it. 
# The files for analysis will all have been saved by this stage.

sns.set()

print(data_array.shape)
x_values = range(data_array.shape[0])

figheight = 8
figwidth = 8

fig, ax = plt.subplots()
fig.set_figheight(figheight)
fig.set_figwidth(figwidth)
#for pic in range(5):
#ax.plot(x_values,data_array[:], "r-")
ax.plot(x_values,data_array[:,0], "r-")
ax.plot(x_values,data_array[:,1], "g-")
ax.plot(x_values,data_array[:,2], "b-")
ax.set_xlabel("Image number")
ax.set_ylabel("L*,a*,b*-value")
fig.set_tight_layout(True)

delta_E_array = np.empty((data_array.shape[0]))

for x in x_values:
    delta_E = m.sqrt((data_array[x,0]-data_array[0,0])**2 + (data_array[x,1]-data_array[0,1])**2 +\
        (data_array[x,1]-data_array[0,1])**2)
    delta_E_array[x] = delta_E

np.save("{}/{}_DeltaE_array".format(np_array_save_dir, window.filename.get()),delta_E_array)

fig2, ax2 = plt.subplots()
fig2.set_figheight(figheight)
fig2.set_figwidth(figwidth)
ax2.plot(x_values,delta_E_array, "k--")
ax2.set_xlabel("Image number")
ax2.set_ylabel(r"$\Delta$E")
fig2.set_tight_layout(True)

