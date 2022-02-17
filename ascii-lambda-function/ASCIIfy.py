# ASCIIfy.py - Functions for ASCII conversion
import numpy as np
import cv2

# Resize the image as specified dimensions to be divided by Region of Interest (ROI)
def resize_cv2image(image, target_width=640, target_height=480):
    dim = int(image.shape[1]*target_width/image.shape[1]), int(image.shape[0]*target_height/image.shape[0])
    return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)


# Generate the ASCII image array to match with the ROI
# Returns False if letters is of invalid length
def generate_ascii_letters(letters, invert=False):
    # Check if letters are less than 256 in length, since there are only
    # 256 possible intensity levels
    if len(letters) < 0 or len(letters) > 256:
        return False

    # Populate the ASCII lookup stack based on the images inserted
    images = []
    if invert:
        letters = letters[::-1]
    for letter in letters:
        img = np.zeros((8, 8), np.uint8)
        img = cv2.putText(img, letter, (-1, 8), cv2.FONT_HERSHEY_PLAIN, 0.7, 255)
        images.append(img)

    return np.stack(images)

# Changing the image to ASCII by ROI average intensity
def ascii_via_intensity(frame, images, box_height=8, box_width=8):
    height, width = frame.shape
    for i in range(0, height, box_height):
        for j in range(0, width, box_width):
            roi = frame[i:i + box_height, j:j + box_width]
            intensity = np.mean(roi)
            ASCII_index = int(len(images) * (intensity / 256))
            roi[:,:] = images[ASCII_index]
    return frame


# Convert videos to ASCII via intensity and canny edge detection
def ascii_vid_convert(vid, images, PATH, scale=1.0, canny_edge=True):
    # Check if the video dimension is valid
    if ((vid.get(3) * vid.get(4)) % 64) == 0:
        print('Resolution is ASCII compatible!!!')
    else:
        print('***RESOLUTION NOT COMPATIBLE***')
        return False

    dim = int(vid.get(3) * scale), int(vid.get(4) * scale)
    print('Output Resolution: {0} x {1}'.format(dim[0], dim[1]))

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(PATH, fourcc, vid.get(5), dim, 0)

    while vid.isOpened():
        ret, frame = vid.read()
        if ret == True:
            if canny_edge:
                #gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gb = cv2.GaussianBlur(frame, (5, 5), 0)
                can = cv2.Canny(gb, 127, 31)
                ascii_frame = ascii_via_intensity(can, images)
                if scale != 1.0:
                    ascii_frame = cv2.resize(ascii_frame, dim, interpolation=cv2.INTER_AREA)
                out.write(ascii_frame)
            else:
                # print(frame.shape)
                #gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # plt.imshow(gray_frame)
                # print(gray_frame.shape)
                ascii_frame = ascii_via_intensity(frame, images)
                if scale != 1.0:
                    ascii_frame = cv2.resize(ascii_frame, dim, interpolation=cv2.INTER_AREA)
                out.write(ascii_frame)
        else:
            break

    # Save the video and release the opened streams
    vid.release()
    out.release()
    return out
