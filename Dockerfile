FROM ubuntu:latest

RUN apt-get update && apt install python3 python3-pip nano -y

WORKDIR /server
ADD main.py .
ADD requirements.txt .
RUN pip install -r /server/requirements.txt

CMD ["python3", "/server/main.py"]