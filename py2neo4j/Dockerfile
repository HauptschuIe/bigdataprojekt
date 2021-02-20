FROM python:3
ADD mongo_2_neo.py /
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD [ "python", "./mongo_2_neo.py" ]
