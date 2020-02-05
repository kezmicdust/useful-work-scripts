# Record and plot the intensity profile over a series of images
# In this script, the average intensity between the pixels of interest is plotted as the final figure
# Author: Keith Bromley, University of Edinburgh
# Created: 2019

from skimage import measure
import numpy as np
import matplotlib.pyplot as plt
import os
from PIL import Image, ImageTk
import tkinter as tk
import tkinter.filedialog as filedialog
import scipy.signal as sig
import imghdr
import sys
from pathlib import Path

class Image_Preview(object):
    def __init__(self, parent):
        self.myParent = parent
        self.startx = self.starty = 0
        self.endx = self.endy = 100
        self.upperFrame = tk.Frame(parent)
        self.upperFrame.pack(side=tk.TOP)
        self.filedialogButton = tk.Button(self.upperFrame, command=self.filedialogButtonClick)
        self.filedialogButton.config(text="Open preview image...", background = "white", foreground="black")
        self.filedialogButton.pack(side=tk.LEFT)
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
        self.filename = tk.StringVar(parent)
        self.filename.set("test")
        self.filenameEntry = tk.Entry(self.upperFrame, textvariable=self.filename)
        self.filenameEntry.pack(side=tk.RIGHT)
        self.lowerFrame = tk.Frame(parent)
        self.lowerFrame.pack(side=tk.BOTTOM)
        self.image_directory = os.getcwd()
        self.image_file = "{}/fireworks.jpg".format(self.image_directory)
        self.image = Image.open(self.image_file)
        #preview_image = Image.open("{}/Lastimageholder.png".format(os.getcwd()))
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
        self.profile_line = self.imageCanvas.create_line(0,0,1,1)
    
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
        self.profile_line = self.imageCanvas.create_line(0,0,1,1)
    
    def savestartcoords(self, event):
        self.startx = self.imageCanvas.canvasx(event.x) # The canvasx (and canvasy) methods allow you to access the
        self.starty = self.imageCanvas.canvasy(event.y) # canvas coordinates instead of just window coordinates
        #print(self.startx, self.starty) # Debugging line
        
    def saveendcoords(self, event):
        self.endx = self.imageCanvas.canvasx(event.x)
        self.endy = self.imageCanvas.canvasy(event.y)
        self.imageCanvas.delete(self.profile_line)
        self.profile_line = self.imageCanvas.create_line(self.startx,self.starty,self.endx,self.endy, \
            width=self.line_thickness.get(), fill=self.line_colour.get())
        #print(self.endx, self.endy) # Debugging line
        

root = tk.Tk()
window = Image_Preview(root)
root.title("Load image and draw profile line. To draw the line just click, hold, drag, and release. Then close window.")
root.mainloop()

#window.image_file = str(window.image_file)
window.image_directory = os.path.dirname(window.image_file) # This gets the directory from the image file location
image_directory_list = os.listdir(window.image_directory) # Turns directory into list for easy iteration

imghdr_filetypes = ['rgb','gif','pbm','pgm','ppm','tiff','rast','xbm','jpeg','bmp','png']
image_suffixes = ['.rgb','.gif','.pbm','.pgm','.ppm','.tif','.rast','.xbm','.jpg','.bmp','.png']

im_index = 0
non_image_files = 0
for im in image_directory_list:
    if imghdr.what("{}\{}".format(window.image_directory,im)) not in imghdr_filetypes: #Just added window.
        # in front of image_directory - if a problem arises, check here
        non_image_files += 1
        im_index +=1
    else:
        break


image = Image.open("{}\{}".format(window.image_directory, image_directory_list[im_index]))
image = image.convert('L')
imdata = np.array(image)
intensity_profile_array = measure.profile_line(imdata,(window.starty, window.startx),(window.endy, window.endx), window.line_thickness.get())
image_directory_length = len(image_directory_list)

i=1 # Set to one as we're going to skip the first file in image_directory_list as we used that one to set up
    # intensity_profile_array which has the correct array shape

for image_file in image_directory_list[im_index+1:]: # Iterate through files in directory missing first one (done already)
    #if imghdr.what("{}\{}".format(window.image_directory,image_file)) not in imghdr_filetypes:
        #non_image_files += 1
    filename = Path("{}/{}".format(window.image_directory, image_file))
    if filename.suffix not in image_suffixes or os.path.isdir(filename) == True:
        i+=1 # Count non-image files
    elif i<len(image_directory_list): # Obviously stop at the end of the directory
        image = Image.open("{}\{}".format(window.image_directory, image_file))
        image = image.convert('L') # Converts image to greyscale
        imdata = np.array(image) # Turns image into numpy array of coordinates (in (y,x) format)
        intensity_profile = measure.profile_line(imdata,(window.starty, window.startx),(window.endy, window.endx), window.line_thickness.get())
        # We use the start and end coordinates we recorded by clicking on the image in the GUI
        #print(intensity_profile)
        #print(intensity_profile.shape[0])
        intensity_profile_array = np.c_[intensity_profile_array,intensity_profile]
        sys.stdout.write("\rProcessed images: {} of {}. Array shape: {}".format(i+1,len(image_directory_list),intensity_profile_array.shape))
        sys.stdout.flush()
        #print("Processed images: {} of {}".format(i+1,len(image_directory_list)))
        #print(intensity_profile_array.shape)
        # The print statement above is handy if you are processing large images online and it takes a while
        #np.c_ is a nice way of adding a column to a numpy array (np.r_ adds a row)
        i+=1

intensity_profile_length = intensity_profile_array.shape[0] # Should be equal to number of pixels in profile line

for j in range(image_directory_length-non_image_files): # This may miss the last value...
    min_value = np.min(intensity_profile_array[:,j]) # Find minimum value in y-column of interest
    for v in range(intensity_profile_length): # Iterate down column. Hmmm... worked and then didn't work
        intensity_profile_array[v,j] = intensity_profile_array[v,j] - min_value # Subtract min value from each value in column
        v+=1
    j+=1

np.save("{}/{}_greyscale_array".format(window.image_directory, window.filename.get()),intensity_profile_array)
np.savetxt("{}/{}_greyscale_array.csv".format(window.image_directory, window.filename.get()), intensity_profile_array, delimiter=',')

#print(intensity_profile_array.shape)
intensity_profile_array_length = intensity_profile_array.shape[1] # Should be equal to number of images analysed
# I think intensity_profile_array_length is the same as image_directory_length - tidy up later
#print (intensity_profile_array[150,100])
# Generate pixel numbers
profile_line_pixels = np.linspace(1,intensity_profile.shape[0]+1,intensity_profile.shape[0])
# This should produce an array of numbers from 1 to however long the drawn line is - each number represents pixels

fig, ax = plt.subplots()

ax.plot(profile_line_pixels,intensity_profile_array[:,1]) # Plot "plot profile" line from 1st image
ax.plot(profile_line_pixels,intensity_profile_array[:,intensity_profile_array_length-1]) # Plot "plot profile" line from last image
plt.show()

area_array = np.zeros((intensity_profile_array_length, 2)) # Create empty array
area_array[:,0] = range(intensity_profile_array_length)  # Plug in x-axis value (0-431 in this case) 

# Choose limits for the addition
low_x = int(input("\nChoose your lower x limit: ")) # Put in error handling later
high_x = int(input("Choose your upper x limit: "))

# Inform the program of the timelapse interval and units

interval = int(input("What was the timelapse interval of this experiment (just the integer - tell me the unit next)? "))
unit = input("What was the unit of the timelapse interval (minutes, hours...)? ")

text_file_name = input("Type in log file name: ")

# For sg_datapoints, choose an odd number like 51 or something. Obviously it should be far less than the overall number of
# datapoints, so if you only had 100 images, then something like 17 might be more sensible
sg_datapoints = input("How many datapoints do you want to apply the Savitzky-Golay smoothing filter over? ")
while sg_datapoints.isdigit() == False:
    sg_datapoints = input("How many datapoints do you want to apply the Savitzky-Golay smoothing filter over? ")
sg_datapoints = int(sg_datapoints)
if sg_datapoints % 2 == 0:
    sg_datapoints += 1

# For sg_power, probably use 3 - higher orders risk overfitting.
sg_power = input("What order of polynomial do you want the SG filter to apply? ")
while sg_power.isdigit() == False:
    sg_power = input("What order of polynomial do you want the SG filter to apply? ")
sg_power = int(sg_power)
if sg_power < 2 or sg_power > 5:
    sg_power = 3
    print("Polynomial order set to 3 as you typed in a number that was too big or too small!")

directory_above_image_directory = os.path.dirname(window.image_directory) #window. or not?
text_file = open("{}/{}.txt".format(directory_above_image_directory, text_file_name), "w+")
text_file.write("Record profile information for {}\n".format(text_file_name))
text_file.write("Line coordinates:\nStart X: {}\nStart Y: {}\nEnd X: {}\nEnd Y: {}\nLine thickness: {}\
    \nSelected lower x-limit (pixel position on line): {}\nSelected upper x-limit (pixel position on line): {}"\
    .format(int(window.startx), int(window.starty), int(window.endx), int(window.endy), window.line_thickness.get(), \
    low_x, high_x))
text_file.close()
# The bit above just saves a log file of the measurement, so it would be possible to go back an recreate the line
# I'll add a text box to the GUI to type in the desired filename - I'll do it with input() until then

for k in range(intensity_profile_array_length): # This will populate the second column of our new array
    area_array[k, 1] = intensity_profile_array[low_x:high_x, k].sum() # For each point, put in the sum of each column in
    # value_array between the limits we selected
    k += 1


aat = area_array.transpose() # Transpose the array to make savgol filter work
s = sig.savgol_filter(aat,sg_datapoints,sg_power) # Maybe make sav_gol_range and polynomial power an optional input
smoothed_area_array = s.transpose() # Transpose it back to make the graphing code work without changing it

# The moving_diff_array function works with a single 2 axis array as input instead of two lists
def moving_diff_array(a,d):
	diff_array = np.zeros(shape=(a.shape[0]-df,a.shape[1]))
	i=0
	while i<a.shape[0]-df:
		xy_array = a[i:d+i]
		x_array = xy_array[:,0]
		y_array = xy_array[:,1]
		sumxy = np.sum(x_array*y_array)
		sumx = np.sum(x_array)
		sumy = np.sum(y_array)
		sumxsq = np.sum(x_array**2)
		grad = (d*sumxy-(sumx*sumy))/((d*sumxsq)-(sumx**2))
		x_value = np.mean(x_array)
		diff_array[i] = [x_value,grad]
		i+=1
	return diff_array

df = 10 # Ensure there are enough data points in the data!

#x_diff = [x for x in np.linspace(-100,100-(200/(datapoints/df)),datapoints-df+1)]
#y_diff = moving_diff_list(x_data,y_data,df)
smoothed_area_array_average = smoothed_area_array
smoothed_area_array_average[:,1] = smoothed_area_array[:,1]/(high_x-low_x)

area_array_average = area_array
area_array_average[:,1] = area_array[:,1]/(high_x-low_x)

diff_data = moving_diff_array(smoothed_area_array_average, df)

fig2, ax2 = plt.subplots()

area_array[:,0] = area_array[:,0]*interval # I need a couple of parameters to input the interval and unit
smoothed_area_array [:,0] = smoothed_area_array[:,0]*interval
diff_data[:,0] = diff_data[:,0]*interval

np.save("{}\\area_array.npy".format(os.getcwd()), area_array)

ax2.plot(area_array[:,0],area_array[:,1], 'r-')
ax2.plot(smoothed_area_array[:,0],smoothed_area_array_average[:,1], 'b--')
#ax2.set_ylim(50,125)
ax2.set_ylabel("Average greyscale value")
ax2.set_xlabel("time ({})".format(unit))
ax3 = ax2.twinx() # Creates a new Axes object that shares x-axis with old Axes object
ax3.plot(diff_data[:,0], diff_data[:,1], 'k--')
#ax3.set_ylim(-0.1,0.2)
ax3.set_ylabel("Gradient over {} {}".format(df*interval, unit))
fig2.tight_layout() # Otherwise y2 label can be slightly clipped apparently
plt.show()