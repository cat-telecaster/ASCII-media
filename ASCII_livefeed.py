import cv2
import numpy as np


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


# Generate the ASCII image array to match with the ROI
def generate_ascii_letters():
    images = []
    #letters = "# $%&\\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_`abcdefghijklmnopqrstuvwxyz{|}~"
    #letters = " \\ '(),-./:;[]_`{|}~"
    #letters = """$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,"^`'. """
    letters = """ .'`^",:;Il!i><~+_-?][}{1)(|\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$""" # Reverse of lookup string
    for letter in letters:
        img = np.zeros((8, 8), np.uint8)
        img = cv2.putText(img, letter, (-1, 8), cv2.FONT_HERSHEY_PLAIN, 0.7, 255)
        images.append(img)
    return np.stack(images)


# Setup camera
cap = cv2.VideoCapture(0)
# Set a smaller resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

images = generate_ascii_letters()

while True:
    # Capture frame-by-frame
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)

    gb = cv2.GaussianBlur(frame, (5, 5), 0)
    can = cv2.Canny(gb, 127, 31)

    ascii_art = ascii_via_intensity(can, images)

    cv2.imshow('ASCII ART', ascii_art)
    cv2.imshow("Webcam", frame)

    if cv2.waitKey(1) == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()