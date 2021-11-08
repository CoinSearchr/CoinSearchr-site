
DROP TABLE coin_list;

CREATE TABLE coin_list (
    date DATETIME NOT NULL,
    id TEXT NOT NULL,
    name TEXT NOT NULL,
    symbol TEXT NOT NULL,
    source TEXT NOT NULL,

    PRIMARY KEY (date, id, name)

);
