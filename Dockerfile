FROM python:3.8-alpine

WORKDIR /app

COPY . /app

RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

EXPOSE 5000
ENTRYPOINT ["python3"]
CMD ["app.py"]
