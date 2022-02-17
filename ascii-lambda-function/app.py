import os
import json
import base64
from requests_toolbelt.multipart import decoder

from ASCIIfy import *

# Write the media object to /tmp
def write_to_file(save_path, data):
    with open(save_path, "wb") as f:
        f.write(data)

# Lambda handler code
def lambda_handler(event, context):
    # Decode the multipart/form-data payload
    content_type_header = event['headers']['Content-Type']

    body = base64.b64decode(event['body'])

    response = {}
    for part in decoder.MultipartDecoder(body, content_type_header).parts:
        dispPart = str(part.headers[b'Content-Disposition']).split(';')
        kv = dispPart[1].split('=')
        obj_type = part.headers[b'Content-Type'] if b'Content-Type' in part.headers else None
        response[str(kv[1]).strip('\"\'\t \r\n')] = {'content': part.content, 'type': obj_type}

    # Generate the ASCII lookup stack
    ascii_stack = generate_ascii_letters(letters=response['letters']['content'].decode('ascii'),
                                         invert=(True if (response['invert']['content'] == b'True') else False))
    if ascii_stack is False:
        print('ERROR: ASCII lookup string may be invalid.')
        return {
            'isBase64Encoded': False,
            "statusCode": 200,
            "body": json.dumps(
                {
                    'response': 'ERROR: ASCII lookup string may be invalid.'
                }
            ),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST",
                "Access-Control-Allow-Origin": "*",  # TODO: Change to host domain for release
                "X-Requested-With": "*"
            }
        }

    media_type = response['media_obj']['type'].split(b'/')[0]
    print(media_type.decode('ascii'))

    if media_type == b'image':
        # Write image to file
        write_to_file('/tmp/photo.jpg', response['media_obj']['content'])

        # Load the image to CV2
        raw_img = cv2.imread('/tmp/photo.jpg', cv2.IMREAD_GRAYSCALE)

        ###### ASCII TRANSFORM ######
        # Resize to input dimensions defined by user input
        img = resize_cv2image(raw_img,
                              target_width=int(response['output_w']['content'].decode('ascii')),
                              target_height=int(response['output_h']['content'].decode('ascii')))

        # Convert image
        if response['canny']['content'] == b'True':
            gb = cv2.GaussianBlur(img, (5, 5), 0)
            can = cv2.Canny(gb, 127, 31)
            ascii_img = ascii_via_intensity(can, ascii_stack)
        elif response['canny']['content'] == b'False':
            ascii_img = ascii_via_intensity(img, ascii_stack)
        
        #############################

        # Write ASCII image to /tmp
        cv2.imwrite('/tmp/gray.jpg', ascii_img)

        # Convert ASCII image into utf-8 encoded base64
        with open("/tmp/gray.jpg", "rb") as imageFile:
            string = base64.b64encode(imageFile.read())
            encoded_img = string.decode("utf-8")

        return {
            'isBase64Encoded': True,
            "statusCode": 200,
            "body": encoded_img,
            "headers": {
                "Content-Type": response['media_obj']['type'],
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST",
                "Access-Control-Allow-Origin": "*",
                "X-Requested-With": "*"
            }
        }
    else:
        return {
            'isBase64Encoded': False,
            "statusCode": 200,
            "body": json.dumps(
                {
                    'response': 'ERROR: Invalid media file!!!'
                }
            ),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST",
                "Access-Control-Allow-Origin": "*",  # TODO: Enter your own
                "X-Requested-With": "*"
            }
    }
