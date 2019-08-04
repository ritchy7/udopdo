/* Database creation */
CREATE DATABASE openfoodfacts CHARACTER SET 'utf8';

/* User creation */
/*CREATE USER 'vagrant'@'localhost' IDENTIFIED BY '1234';
GRANT ALL PRIVILEGES ON openfoodfacts.* TO 'vagrant'@'localhost' IDENTIFIED BY '1234';*/

/* Tables creation */
CREATE TABLE IF NOT EXISTS Category (
    id SMALLINT UNSIGNED AUTO_INCREMENT,
    category_name VARCHAR(200),

    PRIMARY KEY (id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Product (
    id SMALLINT UNSIGNED AUTO_INCREMENT,
    product_name VARCHAR(200),
    img_url TEXT,
    salt VARCHAR(10),
    fat VARCHAR(10),
    sugars VARCHAR(10),
    saturated_fat VARCHAR(10),
    warehouse VARCHAR(100),
    allergens VARCHAR(100),
    category SMALLINT UNSIGNED NOT NULL,
    CONSTRAINT fk_category_id
        FOREIGN KEY (category)
        REFERENCES Category(id),

    PRIMARY KEY (id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS History (
    id SMALLINT UNSIGNED AUTO_INCREMENT,
    product_id SMALLINT UNSIGNED UNIQUE NOT NULL,
    CONSTRAINT fk_product_id
        FOREIGN KEY (product_id)
        REFERENCES Product(id),

    PRIMARY KEY (id)
) ENGINE=InnoDB;