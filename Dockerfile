FROM python:3.12.5-slim-bullseye
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ./polybot ./polybot
ENTRYPOINT ["python", "-m"]
CMD ["polybot.app"]
