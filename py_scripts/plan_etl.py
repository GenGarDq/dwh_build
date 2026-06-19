import pandas as pd
from sqlalchemy import create_engine


filepath = './files/план 02 2026.xlsx'
sheetname = 'план 02 2026'
engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost:5432/postgres')


def plan_transform(filepath, sheetname):
    df = pd.read_excel(
        filepath,
        sheet_name=sheetname,
        header=1,
        skipfooter=1
        )
    df = df.loc[:, (df.ne(0) & df.notna()).any(axis=0)]
    df.rename(columns={
            'Учетный день':'учетный_день',
            'План на день':'план_на_день',
            'Ресторан':'заказ_в_ресторане',
            'БАНКЕТ НАШ':'банкет',
            'Банкет C&B':'банкет_c&b',
            'Агрегатор':'агрегатор_доставка',
            'Самовывоз':'самовывоз_доставка',
            'Доставка':'наша_доставка',
            'Ресторан.1':'средний_чек_на_стол',
            'Доставка.1':'средний_чек_на_доставку',
            'Ресторан.2':'средний_чек_на_гостя_ресторан',
            'Доставка.2':'средний_чек_на_гостя_доставка',
            'Банкет':'средний_чек_на_гостя_банкет'
            },
            inplace=True)
    return df

def plan_load_ods(df, engine, schema, table):
    
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
        
df = plan_transform(filepath, sheetname)
plan_load_ods(df, engine, 'ods', 'restaurant_metrics')