FROM python:3
ADD harvest_chefkoch.py /
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD [ "python", "./harvest_chefkoch.py" ]
