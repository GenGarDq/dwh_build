DROP SCHEMA ods CASCADE;
CREATE SCHEMA ods;

CREATE TABLE ods.fct_checks(
    учетный_день date,
    номер_чека int,
    время_открытия timestamp,
    время_закрытия timestamp,
    блюдо text,
    категория_блюда text,
    тип_заказа text,
    количество_блюд real,
    количество_гостей int,
    сумма_со_скидкой NUMERIC
);

COMMENT ON COLUMN ods.fct_checks.сумма_со_скидкой IS 'Сумма указана в рублях (RUB)';


CREATE TABLE ods.restaurant_metrics (
    учетный_день DATE,
    план_на_день NUMERIC(20, 2),
    заказ_в_ресторане NUMERIC(20, 2),
    банкет NUMERIC(20, 2),
    "банкет_c&b" NUMERIC(20, 2),
    агрегатор_доставка NUMERIC(20, 2),
    самовывоз_доставка NUMERIC(20, 2),
    наша_доставка NUMERIC(20, 2),
    средний_чек_на_стол NUMERIC(20, 2),
    средний_чек_на_доставку NUMERIC(20, 2),
    средний_чек_на_гостя_ресторан NUMERIC(20, 2),
    средний_чек_на_гостя_доставка NUMERIC(20, 2),
    средний_чек_на_гостя_банкет NUMERIC(20, 2)
);

COMMENT ON TABLE ods.restaurant_metrics IS 'Метрики ресторана по дням';