# Baseimage
FROM python:3.12.10-slim-bookworm

# Update Packages
RUN apt update
RUN apt upgrade -y
RUN pip install --upgrade pip
# install git
RUN apt-get install build-essential -y


RUN mkdir /CrewAI-Studio

# Relax TLS/SSL verification for all runtime components
ENV PYTHONHTTPSVERIFY=0 \
    REQUESTS_CA_BUNDLE= \
    CURL_CA_BUNDLE= \
    SSL_CERT_FILE=

# Install requirements
COPY ./requirements.txt /CrewAI-Studio/requirements.txt
WORKDIR /CrewAI-Studio
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# Copy CrewAI-Studio
COPY ./ /CrewAI-Studio/

# Run app
CMD ["streamlit","run","./app/app.py","--server.headless","true"]
EXPOSE 8501
