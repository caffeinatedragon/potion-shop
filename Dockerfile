FROM python:3.8.5 as temporary_image
WORKDIR /opt/potion-shop

COPY ./config/ ./config/
COPY ./static/ ./static/
COPY ./potion-shop/ ./potion-shop/

RUN pip install --upgrade pip && \
    pip install ./potion-shop/ && \
    pip install pex

EXPOSE  8000

RUN pex -r ./config/requirements.txt ./potion-shop setuptools -e potion-shop -o potion-shop.pex

CMD ["./potion-shop.pex"]
