CREATE TABLE random_numbers (
    id SERIAL PRIMARY KEY,
    value FLOAT NOT NULL
);

INSERT INTO random_numbers (value) VALUES
    (3.14),
    (1.618),
    (2.718),
    (0.577),
    (4.669);
