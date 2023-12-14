--Remove £ symbol from price column:
ALTER TABLE dim_products
RENAME COLUMN product_price to product_price_in_gbp;

UPDATE dim_products 
SET product_price_in_gbp = REPLACE(product_price_in_gbp, '£', '');

--Add weight class column:
ALTER TABLE dim_products 
ADD COLUMN weight_class VARCHAR(255);

UPDATE dim_products 
SET weight_class = 
    CASE 
        WHEN weight_in_kg < 2 THEN 'Light'
        WHEN weight_in_kg >= 2 AND weight_in_kg < 40 THEN 'Mid_Sized'
        WHEN weight_in_kg >= 40 AND weight_in_kg < 140 THEN 'Heavy'
        WHEN weight_in_kg >= 140 THEN 'Truck_Required'
    END;

--Rename and parse 'removed' column:
ALTER TABLE dim_products
RENAME COLUMN removed to still_available;

ALTER TABLE dim_products ALTER still_available TYPE bool USING 
    CASE
        WHEN still_available = 'Still_avaliable' THEN TRUE
        WHEN still_available = 'Removed' THEN FALSE
    END;

--Cast column datatypes:
ALTER TABLE dim_products
ALTER COLUMN product_price_in_gbp TYPE float USING product_price_in_gbp::float,
ALTER COLUMN weight_in_kg TYPE float,
ALTER COLUMN "EAN" TYPE varchar(14),
ALTER COLUMN product_code TYPE varchar(12),
ALTER COLUMN date_added TYPE date,
ALTER COLUMN uuid TYPE uuid USING uuid::uuid,
ALTER COLUMN still_available TYPE boolean;
