# /home/irisowner/.local/bin/streamlit run /src/Sample/app.py --server.port 8080 --logger.level=debug
#
import streamlit as st
from openai import OpenAI
import tryiris
import json

st.set_page_config(page_title="超簡単AIチャット")
st.title("超簡単AIチャット（Streamlit）")

client = OpenAI()  # 環境変数 OPENAI_API_KEY を利用

#3回に1度の要約作成用プロンプト生成関数
def build_transcript(messages):
    """モデル用messagesから、人間可読なテキストに整形（user/assistantのみ）"""
    lines = []
    for m in messages:
        if m["role"] in ("user", "assistant"):
            who = "User" if m["role"] == "user" else "Assistant"
            lines.append(f"{who}: {m['content']}")
    return "\n".join(lines)


if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0  # ユーザ→アシスタントの往復数

if "summary" not in st.session_state:
    st.session_state.summary = ""  # ランニングサマリ（空で開始）

# 会話履歴（継続会話の肝）
if "messages_model" not in st.session_state:
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

# 画面に「表示用ログ」を描画（ここは messages_view だけを見る）
if "messages_view" not in st.session_state:
    st.session_state.messages_view=[]

for m in st.session_state.messages_view:
    if m["role"] in ("user", "assistant"):
        with st.chat_message(m["role"]):
            st.markdown(m["content"])


# 入力欄
if prompt := st.chat_input("メッセージを入力..."):
    # 1) まず表示用に積む（画面はこれだけ見続ける）
    st.session_state.messages_view.append({"role": "user", "content": prompt})

    # 2) モデル用にも積む
    st.session_state.messages_model.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    #IRISにベクトル検索
    vresult=tryiris.search(prompt)

    with st.expander("🔍 ベクトル検索の結果：デバッグ"):
        st.write(vresult)
    if not vresult:
        # 見つからないときのフォールバック
        st.warning("ベクトル検索で関連ドキュメントが見つかりませんでした。")
        sourcetext = ""
    
    sourcetext=""
    for item in vresult:
        sourcetext+="title="+ item["Title"]+ ",info=" +item["Doc"]+ ", sourcefile="+ item["Source"] +"\n"
    
    st.session_state.messages_model.append(
        {"role":"system","content":f"sourcetext: {sourcetext}"}
    )
    #print(sourcetext)
    
    # 応答生成
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.messages_model
    )
    answer = resp.choices[0].message.content

    # 3) 表示用にも応答を積む
    st.session_state.messages_view.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)
    
    # 4) モデル用にも応答を積む（この後サマリで圧縮する可能性がある）
    st.session_state.messages_model.append({"role": "assistant", "content": answer})

    # 往復カウント（ユーザ→アシスタントで+1）
    st.session_state.turn_count += 1

    print(f"モデルに渡した内容{st.session_state.messages_model}")
    print(st.session_state.turn_count)


    # === サマリ圧縮 ===
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


# 履歴の保存/読込/データベース保存

col1, col2,col3 = st.columns(3)
#history="/opt/src/history.json"

with col1:
    if st.button("会話履歴を消去"):
        #モデル用は再セット
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
        #表示用も消去したくない場合は以下1行コメント化します。
        st.session_state.messages_view=[]
        st.rerun()

with col2:
    if st.button("データベースから履歴読込"):
        retjson=tryiris.jsonFromDB()
        if not retjson:
            st.warning("会話ログが見つかりませんでした。")
        else:
            st.session_state.messages_model = []  # 置き換えたいなら初期化
            for conv in retjson:
                # [{},{}]の仕組みでデータが入っているかの確認。入っていたら messeges_modelとmesseges_viewに追加
                if isinstance(conv, list) and all(isinstance(m, dict) for m in conv):
                    st.session_state.messages_model.extend(conv)
                    st.session_state.messages_view.extend(conv)
                else:
                    st.error("DBからのデータ形式が想定外でした（List[Dict]ではありません）。")
                    break

            # --- サマリの抽出（後ろから最初に見つかった SummaryHistory を採用）---
            def extract_summary_from_messages(msgs):
                key = "SummaryHistory:"
                for m in reversed(msgs):
                    if m.get("role") == "system":
                        content = m.get("content", "")
                        pos = content.find(key)
                        if pos != -1:
                            return content[pos + len(key):].strip()
                return None

            # もしユーザーの発話がまだ無ければ、直近サマリを「過去の問い合わせ要約」として1行表示
            has_user_utterance = any(m.get("role") == "user" for m in st.session_state.messages_view)
            if not has_user_utterance:
                latestsummary = extract_summary_from_messages(st.session_state.messages_model)
                if latestsummary:
                    st.session_state.messages_view.append({
                        "role": "user",
                        "content": f"【過去の問い合わせ要約】\n\n{latestsummary}"
                    })
                else:
                    st.info("過去サマリ（SummaryHistory:）は見つかりませんでした。")                
            st.rerun()

with col3:
    if st.button("データベースに履歴保存"):
        tryiris.jsonToDB(json.dumps(st.session_state.messages_model,ensure_ascii=False))

