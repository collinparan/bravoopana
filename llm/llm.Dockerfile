FROM python:3.10-buster

WORKDIR /llm
COPY ./llm/requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt 
COPY ./llm ./
RUN chmod u+x llm.py 

ENTRYPOINT ["python","llm.py"]

EXPOSE 81
