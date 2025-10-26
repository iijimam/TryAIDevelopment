# /home/irisowner/.local/bin/streamlit run /src/Phase4-final-version/app.py --server.port 8080 --logger.level=debug
import streamlit as st
from openai import OpenAI
import tryiris
import json

st.set_page_config(page_title="超簡単AIチャット")
st.title("超簡単AIチャット（Streamlit）")

client = OpenAI()  # 環境変数 OPENAI_API_KEY を利用

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

# 画面に履歴を表示
for m in st.session_state.messages_model:
    if m["role"] in ("user","assistant"):
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

# 入力欄
if prompt := st.chat_input("メッセージを入力..."):
    st.session_state.messages_model.append({"role":"user","content":prompt})
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

    # 応答生成
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.messages_model
    )
    answer = resp.choices[0].message.content
    st.session_state.messages_model.append({"role":"assistant","content":answer})

    with st.chat_message("assistant"):
        st.markdown(answer)


# 会話履歴消去／履歴読込／履歴保存/

col1, col2,col3 = st.columns(3)

with col1:
    if st.button("会話履歴を消去"):
        #モデル用は再セット
        st.session_state.messages_model = [
            {
                "role":"system",
                "content":"あなたは親切なアシスタントです。"
            }
        ]
        #表示用も消去
        #st.session_state.messages_view=[]
        st.rerun()

with col2:
    if st.button("データベースから履歴読込"):
        st.rerun()
with col3:
    if st.button("データベースに履歴保存"):
        tryiris.jsonToDB(json.dumps(st.session_state.messages_model,ensure_ascii=False))
        #st.rerun()
