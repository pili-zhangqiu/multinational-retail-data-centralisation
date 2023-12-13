--Remove £ symbol from price column:
UPDATE dim_products 
SET product_price = REPLACE(product_price, '£', '');

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

UPDATE dim_products 
SET still_available = 
    CASE
        WHEN still_available = 'Still_avaliable' THEN TRUE
        WHEN still_available = 'Removed' THEN FALSE
    END;

--Cast column datatypes:
