FROM python:3.10-buster

WORKDIR /front_end
COPY ./front_end/requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt 
COPY ./front_end/ ./
RUN chmod u+x app.py 

ENTRYPOINT ["python","app.py"]

EXPOSE 80
