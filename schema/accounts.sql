CREATE TABLE IF NOT EXISTS Accounts (
    /* Internal account ID */
    Id      INTEGER PRIMARY KEY AUTOINCREMENT,
    Name    VARCHAR,
    Balance FLOAT DEFAULT 0 );
