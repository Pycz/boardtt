FROM ubuntu:14.04

RUN apt-get update
RUN apt-get install -y python-distutils-extra tesseract-ocr tesseract-ocr-eng libopencv-dev libtesseract-dev

RUN apt-get -y install python-pip
RUN pip install pillow==2.6.1

ADD . /app
WORKDIR /app

ENTRYPOINT ["bash"]
