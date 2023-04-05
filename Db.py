import mysql.connector as mysql
import pandas as pd

def connect_db():
    try:
        conn = mysql.connect(
            host="103.200.29.1",
            user="root",
            passwd="qwe10086",  # 换成你的 MySQL 密码
            database="mydatabase"  # 换成你的数据库名
        )
        return conn
    except Exception as e:
        print(e)
    return None

def read_data():
    conn = connect_db()
    cursor = conn.cursor()
    query = "select * from tasks"
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=[i[0] for i in cursor.description])
    return df

def save_data(df):
    conn = connect_db()
    cursor = conn.cursor()
    for index, row in df.iterrows():
        query = "UPDATE tasks SET id='{}', name='{}', param='{}',paramtype='{}',referparam='{}'" \
                ",diff='{}',difftype='{}',fixvalue='{}' where id='{}'"
        query = query.format(row.id, row.name, row.param,row.paramtype,row.referparam,row['diff'],row.difftype,row.fixvalue,row.id)
        print(query)
        cursor.execute(query)
        conn.commit()

if __name__ == '__main__':
    print(read_data())
