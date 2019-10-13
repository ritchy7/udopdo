/* Database creation */
CREATE DATABASE IF NOT EXISTS openfoodfacts CHARACTER SET 'utf8';

/* User creation & privileges */
CREATE USER IF NOT EXISTS 'vagrant'@'localhost' IDENTIFIED BY '1234';
GRANT ALL PRIVILEGES ON openfoodfacts.* TO 'vagrant'@'localhost' IDENTIFIED BY '1234';

/* ****************** */
/* Tables creation */
/* ****************** */
/* Category */
CREATE TABLE IF NOT EXISTS openfoodfacts.Category (
    id SMALLINT UNSIGNED AUTO_INCREMENT,
    category_name VARCHAR(200),

    PRIMARY KEY (id)
) ENGINE=InnoDB;

/* Product */
CREATE TABLE IF NOT EXISTS openfoodfacts.Product (
    id SMALLINT UNSIGNED AUTO_INCREMENT,
    product_name VARCHAR(200),
    product_url TEXT,
    salt VARCHAR(10),
    fat VARCHAR(10),
    sugars VARCHAR(10),
    saturated_fat VARCHAR(10),
    warehouse TEXT,
    allergens TEXT,
    nutrition_grades CHAR(1),
    category_id SMALLINT UNSIGNED NOT NULL,
    CONSTRAINT fk_category_id
        FOREIGN KEY (category_id)
        REFERENCES Category(id),

    PRIMARY KEY (id)
) ENGINE=InnoDB;

/* History */
CREATE TABLE IF NOT EXISTS openfoodfacts.History (
    id SMALLINT UNSIGNED AUTO_INCREMENT,
    product_id SMALLINT UNSIGNED UNIQUE NOT NULL,
    CONSTRAINT fk_product_id
        FOREIGN KEY (product_id)
        REFERENCES Product(id),

    PRIMARY KEY (id)
) ENGINE=InnoDB;