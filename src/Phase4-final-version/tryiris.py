from sqlalchemy import create_engine,text
import datetime

from sqlalchemy import create_engine,text
engine = create_engine("iris://SuperUser:SYS@localhost:1972/USER")
conn=engine.connect()

#----------------
#会話履歴を保存する
#input : プロンプトで渡してるJSON文字が来る
#----------------
def jsonToDB(input):
    today=datetime.datetime.today()
    formatted_dt = today.strftime('%Y-%m-%d %H:%M:%S')
    sql="insert into FS.MyLog (LogDT,Content) values(:logdate,:content)"
    para={"logdate":formatted_dt,"content":input}
    conn.execute(text(sql),para)
    conn.commit()

#---------------
# ベクトル検索用関数
# input : チャットボットのユーザーが入力した質問
#---------------
def search(input):
    sql=(
     "select TOP 3 VECTOR_DOT_PRODUCT(TextVec,TO_VECTOR(FS.GetTextVec(:text),FLOAT,1536)) as sim ,Source,Title,Text"
     " FROM FS.Document ORDER BY sim DESC"
    )
    rset = conn.execute(text(sql), {'text': input}).fetchall()
    docref=[]
    for reco in rset:
        docref.append(
            {"Source":reco[1],"Title":reco[2],"Doc":reco[3]}
        )
    return docref