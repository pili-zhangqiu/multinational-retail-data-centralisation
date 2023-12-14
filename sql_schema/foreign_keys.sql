-- Main source: orders_table
-- Add the foreign key constraints to the orders_table

ALTER TABLE orders_table
    ADD CONSTRAINT card_number_fkey FOREIGN KEY (card_number) REFERENCES dim_card_details(card_number),
    ADD CONSTRAINT date_uuid_fkey FOREIGN KEY (date_uuid) REFERENCES dim_date_times(date_uuid),
    ADD CONSTRAINT product_code_fkey FOREIGN KEY (product_code) REFERENCES dim_products(product_code),
    ADD CONSTRAINT store_code_fkey FOREIGN KEY (store_code) REFERENCES dim_store_details(store_code),
    ADD CONSTRAINT user_uuid_fkey FOREIGN KEY (user_uuid) REFERENCES dim_users(user_uuid);
