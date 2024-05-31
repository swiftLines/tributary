FROM python:3.11
COPY ./entrypoint.py .
COPY ./requirements.txt .
RUN pip install -r requirements.txt
CMD exec gunicorn entrypoint:app
# CMD python entrypoint.py
# CMD echo "hello world"