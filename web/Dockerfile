FROM node:16.17-alpine3.15 as builder

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app


COPY ./ ./

RUN npm install -g tyarn \
    && tyarn install --silent --no-cache --registry=https://registry.npm.taobao.org \
    && tyarn run build


FROM nginx

WORKDIR /usr/share/nginx/html/
COPY ./nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /usr/src/app/dist /usr/share/nginx/html/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]





