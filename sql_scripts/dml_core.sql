INSERT INTO core.dim_dish_categories (category)
SELECT DISTINCT категория_блюда 
FROM ods.fct_checks
WHERE категория_блюда NOT IN (SELECT category FROM core.dim_dish_categories);

INSERT INTO core.dim_order_types ("type")
SELECT DISTINCT тип_заказа 
FROM ods.fct_checks
WHERE тип_заказа NOT IN (SELECT "type" FROM core.dim_order_types);

INSERT INTO core.dim_dishes (category_id, dish)
SELECT DISTINCT c.id, o.блюдо
FROM ods.fct_checks o
JOIN core.dim_dish_categories c ON o.категория_блюда = c.category
WHERE o.блюдо NOT IN (SELECT dish FROM core.dim_dishes);

INSERT INTO core.fct_checks (
    billing_date, check_number, opening_time, closing_time,
    dish_id, order_type_id, dish_quantity, guests_count, amount_with_discount
)
SELECT 
    o.учетный_день,
    o.номер_чека,
    o.время_открытия,
    o.время_закрытия,
    d.id,
    ot.id,
    o.количество_блюд,
    o.количество_гостей,
    o.сумма_со_скидкой
FROM ods.fct_checks o
JOIN core.dim_dishes d ON o.блюдо = d.dish
JOIN core.dim_dish_categories dc ON d.category_id = dc.id AND o.категория_блюда = dc.category
JOIN core.dim_order_types ot ON o.тип_заказа = ot."type";