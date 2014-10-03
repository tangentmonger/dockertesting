#use with e.g.
#sudo docker build -t longtest && sudo docker run -i longtest

FROM ubuntu

#RUN apt-get install python3 
#already part of image

RUN apt-get update

RUN apt-get install -y python3-pip #suddenly dependencies

RUN pip3 install nose
RUN pip3 install nose-json

#get the installation done first to take advantage of image caching

RUN mkdir tests
#where should this go? no home directories :S

#COPY tests/test*.py tests/
#no wildcard support (issue 6820)
COPY tests tests/


#RUN echo Done!

#CMD nosetests


