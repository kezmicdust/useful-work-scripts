# I would like to write a script that generates schematic images of dispersions. I want it to accept size distribution
# data along with some other parameters (shape, colours, box size and shape, number of particles in schematic).
# So the user would upload a text file with size distribution data (acknowledge the weighting - volume averaged etc...)
# and choose a few parameters like "circles", "black", "white box", "2:1 aspect ratio", "border thickness/colour", 
# "image size", "file type" etc... They would then press "Generate" and a lovely eps or png file would be created with
# their desired schematic. Maybe even have the option to upload an image as the particle...
# I will need to use PIL to generate images and tkinter for the interface. Probably a bunch of other stuff too like
# random to randomly position the dispersion particles. Certainly numpy for handling the data.

# Idea: read size distribution by creating loops that add shapes for each bin size. Normalize the total number (and
# area covered) of shapes by calculating total area covered before running through it.

# TO DO (potentially): helper function to control border thickness, tkinter GUI (bundle all into a class),
# draw box outline (choose thickness and colour), rotate anisotropic ones (temporarily make each particle it's own Image object
# and rotate that), shape chooser, add aspect ratio to function arguments.

# EXTRAS ADDED:  
# Antialiasing - allows you to make smaller images that don't look pixelated
# Script placed in function: so you can easily repeat it a few times to "weight" the particle size distribution or 
# introduce different coloured particles
# Improved code to place only ellipse pixel coordinates in banned_pixel_set


#import sys
from PIL import Image, ImageDraw, ImageColor
import numpy as np
import random as rd

# The arguments for the function are: 
# image: if you want to load an image file generated by schematic_generator()
# banned_pixels: loads the banned_pixel_set generated by schematic_generator()
# tot_ell_area: loads the total_ellipse_area generated by schematic_generator() 
# ih: stands for image height 
# iw: stands for image width
# fac: stands for factor (for antialiasing) 
# bg: stands for background colour - will only be used when generating new Image object 
# fill: choose the colour of your particles # You can't make fill = None - it won't work.
# outline: choose the outline colour of your particles (can't control thickness yet) - Antialiasing kind of smudges it out anyway
# min_size_ratio: this is the lower size limit of your particles relative to image HEIGHT
# max_size_ratio: the upper size limit of your particles relative to image HEIGHT
# af: stands for area fraction - the total relative amount of area you want covered by your particles (cumulative). 
"""
Example usage:

first, bps, tea = schematic_generator(ih=1024,iw=1024,fac=4, bg="grey", fill="red", outline = "black", min_size_ratio=0.1, max_size_ratio=0.2, \
    af = 0.1)

second, bps2, tea2 = schematic_generator(image=first, banned_pixels = bps, tot_ell_area=tea, ih=1024,iw=1024, fill="orange", outline = "white", \
    min_size_ratio=0.05, max_size_ratio=0.1, af = 0.3)

third, bps3, tea3 = schematic_generator(image=second, banned_pixels = bps2, tot_ell_area=tea2, ih=1024,iw=1024, fill="green", min_size_ratio=0.01, \
    max_size_ratio=0.05, af = 0.55)

Note how af goes up.
"""

def schematic_generator(image = None, banned_pixels = None, tot_ell_area = None, ih=512, iw=512, fac=4, bg = "blue", fill = "yellow", \
    outline = None, min_size_ratio = 0.01, max_size_ratio = 0.04, af = 0.2):
    final_image_height = ih
    final_image_width = iw
    factor = fac
    working_image_height = final_image_height*factor
    working_image_width = final_image_width*factor # Don't make it too big - it struggled to do 10000 x 10000 pixels (not very efficient code I'm sure)
    box_bg_colour = bg
    ellipse_edge_colour = outline
    ellipse_fill_colour = fill
    ellipse_aspect_ratio = 1

    if image != None:
        im1 = image
        banned_pixel_set = banned_pixels
        total_ellipse_area = tot_ell_area
    elif image == None:
        im1 = Image.new("RGB", (working_image_width, working_image_height), color = box_bg_colour)
        banned_pixel_set = set()
        total_ellipse_area = 0

    min_ellipse_size = int(min_size_ratio*im1.height)
    max_ellipse_size = int(max_size_ratio*im1.height)

    total_box_area = im1.height*im1.width 
    
    area_fraction = af # Don't go higher than ~0.5 as it starts taking a long time to find a gap to put the last ones in.
    # do note that area fraction is always the final total area fraction including previously called functions (as we return total ellipse area)
    
    #loops = 0 
    rejection_counter = 0 # By counting rejections we can escape an infinite while loop if area_fraction too high

    while total_ellipse_area < (area_fraction*total_box_area) and rejection_counter < 1000: 
    # rejection counter at 1000 gives area_fraction ~0.5 if small particles are being generated
    #while loops < 200: # If you want a particular number of ellipses - just make sure you add a conditional to exit
    # the while loop if you put too many ellipses in - it could loop infinitely otherwise. Also don't forget to uncomment
    # the loops = 0 line above and the loops += 1 bit at the end of the while loop.
        #ellipse_aspect_ratio = 0.2 + rd.random()*1.6 # this will give a range from 0.2-1.6 - need to find a way of
        #rotating the object too.
        ellipse_width = rd.randrange(min_ellipse_size,max_ellipse_size)
        ellipse_height = ellipse_aspect_ratio*ellipse_width
        LeftEdge = rd.randrange(2,working_image_width-(int(ellipse_width)+2))
        RightEdge = LeftEdge + int(ellipse_width)
        TopEdge = rd.randrange(2,working_image_height-(int(ellipse_height)+2))
        BottomEdge = TopEdge + int(ellipse_height)
        break_first_for_loop = False
        rejected = False

        for xpos in range(LeftEdge, RightEdge): # Try adding a loop that just check edge pixels (if possible)
            for ypos in range (TopEdge, BottomEdge):
                if (xpos, ypos) in banned_pixel_set:
                    #point = ImageDraw.Draw(im1) # Debugging
                    #point.point([xpos,ypos], fill='red') # Debugging - red dot appears where overlap has been rejected
                    rejected = True
                    break_first_for_loop = True
                    rejection_counter += 1 # Add one to the rejection counter!
                    break
                else:
                    pass
            if break_first_for_loop == True: # Ensures both for loops are exited
                break
        if rejected == True:
            pass
        else:
            draw = ImageDraw.Draw(im1)
            ell = draw.ellipse([(LeftEdge, TopEdge), (RightEdge, BottomEdge)], fill = ellipse_fill_colour, \
            outline = ellipse_edge_colour)
            ellipse_area = (0.5*ellipse_height)*(0.5*ellipse_width)*np.pi
            total_ellipse_area += ellipse_area
            rejection_counter = 0 # Reset rejection counter if ellipse drawn
            #print ('{:.2f}'.format(total_ellipse_area)) # Debugging
            # So here I want to return a set or array of ellipse pixel coordinates (not bounding box coordinates)
            r1 = int((RightEdge - LeftEdge)/2)
            r2 = int((BottomEdge - TopEdge)/2)
            x0 = int(LeftEdge + r1)
            y0 = int(TopEdge + r2)
            if fill != None:
                fillRGB = ImageColor.getrgb(fill)
                fillR, fillG, fillB = fillRGB[0], fillRGB[1], fillRGB[2]
            if outline != None:
                outlineRGB = ImageColor.getrgb(outline)
                outlineR, outlineG, outlineB = outlineRGB[0], outlineRGB[1], outlineRGB[2]
            for x in range(LeftEdge,RightEdge+1):
                for y in range(TopEdge,BottomEdge+1):
                    #if ((x - x0)/r1)**2 + ((y - y0)/r2)**2 <= 1:
                        #banned_pixel_set.add((x,y))
                    if outline == None:
                        if im1.getpixel((x,y)) == (fillR, fillG, fillB):
                            banned_pixel_set.add((x,y))
                    else:
                        if im1.getpixel((x,y)) == (fillR, fillG, fillB) or im1.getpixel((x,y)) == \
                        (outlineR, outlineG, outlineB):
                            banned_pixel_set.add((x,y))                        
                    #if 0.8 <= ((x - x0)/r1)**2 + ((y - y0)/r2)**2 <= 1: # Way of drawing a border with thickness relative to particle size
                        #check = ImageDraw.Draw(im1) # Debugging - this check let me know banned_pixel_set is working fine
                        #check.point([x,y], fill = "black")
            #loops+=1
        print ("Rejection count: {}".format(rejection_counter))

    print("{0:.2f} : {1:.2f}".format(total_ellipse_area/total_box_area, area_fraction))
    #im1.save("test.eps", "EPS")
    im1_resized = im1.resize((final_image_width, final_image_height), resample=Image.ANTIALIAS)
    im1_resized.show()
    print (fill)
    return im1, banned_pixel_set, total_ellipse_area # This will return the large version of the image to pass into another function
    

first, bps, tea = schematic_generator(ih=1024,iw=1024,fac=4, bg="white", fill="red", \
    min_size_ratio=0.2, max_size_ratio=0.3, af = 0.1161)
second, bps2, tea2 = schematic_generator(image=first, banned_pixels = bps, tot_ell_area=tea, ih=1024,iw=1024, \
    fill="blue", min_size_ratio=0.05, max_size_ratio=0.2, af = 0.1161+0.1076)
third, bps3, tea3 = schematic_generator(image=second, banned_pixels = bps2, tot_ell_area=tea2, ih=1024,iw=1024, \
    fill="grey", min_size_ratio=0.02, max_size_ratio=0.05, af = 0.1161+0.1076+0.0862)