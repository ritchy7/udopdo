/* User creation */
/*CREATE USER 'vagrant'@'localhost' IDENTIFIED BY '1234';
GRANT ALL PRIVILEGES ON yuka_like.* TO 'vagrant'@'localhost' IDENTIFIED BY '1234';*/

/* Database creation */
CREATE DATABASE yuka_like CHARACTER SET 'utf8';

/* Tables creation */
CREATE TABLE IF NOT EXISTS Product (
    id SMALLINT UNSIGNED AUTO_INCREMENT,
    product_id INT UNIQUE NOT NULL,
    product_name VARCHAR(200),
    img_url TEXT,
    salt VARCHAR(10),
    fat VARCHAR(10),
    sugars VARCHAR(10),
    satured_fat VARCHAR(10),
    warehouse VARCHAR(30),
    allergens VARCHAR(30),
    categories VARCHAR(200),

    PRIMARY KEY (id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS History (
    id SMALLINT UNSIGNED AUTO_INCREMENT,
    product_id INT UNIQUE NOT NULL,
    CONSTRAINT fk_product_id
        FOREIGN KEY (product_id)
        REFERENCES Product(product_id),

    PRIMARY KEY (id)
) ENGINE=InnoDB;