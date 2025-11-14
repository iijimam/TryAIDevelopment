# 🤖はじめてのAI開発 ～ゼロからのIRIS環境構築とOpenAI連携チャットボット作り～

🐋コンテナを利用して InterSystems IRIS の環境をコマンド 1 つで立ち上げ、標準的な IDE である VSCode を使用して開発体験を味わっていただきながら、OpenAI API と連携したシンプルなチャットボットを作成します。

IRIS の環境構築からチャットボットアプリ実装まで、一緒に試しながら「AI アプリを作成できた！思ったより簡単！」を参加者の皆さんと共有しましょう！🔥

＜目次＞
- [Phase1-爆速環境構築](#phase1-爆速環境構築)
- [Phase2-IRIS データベースの基礎体験](#phase2-iris-データベースの基礎体験)
- [Phase3-ベクトル検索](#phase3-ベクトル検索)
- [Phase4-フロントエンド連携とチャットボット完成](#phase4-フロントエンド連携とチャットボット完成)

## 事前準備

以下のインストールとコンテナイメージの pull を事前に行ってください。

- VSCode
- Docker
- Docker compose
- Git（可能であれば）
- IRIS コンテナの Pull

    ```
    docker pull containers.intersystems.com/intersystems/iris-community:2025.2
    ```

<br>

準備はよろしいですか？？👀

それでは早速、はじめましょう！💨
<br><br>

## Phase1-爆速環境構築

docker compose を使用して IRIS コンテナを立ち上げ、VSCode や管理ツールからの接続を体験します。

### (1)環境構築

早速、今日の流れが含まれるリポジトリを clone または、ダウンロードしましょう。

> WSL 上に docker、docker compose、git をインストールしている場合は、WSL のターミナル上で `git clone` を行ってから以下の流れで VSCode を開くと操作が簡単です。

```
git clone xxx
```
> Zipでダウンロードした方は、展開してください。

git clone または展開したディレクトリに移動し、以下実行すると VSCode が開き本日のワークスペースが開きます。
```
code .
```
ワークショップ直下に [.env](/.env) があるので開きます。

現在
```
OPENAI_API_KEY=
```
と記載されていますが、= の右側 OpenAI の APIキー情報を追記し保存してください（二重引用符は不要です）。

次に、以下のコマンドを実行します。初回実行時のみコンテナのビルドが実行され、ビルドが終わるとコンテナを開始します。

```
docker compose up -d
```

> 事前に IRIS のコンテナイメージを pull していない場合は少し時間がかかります。

以上で、本日の環境構築完了です！

### (2) VSCode での操作

次は、VSCode を利用して IRIS に接続したり、ターミナルセッションから IRIS にログインしてみましょう！

IRIS に接続するために必要な、**ObjectScript** エクステンションをインストールします。

インストール方法の図解： [「VSCodeを使ってみよう！：1、ObjectScript用エクステンションのインストール」](https://jp.community.intersystems.com/node/482976#1)をご覧いただきながらインストールしてみましょう。

インストールが完了したら、コンテナで起動している IRIS に接続します。接続するとワークスペースで IRIS のクラス定義の作成、サーバー側コードの参照、管理ツールを起動するためのメニュー表示などが行えます。

本日の接続先情報は以下の通りです。

host|port|scheme|pathPrefix
--|--|--|--|
127.0.0.1|52773|http|指定しません

接続方法の図解： [「VSCodeを使ってみよう：2、サーバへ接続する」](https://jp.community.intersystems.com/node/482976#2)をご覧いただきながら設定してみましょう。

接続が完了すると、管理ポータルを開くためのメニューなどが図のように開くことができます。

![](/assets/VSCode-menu.jpg)

VSCode 上部に表示されるメニューの中から「Open Management Portal」をクリックし、管理ポータルを開いてみましょう。

ユーザ名、パスワードの入力画面が表示されます。ハンズオン環境では、以下のユーザ名、パスワードでログインしてください。

ユーザ名|パスワード
--|--
SuperUser|SYS

ログインが完了すると以下の画面が開きます。
![](/assets/ManagementPortal-welcome.jpg)

ハンズオンでは、管理ポータルのSQLメニューを中心に操作してきます。

管理ポータル > [システムエクスプローラ] > [SQL] 

![](/assets/ManagementPortal-sql.jpg)

なお、SQL の操作については、SQL shell でも行えます。SQL shell を開くために、IRIS にログインしてみましょう。

VSCode の「Terminal」メニューをクリックし、「New Terminal」をクリックし、コンテナにログインします。

本日のIRISのコンテナ名は、tryaidevelop です。

```
docker exec -it tryaidevelop bash
```
コンテナにログインできたら、次は IRIS にログインします（以降 IRIS にログインした端末を「**IRIS ターミナル**」と呼んでいきます）。

```
iris session iris
```

実行例は以下の通りです。
```
irisowner@0809d9d83a12:/opt/src$ iris session iris

ノード: 0809d9d83a12 インスタンス: IRIS

USER>
```

**USER>** はネームスペースのプロンプトで、IRIS の USER ネームスペースにログインしたことを表しています。

このプロンプトが表示されたらログイン成功です。

USER ネームスペースは、USER データベースに接続する定義が行われていますので、ここで SQL shell に切り替えて CREATE TABLE 文を実行すると、USER データベースにテーブル定義が保存されるようになります。

SQL shell に切り替えるには、`:s` を入力します。SQL shell を終了するときは、`quit` または　`q` を入力します。

例：
```
USER>:s
SQL Command Line Shell
----------------------------------------------------

The command prefix is currently set to: <<nothing>>.
Enter <command>, 'q' to quit, '?' for help.
[SQL]USER>>quit

USER>
```

ちなみに、コンテナログイン後、直接 IRIS の SQL shell を開くこともできます。`iris sql iris`

試される方は、一旦 IRISの接続を終了するため、`halt` または `h` を入力します。
```
USER>h
irisowner@0809d9d83a12:/opt/src$
```

直接 IRIS の SQL shell を起動する方法は以下の通りです。終了する場合は、`quit` または `q` を入力します。

実行例は以下の通りです。
```
irisowner@0809d9d83a12:/opt/src$ iris sql iris
SQL Command Line Shell
----------------------------------------------------

The command prefix is currently set to: <<nothing>>.
Enter <command>, 'q' to quit, '?' for help.
[SQL]USER>>q
irisowner@0809d9d83a12:/opt/src$ 
```

なお、コンテナをログアウトする場合は `exit` を入力してください。

### 💡 まとめ

ここまでの流れで、IRIS コンテナを開始し、VSCode の ObjectScript エクステンションを使用して、IRIS に接続を行いました。

VSCode を使用して、管理ポータルの起動や、Terminal を利用して IRIS へのログイン（IRIS ターミナルにログイン）、SQL shell の起動を確認しました。

管理ポータルやターミナルセッション、プログラミング言語から接続するときの接続先情報には、ネームスペースを指定するルールがありますので、ハンズオン環境では、**USER ネームスペース** を接続先情報として必ず指定してしましょう。

>ネームスペースとは？について詳しくは、参考動画もご参照ください：🎥 <a href="https://youtu.be/ID6ImJTgJRk?list=PLzSN_5VbNaxBPaSSINLzv-CkDJy00bOSQ&t=424" target=_blank>InterSystems IRIS で開発を始めてみよう！（7:03以降：ネームスペースとデータベースについて）</a>

## Phase2-IRIS データベースの基礎体験

テーブル定義を作成し VSCode や管理ツールからデータの参照／更新などを試します。

ハンズオンでは、🤖AI チャットボットを作成していきます。

チャット画面を閉じても、前回の会話履歴を再現できると便利ですので、会話履歴をデータベースに登録できるようにテーブルを用意してみます。

テーブル：FS.MyLog のカラム定義は以下の通りです。

カラム名|型|内容
--|--|--
LogDT|DATETIME|ログを記録した日付時刻
Content|VARCHAR(10000)|ログ記録時点の会話履歴全体

では、早速テーブル定義を作成しましょう！

DDL 文の実行は、管理ポータルのSQL画面からでも、IRIS ターミナルを SQL Shell に切り替えて実行でも、どちらでもかまいません。

> SQL Shell は起動後、複数行の実行モードではありませんので、1度 Enter 入力すると便利です。実行命令には、go を入力してください。

実行する文章は以下の通りです。

```
create table FS.MyLog (LogDT DATETIME,Content VARCHAR(100000))
```
実行後、試しにデータを登録してみましょう！

```
insert into FS.MyLog (LogDT,Content) VALUES('2025-10-31 12:10:05','今日は何の日？')
```
表示してみましょう。
```
select * from FS.MyLog
``` 

後でチャットボットからの会話履歴を登録したいので、一旦データをクリアしたい方は、truncate table を実行してください。

```
truncate table FS.MyLog
```
### 💡まとめ

ここまでの流れで、IRIS の管理ポータルや SQL shell を使ってテーブル定義を作成し、データ登録、参照が行えることを確認し、一般的な RDB 製品と同じように SQL の操作ができること確認できました

次はいよいよ、ベクトル検索のための準備を行っていきます！

> VSCode の SQLTools エクステンションを利用しても操作できます。詳しくは[「VSCode：SQLTools で IRIS に接続する方法」](https://jp.community.intersystems.com/node/489316)をご参照ください。

## Phase3-ベクトル検索

社内文書を使った生成 AI 活用を目指し、サンプル文章をベクトル化したものを IRIS に格納します。

### (1) ハンズオンのテーマ

社内の規則（人事規定）をよく知る AI チャットボットを作って以下のような質問に回答できるようにします。


- 育休をとろうと思うけど、申請の仕方や準備しないといけないものは何？

- 勤務中に階段で踏み外して足を骨折しました。治療費など会社に請求できますか？

- 介護休暇を取得する場合の申請手順を教えてください。一般的な社内の報告順も教えてください。

- パワハラを受けている人がいることを人事に伝えようと思いますが密告者を保護する規則はありますか？


生成 AI に上記質問をするともちろん回答は返りますが、一般的な回答しか返せないため、社内の人事規定に則っているのかまではわかりません。

そこで、社内の規則に沿った回答を返せるように、チャットボットに入力された質問に類似する情報を人事規定から入手し、ユーザの質問に添えて生成 AI に渡し、回答を作ってもらおうと思います。

ハンズオンで使用する人事規定は、厚生省が公開している [「モデル就業規則」](https://www.mhlw.go.jp/content/001018385.pdf) を使用します。

> 注意：モデル就業規則であるため、具体的な数値などは含まれていません。そのため、十分な補足情報にならない可能性もあります。

### (2) 前処理

生成 AI にファイルを添付して回答をしてもらうのも 1 つの手段ですが、人事規定は情報量が多いためチャット内で使用できるトークン数の制限をすぐに超えてしまう可能性が高いです。

そのため、沢山ある情報の中かから**質問に類似した情報だけを抽出**すれば、トークン数を減らすことができます。

この **「類似した情報だけを抽出する」** ためには、どうしたらいいでしょうか・・。

<br>

そうです **💡ベクトル検索です！💡**

IRIS でベクトル検索を行うためには、人事規定の中に含まれる情報からベクトルを作ってテーブルに格納しておく必要があります。

ここで問題になるのが、人事規定は非常に長い文章です。ハンズオンで使用する OpenAI の `text-embedding-3-small` の Embedding（ベクトル化）は、1536 トークンなので、PDF にある全文字列からベクトルを作ることは不可能です。

ベクトルを正しく作るためには、人事規定の文章を 1536 トークンの制限に合うように、分割していく必要がありそうです。

> 参考情報：[Tiktokenizer](https://tiktokenizer.vercel.app/) では、モデルを指定した後、確認したい文字列を入力するとトークンサイズをカウントしてくれます。gpt-4-mini は、「o200k_base」 text-embedding-3-small は、「cl100k_base」を指定します。ご参考：[Encodings](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)

次に問題になるのが、PDF からどのように文章を取り出すか、についてです。

様々な方法がありますが、今回は豊富な機能を持つ [Docling](https://github.com/docling-project/docling) の力を借りました。

> 参考情報：[ドキュメントファイルの解析と変換に特化したオープンソースツール「docling」を試してみた](https://dev.classmethod.jp/articles/converting-document-files-using-oss-tool-docling/)

Docling を使い、一旦 PDF をマークダウン形式に変換しています。

マークダウン形式でなくても単純な文字の抽出もできますが、マークダウンの良い点は、文書のタイトルや見出し情報をみつけやすい点です。また表もマークダウンで表現できるため、今回は、**マークダウン→トークンの制限未満の文字列抽出** を行っています。

> このほかにも、もっと良い方法があるかもしれません！ご存知でしたらぜひ共有お願いします！

PDF からの変換処理ですが、操作される機材によって処理速度がかなり違うため（Macだと数十秒、購入から 3 年経過の Windwos や Google Colab だと 20 分、など様々です。）ハンズオンでは、PDF からマークダウン、マークダウンからテーブル格納に必要な情報に変換したファイル（Embedding付き）を使用することにします。

ファイル名|ファイルの形式|ご参考：変換に使ったプログラム
--|--|--|
[mhlw_full_caption_only.md](/data/mhlw_full_caption_only.md)|マークダウン|pdfmarkdown.py
[mhlw_hr_rules_chunk_embeddings.jsonl](/data/mhlw_hr_rules_chunk_embeddings.jsonlmhlw_hr_rules_chunk_embeddings.jsonl) <br> ※このファイルの中身をベクトル検索で使用するテーブルに格納します|JSON|markdownToChunk.py

### (3) ベクトル検索用テーブル作成

[mhlw_hr_rules_chunk_embeddings.jsonl](/data/mhlw_hr_rules_chunk_embeddings.jsonlmhlw_hr_rules_chunk_embeddings.jsonl) の中の情報をテーブルに登録します。

JSON の中身は以下の通りです。
```
{"id": "mhlw-hr-00001", "title": "モデル就業規則", "text": "令和５年７月版厚生労働省労働基準局監督課", "n_tokens": 30, "embedding": [-0.020464539527893066, 0.05013052746653557,　-- 省略]}
```

"text" の中身の Embedding が "embedding" に設定されています。

"embedding" はベクトルで、OpenAIの `text-embedding-3-small` の Embedding（ベクトル化）は、1536 次元なので、VECTOR 型を利用して、以下のようにテーブルを作成します。
```
CREATE TABLE FS.Document (
    Source VARCHAR(100),
    Title VARCHAR(100),
    Text VARCHAR(100000),
    NumOfToken INTEGER,
    TextVec VECTOR(Float,1536)
)
```

テーブル定義をよく見ると、ベクトル用の VECTOR 型以外の通常の型（VARCHARやINTEGER）を使用する列も含まれています。

例えば、ある値でフィルタリングした後、ベクトル検索で類似するものを取得したい、というような使い方に利用できます。

それでは、管理ポータルの SQL 画面、または、IRISターミナルを SQL shell に切り替えて、上記 CREATE 文を実行してください。

テーブル定義の作成が完了したら、ベクトル検索を高速に処理できるように、以下のインデックス文を実行します。

```
CREATE INDEX HNSWIndex ON TABLE FS.Document (TextVec)
     AS HNSW(Distance='DotProduct')
```

後は、[mhlw_hr_rules_chunk_embeddings.jsonl](/data/mhlw_hr_rules_chunk_embeddings.jsonl) をテーブルにインポートするだけです。

予め IRIS のクラス定義にインポート用メソッドを用意しています。（[FS.InstallUtils.cls](/src/FS/InstallUtils.cls)クラスのloadvectorjsonl() です。）

メソッドの実行は、IRIS ターミナルで行います。

`iris session iris` で IRIS ターミナルを起動し、以下実行します。
```
do ##class(FS.InstallUtils).loadvectorjsonl("/data/mhlw_hr_rules_chunk_embeddings.jsonl",1)
```
IRIS はデータベース側でプログラミングができる特徴があります。メソッドのコードは IRIS 独自の ObjectScript または Python を選択できます。

以上でベクトル検索のためのテーブルの準備が完了です。

### (4) ベクトル検索のテスト

早速、ベクトル検索で、質問内容に類似する人事規定が拾えるか確認してみます。

検索を行うためには、質問内容の文字列を Embedding する必要があります。

Embedding のためのコードは、あらかじめ用意してあり [utils.py](/src/utils.py) の getEmbed() 関数に記載しています。

質問内容を getEmbed() の引数に指定し、ベクトルを入手した後、以下 SQL を実行し、類似する人事規定を入手できるかテストします（実際の実行は後ほど行います）。

```
select TOP 5 VECTOR_DOT_PRODUCT(TextVec,TO_VECTOR(?,1536)) as sim ,Source,Title,Text
 FROM FS.Document ORDER BY sim DESC
```
> メモ：SQL 文内の ? は引数入力の置き換え文字（プレースホルダ）です。

それでは早速、Python シェルを起動します。本日は、IRIS にログインしたターミナルを Python シェルに切り替えて実験してみます。

<span style="color: green">**？？ IRIS にログインしたターミナルを Python shell に切り替える？？**</span> 

これはどういうことかと言いますと、

IRIS は、データベースなのですが、サーバ側で Python を実行できます。この Python は、「Embedded Python または埋め込み Python」と呼ばれていて、IRIS サーバ内に Python のランタイムを組み込んでいるため、ネットワークコネクションを使用せずに IRIS にあるデータにアクセスできます。

それでは早速試してみましょう！

IRIS にログインした後、Python shell に切り替えるには、`:p` を入力します。

コンテナにログインした後の状態から `iris session iris` で IRIS ターミナルを開きます。
```
iris session iris
```
Python shell に切り替えます。
```
:p
```

ここまでの画面例は以下の通りです。
```
irisowner@6eb0d94d6ff1:/opt/src$ iris session iris

ノード: 6eb0d94d6ff1 インスタンス: IRIS

USER>:p

Python 3.12.3 (main, Aug 14 2025, 17:47:21) [GCC 13.3.0] on linux
Type quit() or Ctrl-D to exit this shell.
>>> 
```

Embedding に必要な [utils.py](/src/utils.py) をインポートし、指定文字のベクトルを任意の変数に代入します。

utils.py は /src 以下に配置しています。

```
import sys
sys.path+=["/src"]
import utils
```
「育休をとろうと思うけど、申請の仕方や準備しないといけないものは何？」　のベクトルを作成します。

```
embedding=utils.getEmbed("育休をとろうと思うけど、申請の仕方や準備しないといけないものは何？")
```

続いて、SQL を実行します。Embedded Python 内で IRIS の操作をするには、`import iris` を行います。

```
import iris
```
実行する SQL 文を変数に設定します。

> 引数には置き換え文字（プレースホルダー）の ? を指定できます。

```
sql="""
    select TOP 5 VECTOR_DOT_PRODUCT(TextVec,TO_VECTOR(?,FLOAT,1536)) as sim ,Source,Title,Text
    FROM FS.Document ORDER BY sim DESC
    """
```

💡解説：**VECTOR_DOT_PRODUCT(TextVec,TO_VECTOR(?,FLOAT,1536))** の意味

VECTOR_DOT_PRODUCT()関数は、ベクトルのドット積を求める関数です。

> OpenAI の [Embeddings のドキュメント](https://platform.openai.com/docs/guides/embeddings)より、「Embeddingの長さは1に正規化されている」とあるので、ベクトルのドット積を求める関数を利用しています。

SQL を実行します。dataframe() 関数を使って結果を確認してみます。

SQL の実行は、`iris.sql.exec(SQL文)`、または `statement=iris.sql.prepare(SQL文)` ＋ `statement.execute(引数)` で実行できます。

引数があるので、`iris.sql.prepare()` で実行してみます。

```
statement=iris.sql.prepare(sql)
result=statement.execute(embedding).dataframe()
result
```
```
for text in result["text"]:
    print(text)
```

どうでしょうか。類似する文章が返ってきたでしょうか？👀


### 💡まとめ

IRIS には、VECTOR 型の用意があるので、Embedding した情報をテーブルに格納でき、いつもの SQL でベクトル検索が行えます。

Embedding については、ハンズオンでは OpenAI モデルを利用しましたが、ローカルで実行できる他のモデルを利用することももちろんできます。

ぜひ、いろいろなモデルでの Embedding もお試しください！

## Phase4-フロントエンド連携とチャットボット完成

ここからは、フロントエンドを開発します。

ハンズオンでは、チャットボットの作成に便利な Streamlit を使っていきます。

> Streamlit は、Python で Web アプリケーションを簡単に作成できるフレームワークです。

### その1：簡単 AI チャットボットを動かそう！

以下のチャットボットを作っていきます（ソースコードは後ほど開きます）。

![](/assets/1-AIchat.jpg)

では実際に動かして、OpenAI に質問してみましょう！

コンテナにログインしているターミナルがあれば、それを使います。ログインしていない場合は、コンテナにログインします。
```
docker exec -it tryaidevelop bash
```
アプリを起動します（デバッグモードで起動してます）。
```
/home/irisowner/.local/bin/streamlit run /src/Phase4/app.py --server.port 8080 --logger.level=debug
```
コンテナ内の 8080 ポートでアプリが起動しています。ホスト側では 8080 を 9090 に割り当てていますので、以下URLでアプリを起動してください。

http://localhost:9090

> ※ 「会話履歴を消去」以外のボタンは具体的な処理を記述していないため動きません。

どうでしょうか。ちゃんとチャットボットとして機能してますか？

それでは、コードを開いて中身を確認します。

コード：[Phase4/app.py](/src/Phase4/app.py)

「会話履歴を消去」のボタンの動きは、56行目以降に記載しています。

このボタンを押すまでは、会話の履歴を `st.session_state.messages_model` に追記し続けています。

このボタンをクリックすると、初期のプロンプトが設定されます。

```
        st.session_state.messages_model = [
            {
                "role":"system",
                "content":"あなたは親切なアシスタントです。"
            }
        ]
```

### その2：会話履歴をデータベースの保存してみよう！

コード：[Phase4/app.py](/src/Phase4/app.py) の72行目以降にある未実装のボタン「データベースに履歴保存」に処理を追記してみます。

画面を消去するまで、会話の履歴は全て `st.session_state.messages_model` に保存しています。

「データベースに履歴保存」をクリックした場合、`st.session_state.messages_model` に保存された dictionary を JSON文字列に変更し IRIS に用意した FS.MyLog に登録してみます。

登録した日付時刻がわかると嬉しいので、ボタンクリック時の日付時刻を取得し、INSERT してみます。

#### (1) IRIS への接続

ハンズオンでは、[sqlalchemy-iris](https://pypi.org/project/sqlalchemy-iris/) を利用して IRIS への接続オブジェクトを作り INSERT を実行します。

> コンテナ開始時にパッケージをインストールしています。

接続オブジェクト作成まで流れは以下の通りです。

```
from sqlalchemy import create_engine,text
engine = create_engine("iris://SuperUser:SYS@localhost:1972/USER")
conn=engine.connect()
```

後で実装するベクトル検索に必要な [utils.py](/src/utils.py) をインポートするため以下記載します。
```
import sys
sys.path+=["/src"]
import utils
```

#### (2) INSERT 文の組み立て
この後実行する SQL文 は [Phase2-IRIS データベースの基礎体験](#phase2-iris-データベースの基礎体験) で実行した FS.MyLog への INSERT 文です。

```
insert into FS.MyLog (LogDT,Content) (現在の日付時刻,会話履歴のJSON)
```
現在の日付時刻を DATETIME 形式で取得する必要があるのでその準備をします。

```
import datetime
today=datetime.datetime.today()
formatted_dt = today.strftime('%Y-%m-%d %H:%M:%S')
```

後は会話履歴のJSONを渡せばログへの INSERT は完成です。

この後もデータベースへに対する処理を追加したいので、**[Phase4/tryiris.py](/src/Phase4/tryiris.py)** にコードを追記します（現在ファイルの中身は空です）。

コード例は以下の通りです。

例）tryiris.py に jsonToDB(input) 関数を用意した例
```
from sqlalchemy import create_engine,text
import datetime
import sys
sys.path+=["/src"]
import utils

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
```

#### (3) app.py に作成したスクリプトファイルをインポートして関数を実行する

[Phase4/app.py](/src/Phase4/app.py)  に (2) の手順で追加した Python スクリプトファイルをインポートします。

インポート後、作成した関数を「データベースに履歴保存」ボタンをクリックしたときに処理として追加し、データベースに保存できるかどうか確認します。

作成した関数に渡す引数の情報として `st.session_state.messages_model` を使います。この中は dictionary でデータが登録されているので、json.dumps() 利用して JSON 文字を渡しています。

例）
```
# import の追加（スクリプトファイル名を tryiris とした場合の例）
import tryiris
import json
```
「データベースに履歴保存」ボタンをクリックしたときに処理追加
```
with col3:
    if st.button("データベースに履歴保存"):
        tryiris.jsonToDB(json.dumps(st.session_state.messages_model,ensure_ascii=False))
        #st.rerun()
```

ブラウザで表示していた画面をリロードし、テストしてみます。

「データベースに履歴保存」ボタンクリック後、テーブルに履歴が追記されていることを確認します。

### その3：ベクトル検索の結果を生成 AI に渡してみよう！

いよいよここからは、チャットボットに社内の人事規定の情報を追加するために IRIS のベクトル検索の処理を追加していきます！

流れは以下の通りです。

- ユーザーがチャットボットに質問入力

- 入力文字列に類似する人事規定の文書を拾うため、ベクトル検索を実施（上位 3 件のみ利用）

- OpenAI に送るプロンプトにベクトル検索の結果を追加する。


#### (1) ベクトル検索用関数を用意する

追加したスクリプトファイルに（例では tryiris.py）にベクトル検索を実行する関数を用意します。

実行に使う SQL は、[(4) ベクトル検索のテスト](#4-ベクトル検索のテスト) の流れで利用した以下 SELECT 文です。

```
select TOP 5 VECTOR_DOT_PRODUCT(TextVec,TO_VECTOR(?,FLOAT,1536)) as sim ,Source,Title,Text
 FROM FS.Document ORDER BY sim DESC
```

? の部分を :text に、TOP 5 を 3 に変更し、上記 SQL を実行する関数を用意します。

入力引数は、チャットボットに入力された質問です。

例）
```
def search(input):
    embed=utils.getEmbed(input)
    sql=(
     "select TOP 3 VECTOR_DOT_PRODUCT(TextVec,TO_VECTOR(:embed,FLOAT,1536)) as sim ,Source,Title,Text"
     " FROM FS.Document ORDER BY sim DESC"
    )
    rset = conn.execute(text(sql), {'embed': embed}).fetchall()
    docref=[]
    for reco in rset:
        docref.append(
            {"Source":reco[1],"Title":reco[2],"Doc":reco[3]}
        )
    return docref
```

#### (2) app.py にベクトル検索の呼び出しを追加する

ユーザーからの入力を行ったときに動く以下の処理の下に

```
if prompt := st.chat_input("メッセージを入力..."):
    st.session_state.messages_model.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
```
ベクトル検索の呼び出しを行う以下の関数実行を追加します。

```
    #IRISにベクトル検索
    vresult=tryiris.search(prompt)

    with st.expander("🔍 ベクトル検索の結果：デバッグ"):
        st.write(vresult)
    if not vresult:
        # 見つからないときのフォールバック
        st.warning("ベクトル検索で関連ドキュメントが見つかりませんでした。")
        sourceinfo = ""
        sourcetext = ""
    
    # ベクトル検索の結果を変数に設定
    sourcetext=""
    for item in vresult:
        sourcetext+="title="+ item["Title"]+ ",info=" +item["Doc"]+ ", sourcefile="+ item["Source"] +"\n"
    
    st.session_state.messages_model.append(
        {"role":"system","content":f"sourcetext: {sourcetext}"}
    )
```

#### (3) システムプロンプトを追加する

現時点のシステムプロンプトは、
```
{"role":"system","content":"あなたは親切なアシスタントです。"}
```
なので、せっかくベクトル検索の結果をプロンプトに追加しても、使い方を説明していないため生成 AI が補足情報として認識しない可能性が高いです。

システムプロンプトに、ベクトル検索結果を加味した結果を返すように以下のように修正します。

現在以下のように指示しています（app.py）。
```
# 会話履歴（継続会話の肝）
if "messages_model" not in st.session_state:
    st.session_state.messages_model = [
        {"role":"system","content":"あなたは親切なアシスタントです。"}
    ]
```
`st.session_state.messages_model=`　のリストの中身を以下のように修正してください。

```
    st.session_state.messages_model = [
        {
            "role":"system",
            "content":"""
                あなたは親切なアシスタントです。
                ユーザの質問に類似する社内情報をsourcetext以下に記載します。
                ユーザが希望する内容を社内情報sourcetextの記載に沿って回答してください。
                回答のサマリも作成してください。社内文書のどの情報を使用したかtitleの内容を含めてください。
            """.strip()
        }
    ]
```
メモ：変数 sourcetext は、ベクトル検索で取得した質問に類似する文章を保存している変数です。

app.py を保存しチャットボットからの回答が人事規定の情報を含めた回答が返ってくるかテストします。

今回はシステムプロンプトを変更したので、一度アプリケーションを停止してから再度起動してからテストしてみましょう。

**方法：** app.py を実行しているウィンドウで Ctrl+C を押して停止した後、再度 app.py を実行します。

```
/home/irisowner/.local/bin/streamlit run /src/Phase4/app.py --server.port 8080 --logger.level=debug
```


💡ベクトル検索結果をデバッグとして画面に表示ています。取得できた人事規定のタイトルが回答の中に含まれているか確認してみましょう！

文言例）

- 育休をとろうと思うけど、申請の仕方や準備しないといけないものは何？

- 勤務中に階段で踏み外して足を骨折しました。治療費など会社に請求できますか？

- 介護休暇を取得する場合の申請手順を教えてください。一般的な社内の報告順も教えてください。

- パワハラを受けている人がいることを人事に伝えようと思いますが密告者を保護する規則はありますか？


### 💡 まとめ

ここまでの流れで、以下の事を確認できました。

- Streamlit を使って簡単にできるチャットボットが作成できること
- IRIS のベクトル検索を利用することで、社内文書の類似する文章を抽出できること
- チャットボットで設定しているシステムプロンプトにベクトル検索の結果を追加し、生成 AI に送ることで、一般的な回答ではなく、社内の人事規定に沿った回答を生成 AI から取得できること

<br>
🤖チャットボットは完成しましたが、実はまだ改良できるところがあります。

- A：会話履歴を全て保持し、次のプロンプトに送っているため、会話履歴が多くなるとプロンプトが多くなる＝いつかトークン制限を超えてしまうかもしれない。

- B：会話履歴を消去しても、画面を消去していない間は履歴を表示しておきたい（今は会話履歴消去で画面表示も一緒に消えてしまいます）


A については、例えば、3回のやり取りを迎えたところで、今までの会話履歴の要約を生成 AI に作らせてプロンプトに保持させておくとトークン数を抑えつつも過去の会話概要を生成 AI に伝えることができます。


B については、Streamlit の session_state に画面表示用の情報をセットするように追加し、会話履歴消去の時はプロンプト用の履歴だけを消去するように変更することでよりユーザーフレンドリーな画面を作成できます。

具体的なコード例は、[Sample](/src/Sample/) 以下に用意があります。ぜひご参照ください。

A の処理追加例

`if prompt := st.chat_input("メッセージを入力..."):` のタイミングで以下追記

```
    # 往復カウント（ユーザ→アシスタントで+1）
    st.session_state.turn_count += 1

    # 例：3往復ごとに圧縮
    if st.session_state.turn_count % 3 == 0:
        previous = st.session_state.summary or "(none)"
        new_dialogue = build_transcript(st.session_state.messages_model)

        #記録してたメッセージを初期化
        st.session_state.messages_model=[]

        summaryprompt=f"""
            これまでの要約は History:以降にあります。新たな依頼はNewDialogue:以下にあります。
            1) これまでの要約と新たな依頼を1つの更新された要約に300から500文字で作成します。
            2) 新たな依頼と矛盾しない限り、これまでの要約の重要な事実をすべて引き継いでください。
            3) 矛盾がある場合は、新しい情報を優先します。
            4) 関連性がある場合、引用されたタイトル/セクション（例：規程名・条番号）はそのまま使用します。
            5) 概要テキストのみを出力します。見出しやラベルは含めません。

            History: {previous}

            NewDialogue:{new_dialogue}        
            """.strip()

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": summaryprompt}]
        )
        summary_answer = resp.choices[0].message.content
        st.session_state.summary = summary_answer
        #プロンプト再設定
        st.session_state.messages_model = [
            {
            "role":"system",
            "content":f"""
                あなたは親切なアシスタントです。ユーザの質問に類似する社内情報をsourcetext以下に記載します。
                ユーザが希望する内容を社内情報sourcetextの記載に沿って回答してください。
                回答のサマリも作成してください。社内文書のどの情報を使用したかtitleの内容を含めてください。
                過去の会話の要約は、SummaryHistory以降にあります。
                SummaryHistory: {st.session_state.summary}
                """.strip()
            }
        ]
        print(f"要約後のモデルへのメッセージ：{st.session_state.messages_model}")

```

ぜひ、いろいろお試しください！

お疲れ様でした！🤖