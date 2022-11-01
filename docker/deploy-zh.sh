#! /bin/bash


STAT_JOBS=("en" 0 "zh" 0 "ja" 0 "de" 0 "nl" 0 "fr" 0 "es" 0)

CUR_DIR=$(cd `dirname $0`; pwd)

UNIX_TIME=$(date +%s)
DOCKER_COMPOSE_FILE="${CUR_DIR}/docker-compose_${UNIX_TIME}.yml"


ARGS=${@}

function generate_web_yaml() {
    cat >> ${DOCKER_COMPOSE_FILE} <<- EOF
  canary-web:
    container_name: canary-web

    build:
      context: "../web"
      dockerfile: "./Dockerfile.zh"
    volumes:
      - dist:/usr/src/app/dist
    depends_on:
      - canary-server
    ports:
      - 10005:80

EOF
}

function generate_redis_yaml() {
    cat >> ${DOCKER_COMPOSE_FILE} <<- EOF
  canary-redis:
    image: "redis:alpine"

    container_name: canary-redis

    command: redis-server --port \${REDIS_PORT} --requirepass \${REDIS_PASSWORD} --appendonly yes

    expose:
      - \${REDIS_PORT}
    restart: always

EOF
}

function generate_db_yaml() {
    cat >> ${DOCKER_COMPOSE_FILE} <<- EOF
  canary-db:
    image: mysql:8.0
    hostname: "canary-db"
    container_name: canary-db

    environment:
      MYSQL_ROOT_PASSWORD: \${DB_PASSWORD}
      MYSQL_DATABASE: \${DB_DATABASE}
      MYSQL_TCP_PORT: \${DB_PORT}
    volumes:
      - \${HOME}/.canary/data/mysql:/var/lib/mysql:rw
      - ../server/deploy/voice.sql:/docker-entrypoint-initdb.d/voice.sql:ro
    expose:
      - \${DB_PORT}
    restart: always
    command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci

EOF
}

function generate_minio_yaml() {
    cat >> ${DOCKER_COMPOSE_FILE} <<- EOF
  canary-minio:
    image: "minio/minio"
    hostname: "canary-minio"
    container_name: canary-minio

    environment:
      MINIO_ACCESS_KEY: \${MINIO_ACCESS_KEY}
      MINIO_SECRET_KEY: \${MINIO_SECRET_KEY}
    volumes:
      - \${HOME}/.canary/data/minio:/data
    command: server --address ":\${MINIO_PORT}" --console-address ":\${MINIO_CONSOLE_PORT}" /data
    privileged: true
    restart: always

EOF
}

function generate_rq_dashboard_yaml() {
    cat >> ${DOCKER_COMPOSE_FILE} <<- EOF
  rq-dashboard:
    hostname: "canary-rq-dashboard"
    container_name: canary-rq-dashboard

    command: -u redis://:\${REDIS_PASSWORD}@\${REDIS_HOST}:\${REDIS_PORT}/0

    build:
      context: ../server
      dockerfile: ./Dockerfile.rq_dashboard.zh
    environment:
      RQ_DASHBOARD_USERNAME: \${RQ_DASHBOARD_USERNAME}
      RQ_DASHBOARD_PASSWORD: \${RQ_DASHBOARD_PASSWORD}
    ports:
      - 39181:9181
    depends_on:
      - canary-redis

EOF
}

function generate_server_yaml() {
  SERVER_TYPE=${1}
    cat >> ${DOCKER_COMPOSE_FILE} <<- EOF
  canary-${SERVER_TYPE}:
    container_name: canary-${SERVER_TYPE}
    environment:
      DB_HOST: \${DB_HOST}
      DB_PORT: \${DB_PORT}
      DB_USER: \${DB_USER}
      DB_PASSWORD: \${DB_PASSWORD}
      DB_DATABASE: \${DB_DATABASE}

      REDIS_HOST: \${REDIS_HOST}
      REDIS_PORT: \${REDIS_PORT}
      REDIS_PASSWORD: \${REDIS_PASSWORD}

      EMAIL_SMTP_SERVER: \${EMAIL_SMTP_SERVER}
      EMAIL_SMTP_PORT: \${EMAIL_SMTP_PORT}
      EMAIL: \${EMAIL}
      EMAIL_PASSWORD: \${EMAIL_PASSWORD}
      EMAIL_SSL: \${EMAIL_SSL}

      JWT_SALT: \${JWT_SALT}

      MINIO_HOST: \${MINIO_HOST}
      MINIO_PORT: \${MINIO_PORT}
      MINIO_ACCESS_KEY: \${MINIO_ACCESS_KEY}
      MINIO_SECRET_KEY: \${MINIO_SECRET_KEY}

      PODCAST_SHARE_SECRET_SALT: \${PODCAST_SHARE_SECRET_SALT}

    build:
      context: ../server
      dockerfile: ./Dockerfile.zh
      target: ${SERVER_TYPE}
    depends_on:
      - canary-db
      - canary-redis
      - canary-minio
    volumes:
      - \${HOME}/.ttsvm:/root/.ttsvm
    ports:
      - 8576:8576
    restart: always

EOF
}

function generate_scheduler_yaml() {
  SERVER_TYPE=${1}
    cat >> ${DOCKER_COMPOSE_FILE} <<- EOF
  canary-${SERVER_TYPE}:
    container_name: canary-${SERVER_TYPE}
    environment:
      DB_HOST: \${DB_HOST}
      DB_PORT: \${DB_PORT}
      DB_USER: \${DB_USER}
      DB_PASSWORD: \${DB_PASSWORD}
      DB_DATABASE: \${DB_DATABASE}

      REDIS_HOST: \${REDIS_HOST}
      REDIS_PORT: \${REDIS_PORT}
      REDIS_PASSWORD: \${REDIS_PASSWORD}

      EMAIL_SMTP_SERVER: \${EMAIL_SMTP_SERVER}
      EMAIL_SMTP_PORT: \${EMAIL_SMTP_PORT}
      EMAIL: \${EMAIL}
      EMAIL_PASSWORD: \${EMAIL_PASSWORD}
      EMAIL_SSL: \${EMAIL_SSL}

      JWT_SALT: \${JWT_SALT}

      MINIO_HOST: \${MINIO_HOST}
      MINIO_PORT: \${MINIO_PORT}
      MINIO_ACCESS_KEY: \${MINIO_ACCESS_KEY}
      MINIO_SECRET_KEY: \${MINIO_SECRET_KEY}

      PODCAST_SHARE_SECRET_SALT: \${PODCAST_SHARE_SECRET_SALT}
    build:
      context: ../server
      dockerfile: ./Dockerfile.zh
      target: ${SERVER_TYPE}
    depends_on:
      - canary-db
      - canary-redis
      - canary-minio
    volumes:
      - \${HOME}/.ttsvm:/root/.ttsvm
    restart: always
EOF
}

function generate_job_yaml() {
  JOB=${1}
  INDEX=${2}

    cat >> ${DOCKER_COMPOSE_FILE} <<- EOF
  canary-${JOB}${INDEX}:
    container_name: canary-${JOB}${INDEX}

    environment:
      DB_HOST: \${DB_HOST}
      DB_PORT: \${DB_PORT}
      DB_USER: \${DB_USER}
      DB_PASSWORD: \${DB_PASSWORD}
      DB_DATABASE: \${DB_DATABASE}

      REDIS_HOST: \${REDIS_HOST}
      REDIS_PORT: \${REDIS_PORT}
      REDIS_PASSWORD: \${REDIS_PASSWORD}

      EMAIL_SMTP_SERVER: \${EMAIL_SMTP_SERVER}
      EMAIL_SMTP_PORT: \${EMAIL_SMTP_PORT}
      EMAIL: \${EMAIL}
      EMAIL_PASSWORD: \${EMAIL_PASSWORD}
      EMAIL_SSL: \${EMAIL_SSL}

      JWT_SALT: \${JWT_SALT}

      MINIO_HOST: \${MINIO_HOST}
      MINIO_PORT: \${MINIO_PORT}
      MINIO_ACCESS_KEY: \${MINIO_ACCESS_KEY}
      MINIO_SECRET_KEY: \${MINIO_SECRET_KEY}

      PODCAST_SHARE_SECRET_SALT: \${PODCAST_SHARE_SECRET_SALT}
    build:
      context: ../server
      dockerfile: ./Dockerfile.zh
      target: job
      args:
        JOB: ${JOB}
    depends_on:
      - canary-db
      - canary-redis
      - canary-minio
    volumes:
      - \${HOME}/.ttsvm:/root/.ttsvm
    restart: always

EOF
}

function generate_langs_yaml() {
  for(( i=0;i<${#STAT_JOBS[@]};i+=2)) {
    j=$((i+1))
    if [ ${STAT_JOBS[$j]} -gt 0 ]; then
      for INDEX in `seq 1 ${STAT_JOBS[$j]}`
      do
        generate_job_yaml ${STAT_JOBS[$i]} ${INDEX} 
      done 
    fi
  }
}

function generate_volumn_yaml() {
  cat >> ${DOCKER_COMPOSE_FILE} <<- EOF
volumes:
  dist:
EOF
}

function generate_dockercompose_file() {
    echo 'version: "3"' > ${DOCKER_COMPOSE_FILE}
    echo "services:" >> ${DOCKER_COMPOSE_FILE}
    
    generate_redis_yaml
    generate_db_yaml
    generate_minio_yaml
    generate_rq_dashboard_yaml
    generate_web_yaml
    generate_server_yaml "server"
    generate_scheduler_yaml "scheduler"
    generate_job_yaml "other" ""
    generate_langs_yaml 
    generate_volumn_yaml
}

function parse_args() {
  for LANGUAGE in ${ARGS}
  do
    i=0
    for(( i=0;i<${#STAT_JOBS[@]};i+=2))
    do
      if [ "$LANGUAGE" = "${STAT_JOBS[$i]}" ]
      then
        j=$((i+1))
        (( STAT_JOBS[$j]++ ))
      fi
    done
  done
}

function compose_up() {
  cd ${CUR_DIR}
  docker-compose -f ${DOCKER_COMPOSE_FILE} up -d
}

function run() {
  parse_args
  generate_dockercompose_file
  compose_up
  docker image prune -f
}

run