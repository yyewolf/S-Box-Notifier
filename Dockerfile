FROM python:3.9-alpine

# update apk repo
RUN echo "http://dl-4.alpinelinux.org/alpine/v3.14/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.14/community" >> /etc/apk/repositories && \
    apk update

RUN apk add chromium chromium-chromedriver xvfb && \
    pip install selenium && \
    pip install requests && \
    pip install undetected_chromedriver && \
    pip install pyvirtualdisplay

COPY script.py /script.py
CMD ["python", "-u", "/script.py"]