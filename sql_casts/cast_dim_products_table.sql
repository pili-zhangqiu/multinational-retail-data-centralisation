--Remove £ symbol from price column:
UPDATE dim_products 
SET product_price = TRY_PARSE(REPLACE(product_price, '£', '') AS NUMERIC(10,2))

--Add weight class column:
ALTER TABLE dim_products 
ADD COLUMN weight_class VARCHAR(255);
SET weight_class = 
    CASE 
        WHEN weight_in_kg < 2 THEN 'Light'
        WHEN weight_in_kg >= 2 AND weight_in_kg < 40 THEN 'Mid_Sized'
        WHEN weight_in_kg >= 40 AND weight_in_kg < 140 THEN 'Heavy'
        WHEN weight_in_kg >= 140 THEN 'Truck_Required'
    END;

--Cast column datatypes:
