DROP SCHEMA core CASCADE;
CREATE SCHEMA core;
CREATE TABLE core.dim_dish_categories(
	id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	category text NOT NULL
);

CREATE TABLE core.dim_order_types(
	id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	"type" text NOT null
);

CREATE TABLE core.dim_dishes(
	id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	category_id int REFERENCES core.dim_dish_categories(id),
	dish text NOT NULL
);

CREATE TABLE core.fct_checks(
	billing_date date NOT NULL,
	check_number int NOT NULL,
	opening_time timestamp,
	closing_time timestamp,
	dish_id int REFERENCES core.dim_dishes(id),
	order_type_id int REFERENCES core.dim_order_types(id),
	dish_quantity REAL,
	guests_count SMALLINT,
	amount_with_discount numeric(10,2)
);

