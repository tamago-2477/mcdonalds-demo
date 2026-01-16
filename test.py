import streamlit as st
import time

# --- 設定とスタイル ---
st.set_page_config(page_title="マクドナルド公式風デモ", layout="centered")

# CSS: デザイン調整
st.markdown("""
    <style>
        .stApp { background-color: #ffffff; }
        h1, h2, h3, h4, h5, h6, p, div, span, label, li {
            color: #292929 !important;
            font-family: "Helvetica Neue", Arial, sans-serif;
        }
        [data-testid="stImage"] img {
            height: 180px !important;
            object-fit: contain !important;
            width: 100% !important;
            margin-bottom: 10px;
        }
        /* ボタン共通設定 */
        div.stButton > button {
            font-weight: bold !important;
            border-radius: 4px !important;
        }
        /* 通常ボタン (白) */
        div.stButton > button:first-child {
            background-color: #ffffff !important;
            color: #292929 !important;
            border: 1px solid #c0c0c0 !important;
        }
        div.stButton > button:first-child:hover {
            border-color: #dfa92f !important;
            background-color: #fff9e6 !important;
        }
        /* Primaryボタン (黄色) - カート追加用 */
        div.stButton > button[kind="primary"] {
            background-color: #ffbc0d !important;
            color: #292929 !important;
            border: none !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
            font-size: 18px !important;
            padding: 10px 0 !important;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #e0a800 !important;
        }
        
        /* トグルスイッチ */
        [data-testid="stToggle"] span {
            background-color: #e0e0e0 !important;
            border: 1px solid #888888 !important;
        }
        [data-testid="stToggle"] input:checked + span {
            background-color: #ffbc0d !important;
            border-color: #e0a800 !important;
        }
        /* ラジオボタン */
        [data-testid="stRadio"] label {
            font-weight: bold;
            font-size: 16px;
        }
        /* 警告メッセージ用 */
        .limit-alert {
            padding: 10px;
            background-color: #ffebee;
            color: #c62828;
            border: 1px solid #ef9a9a;
            border-radius: 4px;
            margin-bottom: 10px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# --- 状態管理 ---
if 'page' not in st.session_state:
    st.session_state.page = 'list'
if 'selected_item' not in st.session_state:
    st.session_state.selected_item = None
if 'cart' not in st.session_state:
    st.session_state.cart = []

# --- メニューデータ ---
MENU_DATA = {
    "バーガー": [
        {"name": "てりやきマックバーガー", "price": 400, "type": "burger", "desc": "ポークパティを、日本ならではのてりやき風味に仕上げた人気メニュー。", "img": "てりやき.png"},
        {"name": "ダブルチーズバーガー", "price": 450, "type": "burger", "desc": "クリーミーなチーズと香ばしいビーフパティを2枚も使ったおいしさ。", "img": "ダブルチーズバーガー.png"},
        {"name": "チキンフィレオ®", "price": 420, "type": "burger", "desc": "サクサクのチキンパティとオーロラソースの相性が抜群。", "img": "チキンフィレオ.png"},
        {"name": "ビッグマック®", "price": 480, "type": "burger", "desc": "おいしさも食べごたえもビッグな、マクドナルドの看板メニュー。", "img": "ビックマック.png"},
    ],
    "サイド": [
        {"name": "マックフライポテト", "price": 200, "type": "potato", "desc": "外はカリッとゴールデンブラウン。", "img": "ポテト.png"},
        {"name": "チキンナゲット 5ピース", "price": 200, "type": "side", "desc": "絶妙な温度管理で揚げられたチキン。", "img": "ナゲット.png"},
    ],
    "ハッピーセット": [
        # ★ここを修正しました
        {"name": "ハッピーセット(ハンバーガー)", "price": 520, "type": "happyset", "desc": "チーズバーガー、ポテトS、ドリンクS、おもちゃ。", "img": "ハッピーセット.png"},
    ]
}

# --- ビッグデータシミュレーション (サイドバー) ---
with st.sidebar:
    st.title("🛠️ デモ設定 (管理者)")
    st.caption("AIによるユーザー判定結果をシミュレーションします")
    
    user_status = st.radio(
        "現在のユーザー属性判定:",
        ["👪 一般の家族連れ", "🤖 転売ヤー疑い"],
        index=0
    )
    
    st.divider()
    
    if "転売" in user_status:
        st.error("⚠ 転売対策モード稼働中")
        st.write("ハッピーセット購入制限: **1個まで**")
        HAPPY_SET_LIMIT = 1
    else:
        st.success("✅ 通常モード")
        st.write("ハッピーセット購入制限: **なし**")
        HAPPY_SET_LIMIT = 99

    st.divider()
    
    st.markdown("### 🛒 カート情報")
    if st.session_state.cart:
        st.write(f"点数: {len(st.session_state.cart)}点")
        if st.button("カートを見る / 会計", use_container_width=True):
            st.session_state.page = 'cart'
            st.rerun()
    else:
        st.caption("カートは空です")

# --- 関数定義 ---

def get_happyset_count_in_cart():
    """カートの中にハッピーセットが何個あるか数える"""
    count = 0
    for item in st.session_state.cart:
        if "ハッピーセット" in item['name']:
            count += 1
    return count

def add_to_cart(item, price, options):
    order_item = {
        "name": item['name'],
        "price": price,
        "img": item['img'],
        "options": options
    }
    st.session_state.cart.append(order_item)

def show_product_list():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("##### 富岡店で受け取り") 
    with col2:
        if st.session_state.cart:
            if st.button(f"🛒 カート({len(st.session_state.cart)})", type="primary"):
                st.session_state.page = 'cart'
                st.rerun()

    tab1, tab2, tab3 = st.tabs(["🍔 バーガー", "🍟 サイド", "🎁 ハッピーセット"])

    with tab1: display_category_items(MENU_DATA["バーガー"])
    with tab2: display_category_items(MENU_DATA["サイド"])
    with tab3: display_category_items(MENU_DATA["ハッピーセット"])

def display_category_items(items):
    cols = st.columns(2)
    for i, item in enumerate(items):
        with cols[i % 2]:
            with st.container(border=True):
                st.image(item["img"], use_container_width=True)
                st.markdown(f"**{item['name']}**")
                
                price_suffix = "~" if item.get("type") == "potato" else ""
                st.markdown(f"<h4>¥{item['price']}{price_suffix}</h4>", unsafe_allow_html=True)
                
                if st.button("選 択", key=f"btn_{item['name']}", use_container_width=True):
                    st.session_state.selected_item = item
                    st.session_state.page = 'detail'
                    st.rerun()

def show_product_detail():
    item = st.session_state.selected_item
    item_type = item.get("type", "burger")
    
    if st.button("＜ メニューに戻る"):
        st.session_state.page = 'list'
        st.rerun()

    st.markdown(f"### {item['name']}")
    st.image(item["img"])
    
    # --- AI判定警告 ---
    is_happyset = (item_type == "happyset")
    current_cart_count = get_happyset_count_in_cart()
    limit_reached = False
    
    if is_happyset and HAPPY_SET_LIMIT < 10:
        st.markdown(f"""
            <div class="limit-alert">
                ⚠ 転売対策のため、ハッピーセットはお一人様{HAPPY_SET_LIMIT}個までとさせていただいております。<br>
                (現在カート内: {current_cart_count}個)
            </div>
        """, unsafe_allow_html=True)
        if current_cart_count >= HAPPY_SET_LIMIT:
            limit_reached = True

    st.write(item["desc"])
    st.divider()

    # --- カスタマイズ ---
    current_price = item['price']
    selected_size = None
    donation_note = "標準"
    is_donation = False
    
    if item_type == "potato":
        st.markdown("##### 🍟 サイズ選択")
        size_choice = st.radio("サイズ", ["Sサイズ ¥200", "Mサイズ ¥330", "Lサイズ ¥380"], index=1, horizontal=True)
        if "S" in size_choice: current_price=200; selected_size="Sサイズ"
        elif "M" in size_choice: current_price=330; selected_size="Mサイズ"
        elif "L" in size_choice: current_price=380; selected_size="Lサイズ"
        st.divider()

    if item_type == "burger" or item_type == "happyset":
        with st.expander("🛠️ ソース・トッピング"):
            c1, c2 = st.columns(2)
            with c1: st.toggle("ソース なし"); st.toggle("オニオン なし")
            with c2: st.toggle("ピクルス なし"); st.toggle("マスタード なし")
        st.divider()

    if item_type == "happyset":
        st.info("🍔 **フードロス対策・寄付設定**")
        c_don1, c_don2 = st.columns(2)
        with c_don1: donate_main = st.checkbox(f"🍔 本体を寄付")
        with c_don2: donate_side = st.checkbox("🍟 ポテトを寄付")
        
        if donate_main or donate_side:
            is_donation = True
            total_donation = 0
            notes = []
            if donate_main:
                total_donation += current_price // 2
                # ★修正: 本体寄付のときは文字を追加しない（スッキリ化）
            if donate_side:
                total_donation += 100
                notes.append("ポテト寄付")
            
            # ★修正: カッコの中身がある時だけカッコを表示する
            if notes:
                donation_note = f"¥{total_donation} 寄付 ({', '.join(notes)})"
            else:
                donation_note = f"¥{total_donation} 寄付"
                
            st.success(f"🏅 **{donation_note}**")
        st.divider()

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"## ¥{current_price}")
    with col2:
        if limit_reached:
            st.button("購入制限に達しています", disabled=True, use_container_width=True)
        else:
            if st.button("カートに追加する", type="primary", use_container_width=True):
                options = {"donation": is_donation, "note": donation_note, "size": selected_size}
                add_to_cart(item, current_price, options)
                st.toast(f"{item['name']} を追加しました！", icon="🛒")
                time.sleep(0.5)
                st.session_state.page = 'list'
                st.rerun()

def show_cart():
    st.title("🛒 ショッピングカート")
    if not st.session_state.cart:
        st.write("カートに商品は入っていません。")
        if st.button("メニューに戻る"):
            st.session_state.page = 'list'
            st.rerun()
        return

    total_amount = 0
    if get_happyset_count_in_cart() > 1 and HAPPY_SET_LIMIT == 1:
        st.error("⚠ エラー: ハッピーセットの購入制限を超えています。数量を減らしてください。")

    for i, order in enumerate(st.session_state.cart):
        with st.container(border=True):
            c1, c2 = st.columns([1, 2])
            with c1: st.image(order['img'], use_container_width=True)
            with c2:
                st.markdown(f"**{order['name']}**")
                if order['options'].get('size'): st.markdown(f"サイズ: **{order['options']['size']}**")
                if order['options']['donation']: st.success(f"💚 {order['options']['note']}")
                else: st.caption("カスタマイズ: 標準")
                st.markdown(f"**¥{order['price']}**")
                total_amount += order['price']
                if st.button("削除", key=f"del_{i}"):
                    st.session_state.cart.pop(i)
                    st.rerun()

    st.divider()
    st.markdown(f"### 合計: ¥{total_amount}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("買い物を続ける", use_container_width=True):
            st.session_state.page = 'list'
            st.rerun()
    with col2:
        if get_happyset_count_in_cart() > HAPPY_SET_LIMIT:
             st.button("購入制限エラー", disabled=True, type="primary", use_container_width=True)
        else:
            if st.button("注文を確定する", type="primary", use_container_width=True):
                st.balloons()
                st.success("注文が完了しました！")
                if any(o['options']['donation'] for o in st.session_state.cart):
                    st.info("🎁 寄付分は子ども食堂支援へ送られます。")
                st.session_state.cart = []
                time.sleep(5)
                st.session_state.page = 'list'
                st.rerun()

# --- メイン処理 ---
if st.session_state.page == 'list':
    show_product_list()
elif st.session_state.page == 'detail':
    show_product_detail()
elif st.session_state.page == 'cart':
    show_cart()