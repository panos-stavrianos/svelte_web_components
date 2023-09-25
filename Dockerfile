FROM python:buster

# update
RUN apt update
# install curl
RUN apt install curl
# get install script and pass it to execute:
RUN curl -sL https://deb.nodesource.com/setup_18.x | bash
# and install node
RUN apt-get install nodejs
# confirm that it was successful
RUN node -v
# npm installs automatically
RUN npm -v
RUN npm --version
RUN npm install -g yarn

WORKDIR /workspace

COPY svelte_web_components/svelte_app/package.json .
RUN yarn install

WORKDIR /server
# install python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy the rest of the files
COPY svelte_web_components .

# run the server
CMD ["uvicorn", "server:app",   "--host", "0.0.0.0", "--port", "80"]

# docker build -t svelte_web_components .
# docker run -p 5050:80 svelte_web_components
