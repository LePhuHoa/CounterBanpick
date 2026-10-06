import streamlit as st
import json
import os
import base64
from counter_manager import render_counter_manager

# 1. CẤU HÌNH GIAO DIỆN WEB RỘNG RÃI
st.set_page_config(page_title="Hệ Thống Ban/Pick Dự Đoán Counter", page_icon="🎮", layout="wide")

# CSS làm đẹp giao diện chuẩn giải đấu
st.markdown("""
    <style>
    .hero-box {
        text-align: center;
        margin-bottom: 12px;
        background-color: #1c1f26;
        padding: 6px;
        border-radius: 6px;
        border: 1px solid #2d323f;
    }
    .hero-avatar {
        width: 80px !important;
        height: 80px !important;
        border-radius: 6px;
        object-fit: cover;
        border: 2px solid #3b4252;
    }
    .hero-name {
        font-size: 12px;
        font-weight: bold;
        color: #e5e9f0;
        margin-top: 4px;
        margin-bottom: 4px;
    }
    .predict-combo-box {
        background-color: #1b2234;
        border: 1px solid #3b82f6;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .counter-pair-mini {
        background-color: #241a1a;
        border: 1px solid #ef4444;
        border-radius: 6px;
        padding: 8px;
        text-align: center;
        margin-bottom: 8px;
    }
    .counter-card-blue {
        background-color: #1e293b;
        padding: 12px;
        border-radius: 6px;
        border-left: 5px solid #3b82f6;
        margin-bottom: 15px;
    }
    .counter-card-red {
        background-color: #2e1a1a;
        padding: 12px;
        border-radius: 6px;
        border-left: 5px solid #ef4444;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. HÀM ĐỌC DỮ LIỆU TỪ FILE JSON
DATA_FILE = "data.json"

def load_heroes_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

HEROES_DB = load_heroes_data()

# Hàm mã hóa ảnh sang Base64
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            ext = os.path.splitext(path)[1].lower()
            mime = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".webp": "image/webp",
                ".gif": "image/gif",
            }.get(ext, "image/jpeg")
            return f"data:{mime};base64,{base64.b64encode(image_file.read()).decode()}"
    return "data:image/svg+xml;utf8,<svg xmlns='http://w3.org' width='80' height='80' style='background:%23333'></svg>"

def get_hero_img_path(hero_name):
    if hero_name in HEROES_DB and os.path.exists(HEROES_DB[hero_name]["img"]):
        return HEROES_DB[hero_name]["img"]
    return None

# --- CHUYỂN CHẾ ĐỘ: BAN/PICK <-> QUẢN LÝ COUNTER ---
app_mode = st.sidebar.radio("📂 Chế độ", ["🎮 Ban/Pick", "⚙️ Quản lý Counter"], key="app_mode")
if app_mode == "⚙️ Quản lý Counter":
    render_counter_manager(HEROES_DB, DATA_FILE, get_hero_img_path)
    st.stop()

# --- QUẢN LÝ TIẾN TRÌNH VÒNG PICK ---
if "bp_step" not in st.session_state:
    st.session_state.bp_step = 1
    st.session_state.bp_history = {}

if st.button("🔄 Reset / Làm lại lượt Cấm Chọn"):
    st.session_state.bp_step = 1
    st.session_state.bp_history = {}
    st.rerun()

current_step = st.session_state.bp_step
history = st.session_state.bp_history

PICK_STEPS_INFO = {
    1: {"team": "XANH", "count": 1, "card_class": "counter-card-blue", "desc": "🔷 LƯỢT 1: Team XANH chọn 1 con tướng đầu tiên"},
    2: {"team": "ĐỎ", "count": 2, "card_class": "counter-card-red", "desc": "🔻 LƯỢT 2: Team ĐỎ chọn 2 con tướng tiếp theo"},
    3: {"team": "XANH", "count": 2, "card_class": "counter-card-blue", "desc": "🔷 LƯỢT 3: Team XANH chọn 2 con tướng"},
    4: {"team": "ĐỎ", "count": 2, "card_class": "counter-card-red", "desc": "🔻 LƯỢT 4: Team ĐỎ chọn 2 con tướng"},
    5: {"team": "XANH", "count": 2, "card_class": "counter-card-blue", "desc": "🔷 LƯỢT 5: Team XANH chọn 2 con tướng"},
    6: {"team": "ĐỎ", "count": 1, "card_class": "counter-card-red", "desc": "🔻 LƯỢT 6: Team ĐỎ chọn 1 con tướng cuối cùng Chốt Hạ"}
}

st.title("🎮 PHẦN MỀM BAN/PICK LIÊN QUÂN MOBILE NÂNG CẤP THUẬT TOÁN")
st.write("Thứ tự: **Xanh 1 ➡️ Đỏ 2 ➡️ Xanh 2 ➡️ Đỏ 2 ➡️ Xanh 2 ➡️ Đỏ 1**")
st.markdown("---")


# --- 3. THUẬT TOÁN QUÉT TOÀN BỘ BỘ ĐÔI COUNTER DIỆN RỘNG (YÊU CẦU MỚI) ---
# Tìm hàm display_all_possible_counters trong file game.py của bạn (khoảng dòng 90) và đổi thành đoạn này:

# THAY THẾ TOÀN BỘ HÀM NÀY TRONG FILE GAME.PY CỦA BẠN:

# THAY THẾ TOÀN BỘ HÀM NÀY TRONG FILE GAME.PY CỦA BẠN ĐỂ SỬA LỖI KHÔNG HIỆN COUNTER:

# DÁN ĐÈ TOÀN BỘ HÀM NÀY VÀO FILE GAME.PY ĐỂ XỬ LÝ TRIỆT ĐỂ LỖI DỮ LIỆU CHUỖI:

# DÁN ĐÈ TOÀN BỘ HÀM NÀY VÀO FILE GAME.PY ĐỂ KHẮC PHỤC HOÀN TOÀN LỖI LỌC PHẦN TỬ JSON:

# DÁN ĐÈ TOÀN BỘ HÀM NÀY VÀO FILE GAME.PY ĐỂ KHẮC PHỤC HOÀN TOÀN LỖI ĐỌC LIST:

# DÁN ĐÈ TOÀN BỘ HÀM NÀY VÀO FILE GAME.PY ĐỂ HIỂN THỊ 100% KẾT QUẢ COUNTER:

def _normalize_hero_list(value):
    """Đưa dữ liệu tướng về list[str]."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [x for x in value if isinstance(x, str)]
    return []


def _same_hero_set(list_a, list_b):
    """So sánh 2 đội hình không phụ thuộc thứ tự tướng."""
    a = _normalize_hero_list(list_a)
    b = _normalize_hero_list(list_b)
    return len(a) == len(b) and set(a) == set(b)


def _iter_counter_relations():
    """
    Đọc toàn bộ counters_pair trong data.json.

    Hỗ trợ 2 dạng dữ liệu:

    1. Kịch bản combo:
       [ ["Marja", "Ryoma"], ["Alice", "Hayate"] ]

    2. Dữ liệu counter trực tiếp của 1 tướng:
       ["Maloch", "Dolia"]
       hoặc ["Maloch"]
    """
    for hero_name, hero_data in HEROES_DB.items():
        if not isinstance(hero_data, dict):
            continue

        raw_pairs = hero_data.get("counters_pair", [])
        if not isinstance(raw_pairs, list):
            continue

        for relation in raw_pairs:
            if not isinstance(relation, list):
                continue

            # Dạng: [[enemy1, enemy2], [counter1, counter2]]
            if (
                len(relation) == 2
                and isinstance(relation[0], list)
                and isinstance(relation[1], list)
            ):
                enemy_combo = _normalize_hero_list(relation[0])
                counter_combo = _normalize_hero_list(relation[1])

                if enemy_combo and counter_combo:
                    yield enemy_combo, counter_combo, "combo"
                continue

            # Dạng dữ liệu trực tiếp của hero:
            # "Marja": {"counters_pair": [["Alice", "Hayate"], ...]}
            # hoặc "Marja": {"counters_pair": ["Alice", "Hayate"]}
            # Mỗi item được xem là counter cho chính hero_name.
            if relation and all(isinstance(x, str) for x in relation):
                counter_combo = _normalize_hero_list(relation)
                if counter_combo:
                    yield [hero_name], counter_combo, "single"


def _add_prediction(predicted_combos, label, counter_combo):
    counter_combo = _normalize_hero_list(counter_combo)
    if not counter_combo:
        return

    predicted_combos.setdefault(label, [])
    if counter_combo not in predicted_combos[label]:
        predicted_combos[label].append(counter_combo)


def _find_counters_for_selection(selected_heroes_list, current_step):
    """
    Tìm counter theo đúng luật 6 lượt:

    Lượt 1: 1 tướng -> quét mọi combo chứa tướng đó.
             Ví dụ Marja + Ryoma -> Alice + Hayate cũng được hiện
             ngay khi mới pick Marja.

    Lượt 2/3/4: 2 tướng -> ưu tiên dữ liệu combo chính xác.
                Nếu KHÔNG có combo chính xác -> lấy dữ liệu counter
                của từng tướng riêng lẻ.

    Lượt 5: 2 tướng -> giống lượt 2/3/4 nhưng kết quả ưu tiên
             counter chỉ 1 tướng.

    Lượt 6: 1 tướng -> không cần dự đoán tiếp.
    """
    selected = _normalize_hero_list(selected_heroes_list)
    if not selected:
        return [], False

    if current_step == 6:
        return [], False

    relations = list(_iter_counter_relations())
    results = []

    # ---------------------------------------------------------
    # LƯỢT 1: PICK 1 -> HIỆN CÁC COUNTER COMBO LIÊN QUAN
    # ---------------------------------------------------------
    if current_step == 1:
        target = selected[0]

        for enemy_combo, counter_combo, relation_type in relations:
            # Nếu Marja nằm trong [Marja, Ryoma], dữ liệu đó cũng
            # phải xuất hiện ngay khi chỉ mới pick Marja.
            if target in enemy_combo:
                results.append({
                    "enemy": enemy_combo,
                    "counter": counter_combo,
                    "type": relation_type,
                    "exact": False,
                })

        # Loại trùng nhưng giữ nguyên thứ tự trong data.json.
        unique = []
        seen = set()
        for item in results:
            key = (tuple(item["enemy"]), tuple(item["counter"]))
            if key not in seen:
                seen.add(key)
                unique.append(item)
        return unique, bool(unique)

    # ---------------------------------------------------------
    # LƯỢT 2/3/4/5: PICK 2
    # ---------------------------------------------------------
    if len(selected) != 2:
        return [], False

    # 1. ƯU TIÊN KỊCH BẢN COMBO CHÍNH XÁC.
    exact_results = []
    for enemy_combo, counter_combo, relation_type in relations:
        if relation_type == "combo" and _same_hero_set(enemy_combo, selected):
            exact_results.append({
                "enemy": enemy_combo,
                "counter": counter_combo,
                "type": relation_type,
                "exact": True,
            })

    if exact_results:
        return exact_results, True

    # 2. KHÔNG CÓ COMBO 2 TƯỚNG -> FALLBACK VỀ COUNTER TỪNG TƯỚNG.
    fallback_results = []
    for hero in selected:
        for enemy_combo, counter_combo, relation_type in relations:
            if relation_type == "single" and _same_hero_set(enemy_combo, [hero]):
                fallback_results.append({
                    "enemy": enemy_combo,
                    "counter": counter_combo,
                    "type": "fallback",
                    "exact": False,
                })

    # Loại trùng.
    unique = []
    seen = set()
    for item in fallback_results:
        key = (tuple(item["enemy"]), tuple(item["counter"]))
        if key not in seen:
            seen.add(key)
            unique.append(item)

    # Lượt 5 chỉ ưu tiên dữ liệu counter 1 tướng.
    if current_step == 5:
        one_hero_results = [x for x in unique if len(x["counter"]) == 1]
        if one_hero_results:
            return one_hero_results, True

    return unique, bool(unique)


def _render_counter_card(counter_combo, index):
    """Hiển thị 1 bộ counter, hỗ trợ bộ 1 hoặc 2 tướng."""
    counter_combo = _normalize_hero_list(counter_combo)
    if not counter_combo:
        return

    st.markdown(
        '<div class="counter-pair-mini" style="background-color: #241a1a; '
        'border: 1px solid #ef4444; border-radius: 6px; padding: 8px; '
        'text-align: center; margin-bottom: 8px;">',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<span style='font-size:11px; color:#ef4444; font-weight:bold;'>"
        f"Bộ {index + 1}</span>",
        unsafe_allow_html=True,
    )

    # Bộ 1 hoặc bộ 2 đều hiển thị đẹp.
    display_cols = st.columns(max(len(counter_combo), 1))
    for i, hero in enumerate(counter_combo):
        with display_cols[i]:
            path = get_hero_img_path(hero)
            if path:
                st.image(path, width=55)
            st.markdown(
                f"<p style='font-size:11px; margin:0; white-space:nowrap;'>"
                f"{hero}</p>",
                unsafe_allow_html=True,
            )

    st.markdown('</div>', unsafe_allow_html=True)


def display_predictive_counter(selected_heroes_list, current_step=None):
    """
    Hiển thị counter theo đúng luật Ban/Pick:

    Lượt 1:
      - Nếu tướng vừa pick có dữ liệu counter riêng -> CHỈ dùng dữ liệu riêng.
      - Nếu không có counter riêng -> tìm các kịch bản combo có chứa tướng đó.

    Lượt 2-4:
      - Ưu tiên dữ liệu counter cho đúng cặp 2 tướng.
      - Nếu không có -> lấy counter riêng của từng tướng.

    Lượt 5:
      - Tương tự lượt 2-4 nhưng chỉ hiển thị counter 1 tướng nếu dữ liệu phù hợp.

    Lượt 6:
      - Không hiển thị counter.
    """
    if not selected_heroes_list:
        return

    # Chuẩn hóa dữ liệu đầu vào.
    if isinstance(selected_heroes_list, str):
        selected_heroes_list = [selected_heroes_list]

    selected_heroes_list = [
        h for h in selected_heroes_list
        if isinstance(h, str) and h.strip()
    ]

    if not selected_heroes_list:
        return

    # Lượt 6: Đỏ pick 1 để chốt, không cần counter.
    if current_step == 6:
        return

    predicted_combos = {}

    def add_combo(mode, combo):
        """Thêm một bộ counter, tránh trùng."""
        if not isinstance(combo, list):
            return

        combo = [x for x in combo if isinstance(x, str) and x.strip()]
        if not combo:
            return

        if mode not in predicted_combos:
            predicted_combos[mode] = []

        if combo not in predicted_combos[mode]:
            predicted_combos[mode].append(combo)

    def get_solo_counters(hero_name):
        """
        Lấy dữ liệu counter riêng của một tướng.

        Chấp nhận:
          ["Maloch", "Dolia"]
        hoặc:
          [["Maloch", "Dolia"], ["Fennik", "Capheny"]]
        """
        hero_data = HEROES_DB.get(hero_name, {})
        raw = hero_data.get("counters_pair", [])

        if not isinstance(raw, list):
            return []

        result = []

        for item in raw:
            # Dạng trực tiếp: ["A", "B"]
            if (
                isinstance(item, list)
                and len(item) > 0
                and all(isinstance(x, str) for x in item)
            ):
                result.append(item)

            # Dạng lồng: [["A", "B"], ["C", "D"]]
            elif isinstance(item, list):
                for sub_item in item:
                    if (
                        isinstance(sub_item, list)
                        and sub_item
                        and all(isinstance(x, str) for x in sub_item)
                    ):
                        result.append(sub_item)

        # Loại trùng
        unique = []
        for combo in result:
            if combo not in unique:
                unique.append(combo)

        return unique

    def find_exact_pair_counters(h1, h2):
        """Tìm counter cho đúng cặp h1 + h2 trong toàn bộ database."""
        result = []

        for _, hero_data in HEROES_DB.items():
            raw_pairs = hero_data.get("counters_pair", [])

            if not isinstance(raw_pairs, list):
                continue

            for relation in raw_pairs:
                if not (
                    isinstance(relation, list)
                    and len(relation) == 2
                    and isinstance(relation[0], list)
                    and isinstance(relation[1], list)
                ):
                    continue

                enemy_combo = relation[0]
                counter_combo = relation[1]

                if (
                    len(enemy_combo) >= 2
                    and h1 in enemy_combo
                    and h2 in enemy_combo
                    and h1 != h2
                ):
                    if counter_combo not in result:
                        result.append(counter_combo)

        return result

    # ============================================================
    # LƯỢT 1: PICK 1
    # ============================================================
    if len(selected_heroes_list) == 1:
        target_hero = selected_heroes_list[0]

        # QUAN TRỌNG:
        # Trước tiên tìm counter RIÊNG của Marja.
        solo_counters = get_solo_counters(target_hero)

        # Nếu có counter riêng -> CHỈ hiện counter riêng.
        if solo_counters:
            predicted_combos["Bất kỳ vị tướng nào"] = []
            for combo in solo_counters:
                add_combo("Bất kỳ vị tướng nào", combo)

        # Nếu KHÔNG có counter riêng -> mới tìm các combo:
        # Marja + HeroB -> CounterA + CounterB
        else:
            for _, hero_data in HEROES_DB.items():
                raw_pairs = hero_data.get("counters_pair", [])

                if not isinstance(raw_pairs, list):
                    continue

                for relation in raw_pairs:
                    if not (
                        isinstance(relation, list)
                        and len(relation) == 2
                        and isinstance(relation[0], list)
                        and isinstance(relation[1], list)
                    ):
                        continue

                    enemy_combo = relation[0]
                    counter_combo = relation[1]

                    if target_hero not in enemy_combo:
                        continue

                    # Chỉ xử lý dữ liệu combo có ít nhất 2 tướng.
                    if len(enemy_combo) < 2:
                        continue

                    partner = next(
                        (h for h in enemy_combo if h != target_hero),
                        None
                    )

                    if partner:
                        add_combo(partner, counter_combo)

    # ============================================================
    # LƯỢT 2, 3, 4, 5: PICK 2
    # ============================================================
    elif len(selected_heroes_list) == 2:
        h1, h2 = selected_heroes_list

        # 1. Ưu tiên dữ liệu counter chính xác cho cả cặp.
        exact_counters = find_exact_pair_counters(h1, h2)

        if exact_counters:
            predicted_combos["Khớp kịch bản chính thức"] = []
            for combo in exact_counters:
                add_combo("Khớp kịch bản chính thức", combo)

        # 2. Không có dữ liệu cho cả cặp:
        #    lấy dữ liệu counter riêng của từng tướng.
        else:
            h1_solo = get_solo_counters(h1)
            h2_solo = get_solo_counters(h2)

            if h1_solo:
                for combo in h1_solo:
                    add_combo(h1, combo)

            if h2_solo:
                for combo in h2_solo:
                    add_combo(h2, combo)

    # ============================================================
    # RENDER
    # ============================================================
    if not predicted_combos:
        st.info(
            "ℹ️ Chưa có dữ liệu counter cho các tướng đang chọn."
        )
        return

    for mode, counter_pairs_list in predicted_combos.items():

        if mode == "Khớp kịch bản chính thức":
            st.markdown("""
            <div style="background-color:#2e1a1a; padding:12px;
                        border-radius:6px; border-left:5px solid #ef4444;
                        margin-bottom:15px;">
                <h4 style="margin:0 0 5px 0; color:#ffcc00; font-size:14px;">
                    🔥 ĐÃ PHÁT HIỆN BỘ ĐÔI COUNTER KHỚP KỊCH BẢN:
                </h4>
                <p style="margin:0; font-size:12px; color:#ccc;">
                    Ưu tiên các bộ counter được khai báo trực tiếp cho cặp tướng này.
                </p>
            </div>
            """, unsafe_allow_html=True)

        elif len(selected_heroes_list) == 1:
            display_name = selected_heroes_list[0].upper()

            st.markdown(f"""
            <div class="predict-combo-box"
                 style="border-left:5px solid #ffcc00;">
                <h4 style="margin:0 0 5px 0; color:#ffcc00; font-size:14px;">
                    💡 COUNTER ĐỀ XUẤT CHO [{display_name}]:
                </h4>
                <p style="margin:0; font-size:12px; color:#ccc;">
                    Các bộ counter có sẵn trong dữ liệu.
                </p>
            </div>
            """, unsafe_allow_html=True)

        else:
            display_name = mode

            st.markdown(f"""
            <div class="predict-combo-box"
                 style="background-color:#1b2234;
                        border:1px solid #3b82f6;
                        padding:15px; margin-bottom:15px;
                        border-radius:8px;">
                <h4 style="margin:0 0 5px 0; color:#ffcc00; font-size:14px;">
                    💡 COUNTER CHO {display_name.upper()}:
                </h4>
                <p style="margin:0; font-size:12px; color:#ccc;">
                    Đây là các bộ counter lấy từ dữ liệu của từng tướng.
                </p>
            </div>
            """, unsafe_allow_html=True)

        cols = st.columns(max(len(counter_pairs_list), 1))

        for idx, c_pair in enumerate(counter_pairs_list):
            with cols[idx]:
                st.markdown(
                    '<div class="counter-pair-mini">',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"<span style='font-size:11px; color:#ef4444; "
                    f"font-weight:bold;'>Bộ {idx + 1}</span>",
                    unsafe_allow_html=True
                )

                c1 = c_pair[0] if len(c_pair) > 0 else "Chưa rõ"
                c2 = c_pair[1] if len(c_pair) > 1 else None

                if c2:
                    img_c1, img_c2 = st.columns(2)

                    with img_c1:
                        p1 = get_hero_img_path(c1)
                        if p1:
                            st.image(p1, width=45)
                        st.markdown(
                            f"<p style='font-size:11px; margin:0; "
                            f"white-space:nowrap;'>{c1}</p>",
                            unsafe_allow_html=True
                        )

                    with img_c2:
                        p2 = get_hero_img_path(c2)
                        if p2:
                            st.image(p2, width=45)
                        st.markdown(
                            f"<p style='font-size:11px; margin:0; "
                            f"white-space:nowrap;'>{c2}</p>",
                            unsafe_allow_html=True
                        )
                else:
                    p1 = get_hero_img_path(c1)
                    if p1:
                        st.image(p1, width=55)
                    st.markdown(
                        f"<p style='font-size:11px; margin:0; "
                        f"text-align:center;'>{c1}</p>",
                        unsafe_allow_html=True
                    )

                st.markdown("</div>", unsafe_allow_html=True)

# --- 4. GIAO DIỆN HIỂN THỊ TIẾN TRÌNH LƯỢT HÀNG NGANG ---
if current_step <= 6:
    step_info = PICK_STEPS_INFO[current_step]
    
    st.markdown(f"""
    <div class="{step_info['card_class']}">
        <h3 style='margin:0; color:#ffcc00; font-size:16px;'>{step_info['desc']}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    step_key = f"step_{current_step}_choices"
    if step_key not in st.session_state:
        st.session_state[step_key] = []
        
    current_choices = st.session_state[step_key]
    
    if current_choices:
        st.write("📌 Tướng đã chọn ở lượt này:")
        pick_cols = st.columns(6)
        for idx, h_name in enumerate(current_choices):
            with pick_cols[idx]:
                path = get_hero_img_path(h_name)
                if path: st.image(path, width=60, caption=h_name)
                
        # --- HIỂN THỊ COUNTER THEO ĐÚNG 6 LƯỢT BAN/PICK ---
        # Lượt 1: chọn 1 -> hiện counter ngay.
        if current_step == 1 and len(current_choices) == 1:
            display_predictive_counter(current_choices, current_step)

        # Lượt 2, 3, 4, 5: phải chọn đủ 2 -> hiện counter.
        elif current_step in (2, 3, 4, 5) and len(current_choices) == 2:
            display_predictive_counter(current_choices, current_step)
            st.success("Đã chọn đủ số lượng tướng cho lượt này. Nhấn nút Khóa để tiếp tục.")

        # Lượt 6: chọn 1 -> không hiện counter tiếp, chỉ chốt đội hình.
        elif current_step == 6 and len(current_choices) == 1:
            st.success("Đã chọn tướng cuối cùng. Nhấn nút Khóa để kết thúc trận đấu.")
        
        if len(current_choices) == step_info["count"]:
            if st.button(f"🔒 Khóa lượt chọn của Team {step_info['team']} ➡️"):
                history[f"Lượt_{current_step}"] = current_choices.copy()
                st.session_state.bp_step += 1
                st.session_state[step_key] = []
                st.rerun()
    else:
        st.caption("Chưa chọn tướng nào ở lượt này, vui lòng click nút [➕ Chọn] ở danh sách phía dưới...")

    st.markdown("---")

    # --- 5. BẢNG DANH SÁCH TƯỚNG ---
    st.write("### 📋 BẢNG CHỌN TƯỚNG")
    role_options = ["Tất cả", "Đấu Sĩ", "Đỡ Đòn", "Pháp Sư", "Sát Thủ", "Xạ Thủ", "Trợ Thủ"]
    selected_role = st.radio("Vai trò:", options=role_options, horizontal=True, label_visibility="collapsed")
    
    filtered_heroes = {}
    for h_name, h_data in HEROES_DB.items():
        if selected_role == "Tất cả" or selected_role in h_data.get("roles", []):
            filtered_heroes[h_name] = h_data
            
    if filtered_heroes:
        sorted_names = sorted(list(filtered_heroes.keys()))
        columns_per_row = 10
        
        for i in range(0, len(sorted_names), columns_per_row):
            row_heroes = sorted_names[i:i + columns_per_row]
            cols = st.columns(columns_per_row)
            
            for idx, name in enumerate(row_heroes):
                with cols[idx]:
                    img_base64 = get_image_base64(filtered_heroes[name]['img'])
                    st.markdown(f"""
                        <div class="hero-box">
                            <img src="{img_base64}" class="hero-avatar">
                            <div class="hero-name">{name}</div>
                        </div>
                    """, unsafe_allow_html=True)
                                        # RÀNG BUỘC SỐ LƯỢNG CHỌN CỦA LƯỢT VÀ NÚT TƯƠNG TÁC
                    is_disable = len(current_choices) >= step_info["count"] and name not in current_choices
                    
                    if name in current_choices:
                        if st.button("❌ Hủy", key=f"del_{name}_{current_step}", use_container_width=True):
                            current_choices.remove(name)
                            st.rerun()
                    else:
                        if st.button("➕ Chọn", key=f"add_{name}_{current_step}", use_container_width=True, disabled=is_disable):
                            current_choices.append(name)
                            st.rerun()
else:
    # MÀN HÌNH TỔNG KẾT SAU KHI HOÀN THÀNH CẢ 6 LƯỢT PICK
    st.balloons()
    st.header("🏆 TỔNG KẾT ĐỘI HÌNH BAN/PICK TRẬN ĐẤU")
    col_x, col_d = st.columns(2)
    with col_x:
        st.info("🔷 TEAM XANH ĐỘI HÌNH:")
        x_heroes = history.get("Lượt_1", []) + history.get("Lượt_3", []) + history.get("Lượt_5", [])
        for h in x_heroes:
            st.markdown(f"- **{h}**")
            path = get_hero_img_path(h)
            if path: st.image(path, width=50)
    with col_d:
        st.error("🔻 TEAM ĐỎ ĐỘI HÌNH:")
        d_heroes = history.get("Lượt_2", []) + history.get("Lượt_4", []) + history.get("Lượt_6", [])
        for h in d_heroes:
            st.markdown(f"- **{h}**")
            path = get_hero_img_path(h)
            if path: st.image(path, width=50)
