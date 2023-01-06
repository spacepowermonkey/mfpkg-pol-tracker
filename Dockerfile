FROM python:3.10

RUN mkdir -p /srv/{{PKG_NAME}}
RUN mkdir -p /data
RUN mkdir -p /docs

COPY data /data
COPY src /srv/{{PKG_NAME}}

#####
# Custom Section

#####

WORKDIR /srv
ENTRYPOINT [ "python3" ]
CMD [ "-m", "{{PKG_NAME}}"]
