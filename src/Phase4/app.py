# /home/irisowner/.local/bin/streamlit run /src/Phase4/app.py --server.port 8080 --logger.level=debug
import streamlit as st
from openai import OpenAI

##--- ここにインポートを追加 --##


##---------------------------##

st.set_page_config(page_title="超簡単AIチャット")
st.title("超簡単AIチャット（Streamlit）")

client = OpenAI()  # 環境変数 OPENAI_API_KEY を利用

# 会話履歴（継続会話の肝）
if "messages_model" not in st.session_state:
    st.session_state.messages_model = [
        {"role":"system","content":"あなたは親切なアシスタントです。"}
    ]
    ##-- ベクトル検索結果の内容を含めるプロンプトに変更する --##

    ##----------------------------------------------------##

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

    ##--- ここに関数の呼び出しを追加 --##

    ##-------------------------------##

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
        ##--- ここに関数の呼び出しを追加 --##

        ##-------------------------------##
        st.rerun()
