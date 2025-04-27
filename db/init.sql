-- init.sql
CREATE TABLE random_numbers (
    id SERIAL PRIMARY KEY,
    value FLOAT NOT NULL
);

COPY random_numbers(value)
FROM '/docker-entrypoint-initdb.d/data/random_numbers.csv'
DELIMITER ',' CSV HEADER;