from PIL import Image
import glob
import random
import shutil, os

'''
This program takes source images (the cropped down and shrunk images)
and creates an image of the inputed image using them.
'''

global source_size #recommened 25
global max_crop_size #recommened 300
global min_crop_size #recommened 4000+
global input_resize_factor #recommened 6

input_resize_factor = int(intput("Input Resize Factor: ")) 
#factor of which input image is shrunk
min_crop_size = int(intput("Min Source Size: ")) 
#minimium source dimention
max_crop_size = int(intput("Max Source Size: ")) 
#maximum source dimention
source_size = int(intput("Resized Source Image Size: ")) 
#rescaled source size
#these factors change quality and size of outputed image

def InputArray(filename): #inputs image and processes it and stores rgb in array

    input_image = Image.open(filename)

    width, height = input_image.size
    width = int(width/input_resize_factor)
    height = int(height/input_resize_factor)

    input_image = input_image.resize((width, height), Image.ANTIALIAS)
    
    input_image_array = []
    image_array = []

    for y in range(height): #gets each pixel and adds it to array
        for x in range(width):
            try:
                r, g, b = input_image.getpixel((x, y))
            except:
                r, g, b, a = input_image.getpixel((x, y))
            input_image_array.append((r, g, b))

    return input_image_array, (width, height)


def SourceImages(): #gets source images and processes them

    image_list = []
    image_list_ims = []
    
    for filename in glob.glob('source/*'): #for each file in source dir
        try:
            im=Image.open(filename)
            width, height = im.size

            #if it meets requirements
            if (width >= min_crop_size and height >= min_crop_size and
                    width <= max_crop_size and height <= max_crop_size): 
                
                if width > height:
                    smallest_length = height
                elif width < height:
                    smallest_length = width
                else:
                    smallest_length = width

                #get dimmentions to make it square
                left = (width - smallest_length) / 2 
                right = (width + smallest_length) / 2
                top = (height - smallest_length) / 2
                bottom = (height + smallest_length) / 2


                # Crop to the center of the image to make it square
                #and resize it
                im = im.crop((left, top, right, bottom))
                im = im.resize((source_size, source_size), Image.ANTIALIAS)
                
                total_r = 0
                total_g = 0
                total_b = 0

                #gets the average colour of the source
                for y in range(source_size): 
                    for x in range(source_size):
                        try:
                            r, g, b = im.getpixel((x, y))
                        except:
                            #png images that have 4th channel
                            r, g, b, a = im.getpixel((x, y))
                        total_r = total_r + r
                        total_g = total_g + g
                        total_b = total_b + b

                total = total_r + total_g + total_b
                r = int(total_r / (source_size*source_size))
                g = int(total_g / (source_size*source_size))
                b = int(total_b / (source_size*source_size))

                #adds each images average colour and image to array
                image_list.append((r, g, b))
                image_list_ims.append(im)

            else:
                #if its wrong size move it to wrongsize folder
                #so it doesnt need to be reprocesed when used again
                im.close()
                name = filename.split("\\")[1]
                source = filename
                des = "wrongsize\\"
                shutil.move(source, des)
                os.remove(source)
        except Exception as e: print(e) #if non images are in file
    
    return image_list, image_list_ims


def Match(input_array, source_array, source_ims):
    #for each pixel in input find matching source image
    index_list = []
    
    for input_number in range(len(input_array)): #each pixel index in input
        input_rgb = input_array[input_number] 
        input_r, input_g, input_b = input_rgb #get input rgb values
        best_difference = 1000
        best_index = 0
        for source_number in range(len(source_array)): #for each source index
            source_rgb = source_array[source_number]
            source_r, source_g, source_b = source_rgb
            diff_r = input_r-source_r
            diff_g = input_g-source_g
            diff_b = input_b-source_b
            if diff_r < 0:
                diff_r *= -1
            if diff_g < 0:
                diff_g *= -1
            if diff_b < 0:
                diff_b *= -1
            #find the overall difference in values
            total_difference = diff_r + diff_g + diff_b
            if total_difference < best_difference:
                best_difference = total_difference
                best_index = source_number #find best source image
        index_list.append(best_index)

    return index_list

def Create(index_list, source_ims, input_size, source_array, input_array):
    #takes chosen source images and creates overall image
    #using large nested loop

    input_w, input_h = input_size
    output_array = []

    for row in range(input_h): #for every row in the input image
        if row % 10 == 0:
            print("Row", row, "/", input_h)
            
        for image_row in range(source_size): #for ever row in the source images
            
            for image_number in range(input_w): #for every image in that row
                #get the source image
                image_index = index_list[ (row * input_w) + image_number] 
                image = source_ims[image_index]
                
                for image_pixel in range(source_size):
                    #for each pixel in the row of the source image
                    
                    try:
                        pixel_r, pixel_g, pixel_b = image.getpixel(
                            (image_pixel, image_row))
                    except:
                        pixel_r, pixel_g, pixel_b, a = image.getpixel(
                            (image_pixel, image_row))
                        
                    #add those pixels to the overall image
                    output_array.append((pixel_r, pixel_g, pixel_b))

    #creates final image and saves it in output folder
    output_height = input_h * source_size
    output_width = input_w * source_size
    im = Image.new("RGB", (output_width, output_height))
    im.putdata(output_array)
    im.save("output/" + str(random.randint(1,1000)) + ".jpg")

#main loop
print("Getting Source Images")
source_array, source_ims = SourceImages()
      
for filename in glob.glob('input/*'): #each input image in input folder
    print("Getting Input Image")
    input_array, input_size = InputArray(filename)

    print("Matching Pixels")
    index_list = Match(input_array, source_array, source_ims)

    print("Creating Final Image")
    Create(index_list, source_ims, input_size, source_array, input_array)
print("Done")
