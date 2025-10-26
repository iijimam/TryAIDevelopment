Class FS.InstallUtils
{

ClassMethod loadsql(file As %String) As %Status
{
    //ログは入力ファイルと同じディレクトリに置く
    set logfile=##class(%File).GetDirectory(file)_"sqlload-log.txt"
    set sql="LOAD SQL FROM FILE '"_file_"' DIALECT 'IRIS'"
    set sql=sql_" LOG TO FILE '"_logfile_"' IGNORE ERRORS"
    set stmt=##class(%SQL.Statement).%New()
    set tResult = ##class(%SQL.Statement).%ExecDirect(.tStatement,sql)
    if tResult.%SQLCODE<0 {
        write "Error::",tResult.%Message,!
    }
}

/// OpenAIのEmbeddingを実行（/src/utils.pyをインポートして実行してます）
ClassMethod GetTextVec(input As %String(MAXLEN=100000)) As %String [ SqlName = GetTextVec, SqlProc ]
{
    #dim %sqlcontext As %ProcedureContext
    if $get(input)="" {
        set %sqlcontext.%Message="テキストが指定されていません"
        set %sqlcontext.%SQLCODE=-401
        return ""
    }

    //utils.pyインポート
    set sys=##class(%SYS.Python).Import("sys")
    do sys.path.append("/src")
    set utils=##class(%SYS.Python).Import("utils")
    return utils.getEmbed(input)
}

/// VECTOR型の方：ファイルにEmbeddingが入ってるファイルを使うINSERT
/// listflg : Embedingがlistの場合に1、文字の場合に0
ClassMethod loadvectorjsonl(file As %String, listflg As %Integer) [ Language = python, SqlProc ]
{
    import iris
    import irisbuiltins
    import json
    import time
    import sys

    start = time.time()  # 現在時刻（処理開始前）を取得
    try:
        with open(file, "r", encoding="utf-8") as f:
            docs = [json.loads(line) for line in f]
        
        sql="insert into FS.Document (Source,Title,Text,NumOfToken,TextVec) Values(?,?,?,?,TO_VECTOR(?,Float,1536))"
        stmt=iris.sql.prepare(sql)
        if listflg==1:
            for item in docs:
                embeddingstr=str(item["embedding"])
                #print(embeddingstr[1:-1])
                rs=stmt.execute(item["id"],item["title"],item["text"],item["n_tokens"],embeddingstr[1:-1])
        else:
            for item in docs:
                #print(item["text"])
                rs=stmt.execute(item["id"],item["title"],item["text"],item["n_tokens"],item["embedding"])

    except irisbuiltins.SQLError as ex:
        print(str(repr(ex)))
        print(item["title"])
        print(ex.sqlcode)
        print(ex.message)
        print(ex.statement)
        raise
    
    end = time.time()  # 現在時刻（処理完了後）を取得
    time_diff = end - start  # 処理完了後の時刻から処理開始前の時刻を減算する
    print(f"処理時間：{time_diff}")  # 処理にかかった時間データを使用
}

/// VECTOR型の方：EmbeddingしながらINSERT
ClassMethod loadjsonl(file As %String) [ Language = python, SqlProc ]
{
    import iris
    import irisbuiltins
    import json
    import time
    import sys
    #コンテナビルド時
    sys.path+=["/opt/src"]
    
    #コンテナ開始後修正した場合
    #sys.path+=["/opt"]

    import utils

    start = time.time()  # 現在時刻（処理開始前）を取得
    try:
        with open(file, "r", encoding="utf-8") as f:
            docs = [json.loads(line) for line in f]
        
        #sql="insert into FS.Document (ChunkID,TokenCount,Text,FileName) Values(?,?,?,?)"
        sql="insert into FS.Document (FileName,DocLevel,Title,Text,TextVec) Values(?,?,?,?,TO_VECTOR(?,Float,1536))"
        stmt=iris.sql.prepare(sql)
        for item in docs:
            #print(item["text"])
            embed=utils.getEmbed(item["text"])
            rs=stmt.execute(item["source"],item["level"],item["title"],item["text"],embed)
    
    except irisbuiltins.SQLError as ex:
        print(str(repr(ex)))
        print(item["title"])
        print(ex.sqlcode)
        print(ex.message)
        print(ex.statement)
        raise
    
    end = time.time()  # 現在時刻（処理完了後）を取得
    time_diff = end - start  # 処理完了後の時刻から処理開始前の時刻を減算する
    print(f"処理時間：{time_diff}")  # 処理にかかった時間データを使用
}

/// EMBEDDING型の方（未使用）
ClassMethod loaddata(file As %String) [ Language = python, SqlProc ]
{
    import iris
    import irisbuiltins
    import json
    import time
    start = time.time()  # 現在時刻（処理開始前）を取得
    try:
        with open(file, "r", encoding="utf-8") as f:
            docs = [json.loads(line) for line in f]
        
        #sql="insert into FS.Document (ChunkID,TokenCount,Text,FileName) Values(?,?,?,?)"
        sql="insert into FS.Document (FileName,DocLevel,Title,Text) Values(?,?,?,?)"
        stmt=iris.sql.prepare(sql)
        for item in docs:
            #print(type(item["embedding"][0]))
            #embeddingstr=str(item["embedding"])
            #print(embeddingstr[1:-1])
            rs=stmt.execute(item["source"],item["level"],item["title"],item["text"])            
            #rs=stmt.execute(item["chunk_id"],item["token_count"],item["text"],item["source"])            
            #rs=stmt.execute(item["fishname"],item["text"],item["embedding"][0])
    
    except irisbuiltins.SQLError as ex:
        print(str(repr(ex)))
        print(item["title"])
        print(ex.sqlcode)
        print(ex.message)
        print(ex.statement)
        raise
    
    end = time.time()  # 現在時刻（処理完了後）を取得
    time_diff = end - start  # 処理完了後の時刻から処理開始前の時刻を減算する
    print(f"処理時間：{time_diff}")  # 処理にかかった時間データを使用
}

}
