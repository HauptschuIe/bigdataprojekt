FROM python:3
ADD api.py /
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD [ "python", "./api.py" ]
