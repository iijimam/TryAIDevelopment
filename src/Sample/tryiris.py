from sqlalchemy import create_engine,text
import datetime
import json

engine = None
conn = None

def initial():
    global engine, conn
    engine = create_engine("iris://SuperUser:SYS@localhost:1972/USER",echo=True)
    if engine is None:
        engine = create_engine("iris://SuperUser:SYS@localhost:1972/USER", echo=True, future=True)
    if conn is None:
        conn = engine.connect()


#インポート時に初期化
initial()


#-----------------
#会話履歴を保存する
#2回に1度過去の会話履歴の要約を作っているので依頼時の全情報を1レコードに保存する
#input : プロンプトで渡してるJSON文字が来る
def jsonToDB(input):
    print(input)
    today=datetime.datetime.today()
    formatted_dt = today.strftime('%Y-%m-%d %H:%M:%S')
    sql="insert into FS.MyLog (LogDT,Content) values(:logdate,:content)"
    para={"logdate":formatted_dt,"content":input}
    conn.execute(text(sql),para)
    conn.commit()

def jsonFromDB():
    sql=(
     "select top 4 Content FROM FS.MyLog"
    )
    rset=conn.execute(text(sql))
    resultjson=[]
    for reco in rset:
        obj=json.loads(reco[0])
        resultjson.append(obj)

    return resultjson


def search(input):
    sql=(
     "select TOP 3 VECTOR_DOT_PRODUCT(TextVec,TO_VECTOR(FS.GetTextVec(:text),FLOAT,1536)) as sim ,Source,Title,Text"
     " FROM FS.Document ORDER BY sim DESC"
    )
    print(sql)
    rset = conn.execute(text(sql), {'text': input}).fetchall()
    docref=[]
    for reco in rset:
        #print(reco)
        docref.append(
            {"Source":reco[1],"Title":reco[2],"Doc":reco[3]}
        )
    return docref

# インポート時にだけ実行したい場合は、関数の呼び出し方を工夫する
if __name__ == "__main__":
    initial()