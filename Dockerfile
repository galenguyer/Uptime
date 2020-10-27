# First build React app
FROM node:12.16.2 as build-deps

WORKDIR /usr/src/app

COPY uptime-web/package.json uptime-web/yarn.lock ./

RUN yarn

COPY uptime-web/ ./

RUN yarn build

# create the final image with nginx preinstalled
FROM docker.galenguyer.com/nginx-auto/nginx-simple:latest

RUN apk add python3 supervisor \
    && ln -sf python3 /usr/bin/python \
    && python3 -m ensurepip \
    && pip3 install --upgrade pip setuptools wheel

WORKDIR /var/www/html

COPY --from=build-deps /usr/src/app/build /var/www/html

WORKDIR /app

COPY uptime-api/requirements.txt ./

RUN pip3 install -r requirements.txt

COPY uptime-api/ .

# copy config files 
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY nginx.conf /etc/nginx/nginx.conf

# configure entrypoint
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
