FROM python:slim-bullseye
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ./polybot ./polybot
ENTRYPOINT ["python", "-m"]
CMD ["polybot.app"]
