FROM postgres:13.4
RUN mkdir -p "$PGDATA" && chmod 700 "$PGDATA"
ADD init.sql /docker-entrypoint-initdb.d
EXPOSE 5432