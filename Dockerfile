FROM python:3.10

RUN mkdir -p /srv/pol-tracker
RUN mkdir -p /data
RUN mkdir -p /docs

COPY data /data
COPY src /srv/pol-tracker

#####
# Custom Section
RUN pip install beautifulsoup4 requests
#####

WORKDIR /srv
ENTRYPOINT [ "python3" ]
CMD [ "-m", "pol-tracker"]
