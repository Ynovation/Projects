import zipfile
from zipfile import ZipFile

from PIL import Image, ImageDraw
import pytesseract as tess
import cv2 as cv
import numpy as np

face_cascade = cv.CascadeClassifier('readonly/haarcascade_frontalface_default.xml')

#face crop function

def detect_faces(test_image):
    # create a copy of the image to prevent any changes to the original one.
    image_copy = test_image.copy()

    #convert the test image to gray scale as opencv face detector expects gray images
    gray_image = cv.cvtColor(image_copy, cv.COLOR_BGR2GRAY)

    # Applying the haar classifier to detect faces
    faces_rect = face_cascade.detectMultiScale(gray_image, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30) )

    lst_of_face = []
    
    for (x, y, w, h) in faces_rect:
        #cv.rectangle(image_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
        roi_color = image_copy[y:y + h, x:x + w]
        #cv.imwrite(str(w) + str(h) + '_faces.jpg', roi_color)
        
        PIL_img_of_face = Image.fromarray(roi_color)
        lst_of_face.append(PIL_img_of_face)

    return lst_of_face


#function for the program

def face_detect(name_search, file_name):
    
    # specifying the zip file name 
    file_name = 'readonly/images.zip'

    imgzip = zipfile.ZipFile(file_name)
    inflist = imgzip.infolist()


    strng_vs_pic = {}

    file_names = []    
    for name in imgzip.namelist():
        file_names.append(name)

    iterator = 0

    for f in inflist:
        ifile = imgzip.open(f)
        img = Image.open(ifile)
    
        text = tess.image_to_string(img)
    
        iterator += 1
        pic_name = "image" + str(iterator)
        strng_vs_pic[pic_name]= (text, img, file_names[iterator - 1])
    

    pictures_we_will_scan_for_faces = []
    relative_file_names = []

    accumulator = 0

    for value in strng_vs_pic:
        accumulator += 1
        picz_name = "image" + str(accumulator)
        if name_search in strng_vs_pic[picz_name][0]:
            pictures_we_will_scan_for_faces.append(strng_vs_pic[picz_name][1])
            relative_file_names.append(strng_vs_pic[picz_name][2])
    
    converted_PIL_to_CVImages = []

    for item in pictures_we_will_scan_for_faces:
        imcv = cv.cvtColor(np.asarray(item), cv.COLOR_RGB2BGR)
        converted_PIL_to_CVImages.append(imcv)
        
    faces = []

    for picz in converted_PIL_to_CVImages:
        face = detect_faces(picz)
        faces.append(face)    
    
    #create contact sheet
    info_sheets = []    

    index = 0    


    for f in faces:
    
        contact_sheet = Image.new("RGB", (200 * 4, 200 * 3))
        x = 0
        y = 0
        for img in f:
            resized_img = img.resize((200, 200))
            contact_sheet.paste(resized_img, (x, y))
            if x + 200 == contact_sheet.width:
                x = 0
                y = y + 200
            else:
                x = x + 200
    
        rect = Image.new(contact_sheet.mode, (contact_sheet.width, 100), color = (255, 255, 255))
        d = ImageDraw.Draw(rect)
        d.text((10, 10), 'Results found in {}'.format(relative_file_names[index]), fill = (0, 0, 0))
        if len(f) == 0:
            d.text((10, 20), 'But there were no faces in that file!', fill = (0, 0, 0))
        if index<len(file_names):    
            index += 1
        info_sheet = Image.new(contact_sheet.mode, (contact_sheet.width, contact_sheet.height + rect.height))
        info_sheet.paste(rect, (0, 0))
        info_sheet.paste(contact_sheet, (0, 100))
        info_sheets.append(info_sheet)
    
    result = []
    
    for img in info_sheets:
        result.append(display(img))
        
    return result

face_detect('Mark', 'readonly/images.zip' )
