FROM python:3.9-slim-buster
RUN apt update && apt install -y curl gcc make g++
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt install -y nodejs
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY lib src public flows pod-logs package.json ./
RUN npm install
RUN npm run build

CMD [ "echo", "hello" ]
