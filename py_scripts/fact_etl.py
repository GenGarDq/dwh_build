import pandas as pd
from sqlalchemy import create_engine


filepath_1 = './files/факт 02 2025.csv'
filepath_2 = './files/факт 02 2026.csv'
engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost:5432/postgres')

def fact_transform(*filepaths):
    result = pd.DataFrame()
    for filepath in filepaths:
        df = pd.read_csv(filepath, delimiter= ',')
        df.drop(columns=['Час открытия', 'Час закрытия'], inplace=True)
        df.rename(columns={
            'Учетный день': 'учетный_день',
            'Номер чека': 'номер_чека',
            'Время открытия': 'время_открытия',
            'Время закрытия': 'время_закрытия',
            'Блюдо': 'блюдо',
            'Категория блюда': 'категория_блюда',
            'Тип заказа': 'тип_заказа',
            'Количество блюд': 'количество_блюд',
            'Количество гостей': 'количество_гостей',
            'Сумма со скидкой, р.': 'сумма_со_скидкой'
        }, inplace=True)

        df['учетный_день'] = pd.to_datetime(df['учетный_день'], format='%m/%d/%Y')
        df['время_открытия'] = pd.to_datetime(df['время_открытия'], format='%m/%d/%y %H:%M')
        df['время_закрытия'] = pd.to_datetime(df['время_закрытия'], format='%m/%d/%y %H:%M')
        df['количество_блюд'] = df['количество_блюд'].astype('int64')
        df['количество_гостей'] = df['количество_гостей'].astype('int64')
        df['сумма_со_скидкой'] = df['сумма_со_скидкой'].astype('float64')
        df['блюдо'] = df['блюдо'].str.rstrip('+').str.strip().str.lower()
        df['категория_блюда'] = df['категория_блюда'].str.strip().str.lower()
        df['тип_заказа'] = df['тип_заказа'].str.strip().str.lower()

        result = pd.concat([result, df], ignore_index=True)
    
    bad = result.groupby(['номер_чека', 'время_закрытия'])['сумма_со_скидкой'].transform('sum')
    result = result[bad != 0]
    return result

def fact_load_ods(df, engine, schema, table):
    
    dates = df['учетный_день'].dt.strftime('%Y-%m-%d').unique()
    
    with engine.begin() as conn:
        for d in dates:
            conn.exec_driver_sql(
                f"DELETE FROM {schema}.{table} WHERE учетный_день = %s",
                (d,)
            )
            
    with engine.connect() as conn:
        df.to_sql(name=table,
                con=conn,
                schema=schema,
                if_exists='append', 
                index=False)


df = fact_transform(filepath_1, filepath_2)
fact_load_ods(df, engine, 'ods', 'fct_checks')