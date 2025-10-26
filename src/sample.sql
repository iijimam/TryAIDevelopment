create table FS.MyLog (LogDT DATETIME,Content VARCHAR(100000))
go

--- ベクトル検索用テーブル
CREATE TABLE FS.Document (
    Source VARCHAR(100),
    Title VARCHAR(100),
    Text VARCHAR(100000),
    NumOfToken INTEGER,
    TextVec VECTOR(Float,1536)
)
go


--- インデックス準備
CREATE INDEX HNSWIndex ON TABLE FS.Document (TextVec)
     AS HNSW(Distance='DotProduct')
go


--- 検索実行
---select TOP 5 
--- VECTOR_DOT_PRODUCT(TextVec,TO_VECTOR(FS.GetTextVec(?),FLOAT,1536)) as sim ,Source,Title,Text
--- FROM FS.Document ORDER BY sim DESC

---select TOP 10 VECTOR_DOT_PRODUCT(TextVec,TO_VECTOR(FS.GetTextVec('産休・育休を取得する場合の申請手順を教えてください。一般的な社内の報告順も教えてください。'),FLOAT,1536)) as sim ,Source,Title,Text FROM FS.Document ORDER BY sim DESC
  

  