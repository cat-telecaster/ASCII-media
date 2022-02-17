import os
import json
import base64
import filetype

from ASCIIfy import *

# INPUTS:
MEDIA_PATH = 'ENTER_INPUT_PATH_HERE'
letters = """$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,"^`'. """  # Lookup string for ASCII
SCALE = 1.00        # Video resolution scaling for video out
CANNY = True        # Canny image processing via CV2
output_w = 1080     # Defined output width for ASCII image out
output_h = 1080     # Defined output height for ASCII image out
invert = True       # Invert intensity range; recommended when canny image processing is in use
IMAGE_PATH = '/ENTER_OUTPUT_PATH_HERE/result.jpg'
VID_PATH = '/ENTER_OUTPUT_PATH_HERE/output.mp4'

if __name__ == '__main__':
    media = filetype.guess(MEDIA_PATH)
    if media is None:
        print('Cannot guess file type!!!')
    else:
        print('This is a {0}'.format(media.mime.split('/')[0]))
        media_type = media.mime.split('/')[0]

    # Generate the ASCII lookup stack
    ascii_stack = generate_ascii_letters(letters, invert)
    if ascii_stack is False:
        print('ERROR: ASCII lookup string may be invalid.')

    if media_type == 'image':
        raw_img = cv2.imread(MEDIA_PATH, cv2.IMREAD_GRAYSCALE)

        # Resize to input dimensions defined by user input
        img = resize_cv2image(raw_img,
                              target_width=output_w,
                              target_height=output_h)

        # Convert image
        if CANNY:
            gb = cv2.GaussianBlur(img, (5, 5), 0)
            can = cv2.Canny(gb, 127, 31)
            ASCII_image = ascii_via_intensity(can, ascii_stack)
        else:
            ASCII_image = ascii_via_intensity(img, ascii_stack)

        # Save the output
        cv2.imwrite(IMAGE_PATH, ASCII_image)
        print('IMAGE CONVERSION DONE!!!')

    elif media_type == 'video':
        raw_vid = cv2.VideoCapture(MEDIA_PATH, cv2.IMREAD_GRAYSCALE)

        if raw_vid.isOpened() == False:
            print('Error opening video.')
        else:
            fps = raw_vid.get(5)
            print('Frame Rate: {0}'.format(fps))
            frame_count = raw_vid.get(7)
            print('Frame count: {0}'.format(frame_count))

        # Generate and save video
        ascii_vid = ascii_vid_convert(raw_vid,
                                      ascii_stack,
                                      PATH=VID_PATH,
                                      scale=SCALE,
                                      canny_edge=CANNY)
        print('VIDEO CONVERSION DONE!!!')
