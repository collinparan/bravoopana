FROM python:3.11.1-buster

WORKDIR /front_end
COPY ./requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt 
COPY ./ ./
RUN chmod u+x app.py 

ENTRYPOINT ["python","app.py"]

EXPOSE 80
