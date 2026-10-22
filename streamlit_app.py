import streamlit as st
import random
import sqlite3

# --- SQLite3 データベースの初期化 ---
def init_db():
    conn = sqlite3.connect("recipe.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_name TEXT,
            ingredients TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="大学生のズボラ飯献立ナビ", page_icon="🍳")
st.title("🍳 大学生のズボラ飯献立ナビ + 保存機能")
st.write("冷蔵庫にあるものを入力してね。気に入ったレシピはデータベースに保存できるよ！")

recipe_db = [
    {"name": "爆速！親子丼風レンジ蒸し", "main": ["鶏肉", "卵"], "desc": "鶏肉と麺つゆをレンジでチン。最後に溶き卵を入れてさらに30秒！"},
    {"name": "キャベツと卵のズボラ炒め", "main": ["キャベツ", "卵"], "desc": "キャベツをちぎって炒め、卵を投入。マヨネーズで味付け。"},
    {"name": "鶏肉のポン酢さっぱり煮", "main": ["鶏肉"], "desc": "鶏肉を焼いてポン酢と砂糖少々で煮詰めるだけ。"},
    {"name": "無限キャベツ", "main": ["キャベツ"], "desc": "ちぎったキャベツにツナ缶、ごま油、鶏ガラを混ぜる。"},
    {"name": "たまごかけご飯（豪華版）", "main": ["卵"], "desc": "TKGに、ごま油と醤油、天かすをのせる。"},
    {"name": "鶏肉とキャベツのレンジ蒸し", "main": ["鶏肉", "キャベツ"], "desc": "キャベツの上に鶏肉をのせ、酒と塩を振りレンジで5分。"}
]

if "display_recipes" not in st.session_state:
    st.session_state.display_recipes = []

tab1, tab2 = st.tabs(["🔍 レシピ検索", "⭐ お気に入り一覧"])

with tab1:
    ingredients = st.text_input("冷蔵庫にある食材（例：卵, 鶏肉, キャベツ）", "")
    
    if st.button("献立を提案してもらう"):
        if ingredients:
            user_ingredients = [i.strip() for i in ingredients.replace("、", ",").split(",")]
            found_recipes = []
            
            for recipe in recipe_db:
                if any(item in user_ingredients for item in recipe["main"]):
                    found_recipes.append(recipe)
            
            if found_recipes:
                st.session_state.display_recipes = random.sample(found_recipes, min(len(found_recipes), 3))
            else:
                st.session_state.display_recipes = []
                st.warning("その食材に合うレシピが見つからない...適当に炒めちゃおう！")
        else:
            st.error("食材を入力してね。")

    if st.session_state.display_recipes:
        st.subheader("今日のご飯はこれだ！")
        for r in st.session_state.display_recipes:
            with st.container():
                st.markdown(f"### ✨ {r['name']}")
                st.write(f"**作り方:** {r['desc']}")
                
                if st.button("お気に入りに保存", key=f"save_{r['name']}"):
                    try:
                        conn = sqlite3.connect("recipe.db")
                        c = conn.cursor()
                        c.execute("INSERT INTO favorites (recipe_name, ingredients) VALUES (?, ?)", (r['name'], ", ".join(r['main'])))
                        conn.commit()
                        conn.close()
                        st.success(f"「{r['name']}」を保存しました！タブを切り替えて見てみてね。")
                    except Exception as e:
                        st.error(f"保存に失敗しました...: {e}")
                st.divider()

with tab2:
    st.subheader("保存したお気に入りレシピ")
    
    if st.button("リストを更新"):
        pass 
    
    try:
        conn = sqlite3.connect("recipe.db")
        c = conn.cursor()
        
        # --- 👇 課題用に ORDER BY id DESC を追加 👇 ---
        c.execute("SELECT * FROM favorites ORDER BY id DESC")
        
        rows = c.fetchall()
        conn.close()
        
        if rows:
            for row in rows:
                st.info(f"**{row[1]}** （主な食材: {row[2]}）")
        else:
            st.write("まだ保存されたレシピはありません。")
            
    except Exception as e:
        st.error(f"データの読み込みに失敗しました: {e}")
