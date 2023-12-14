--Cast column datatypes:
ALTER TABLE dim_card_details

ALTER COLUMN card_number TYPE varchar(19),
ALTER COLUMN expiry_date TYPE date,
ALTER COLUMN date_payment_confirmed TYPE date;
