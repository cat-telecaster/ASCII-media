# Pull the base image with python 3.8 as a runtime for Lambda
FROM public.ecr.aws/lambda/python:3.8

# COPY the python requirements from requirements.txt and app.py to container
COPY app.py ASCIIfy.py requirements.txt ./
RUN python3.8 -m pip install -r requirements.txt -t .

# Set CMD to handler
CMD ["app.lambda_handler"]