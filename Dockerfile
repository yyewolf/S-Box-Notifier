FROM python:3.9-alpine

# update apk repo
RUN echo "http://dl-4.alpinelinux.org/alpine/v3.14/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.14/community" >> /etc/apk/repositories && \
    apk update

RUN apk add chromium chromium-chromedriver && \
    pip install selenium && \
    pip install requests

COPY public.py /public.py
CMD ["python", "/public.py"]