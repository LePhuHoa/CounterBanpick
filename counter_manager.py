"""
Quản lý Counter bằng giao diện web (Streamlit).

Thêm / Sửa / Xóa / Tìm kiếm counter, tự ghi vào data.json.
Không cần sửa JSON bằng tay.

Hai dạng dữ liệu trong "counters_pair" (giữ nguyên như data.json hiện tại):

  Counter riêng (1 tướng):   ["Alice", "Hayate"]
      -> nằm trong counters_pair của tướng bị counter (vd: Marja)

  Counter combo (2 tướng):   [["Taara", "Lorion"], ["Billow"]]
      -> [cặp bị counter, bộ counter]
         nằm trong counters_pair của tướng đầu tiên của cặp
"""

import json
import os
import shutil
import tempfile

import streamlit as st

PLACEHOLDER = "— Chọn tướng —"
NONE_OPTION = "— Không có —"

# Loại nhập
TYPE_1 = "① 1 tướng bị counter → 1-2 tướng counter"
TYPE_2 = "② Cặp tướng → cặp tướng counter"
TYPE_3 = "③ Cặp tướng → 1 tướng counter"
ALL_TYPES = [TYPE_1, TYPE_2, TYPE_3]


# =====================================================================
# 1. ĐỌC / PHÂN TÍCH DỮ LIỆU
# =====================================================================
def _is_str_list(x):
    return isinstance(x, list) and len(x) > 0 and all(isinstance(i, str) for i in x)


def _is_combo(item):
    """[[enemy1, enemy2], [counter...]]"""
    return (
        isinstance(item, list)
        and len(item) == 2
        and _is_str_list(item[0])
        and _is_str_list(item[1])
    )


def iter_entries(db):
    """
    Duyệt mọi counter trong database.
    Mỗi phần tử: {owner, idx, kind('solo'|'combo'), enemy[list], counter[list], raw}
    owner + idx cho biết vị trí chính xác trong data.json để sửa / xóa.
    """
    for owner, hero in db.items():
        if not isinstance(hero, dict):
            continue
        pairs = hero.get("counters_pair", [])
        if not isinstance(pairs, list):
            continue
        for idx, item in enumerate(pairs):
            if _is_combo(item):
                yield {
                    "owner": owner, "idx": idx, "kind": "combo",
                    "enemy": list(item[0]), "counter": list(item[1]), "raw": item,
                }
            elif _is_str_list(item):
                yield {
                    "owner": owner, "idx": idx, "kind": "solo",
                    "enemy": [owner], "counter": list(item), "raw": item,
                }


def _same_set(a, b):
    return len(a) == len(b) and set(a) == set(b)


def _find_duplicate(db, enemy, counter, ignore=None):
    """Trả về entry trùng (cùng tướng bị counter + cùng bộ counter), bỏ qua `ignore`."""
    for e in iter_entries(db):
        if ignore and (e["owner"], e["idx"]) == ignore:
            continue
        if _same_set(e["enemy"], enemy) and _same_set(e["counter"], counter):
            return e
    return None


def _entry_text(enemy, counter):
    return f"{' + '.join(enemy)}  →  {' + '.join(counter)}"


# =====================================================================
# 2. GHI data.json (giữ đúng kiểu định dạng gọn của file gốc)
# =====================================================================
def _dump_db(db, newline):
    lines = ["{"]
    names = list(db.keys())
    for hi, name in enumerate(names):
        hero = db[name]
        lines.append(f"  {json.dumps(name, ensure_ascii=False)}: {{")
        keys = list(hero.keys())
        for ki, key in enumerate(keys):
            val = hero[key]
            comma = "," if ki < len(keys) - 1 else ""
            k = json.dumps(key, ensure_ascii=False)
            if key == "counters_pair" and isinstance(val, list) and val:
                lines.append(f"    {k}: [")
                for vi, item in enumerate(val):
                    c = "," if vi < len(val) - 1 else ""
                    lines.append(f"      {json.dumps(item, ensure_ascii=False)}{c}")
                lines.append(f"    ]{comma}")
            else:
                lines.append(f"    {k}: {json.dumps(val, ensure_ascii=False)}{comma}")
        lines.append("  }" + ("," if hi < len(names) - 1 else ""))
    lines.append("}")
    return newline.join(lines) + newline


def save_db(db, path):
    """Ghi an toàn: sao lưu data.json.bak, ghi file tạm rồi thay thế."""
    newline = "\r\n"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8", newline="") as f:
            head = f.read(4096)
        newline = "\r\n" if "\r\n" in head else "\n"
        shutil.copyfile(path, path + ".bak")

    text = _dump_db(db, newline)
    json.loads(text)  # đảm bảo JSON hợp lệ trước khi ghi đè

    folder = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(suffix=".tmp", dir=folder)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


# =====================================================================
# 3. THAO TÁC DỮ LIỆU (thêm / sửa / xóa)
# =====================================================================
def _validate(db, enemy, counter, ignore=None):
    """Trả về chuỗi lỗi, hoặc None nếu hợp lệ."""
    if len(set(enemy)) != len(enemy):
        return "Hai tướng bị counter không được giống nhau."
    if len(set(counter)) != len(counter):
        return "Hai tướng counter không được giống nhau."
    overlap = set(enemy) & set(counter)
    if overlap:
        return f"{', '.join(sorted(overlap))} không thể vừa là tướng bị counter vừa là counter."
    dup = _find_duplicate(db, enemy, counter, ignore)
    if dup:
        return f"Counter này đã có rồi: {_entry_text(dup['enemy'], dup['counter'])}"
    return None


def _build_item(enemy, counter):
    return list(counter) if len(enemy) == 1 else [list(enemy), list(counter)]


def _pairs_of(db, hero):
    hero_data = db[hero]
    if not isinstance(hero_data.get("counters_pair"), list):
        hero_data["counters_pair"] = []
    return hero_data["counters_pair"]


def add_entry(db, path, enemy, counter):
    err = _validate(db, enemy, counter)
    if err:
        return err
    _pairs_of(db, enemy[0]).append(_build_item(enemy, counter))
    save_db(db, path)
    return None


def update_entry(db, path, owner, idx, snapshot, enemy, counter):
    pairs = _pairs_of(db, owner)
    if idx >= len(pairs) or pairs[idx] != snapshot:
        return "Dữ liệu đã thay đổi, hãy tải lại trang rồi thử lại."
    err = _validate(db, enemy, counter, ignore=(owner, idx))
    if err:
        return err

    new_item = _build_item(enemy, counter)
    new_owner = enemy[0]
    if new_owner == owner:
        pairs[idx] = new_item
    else:
        del pairs[idx]
        _pairs_of(db, new_owner).append(new_item)
    save_db(db, path)
    return None


def delete_entry(db, path, owner, idx, snapshot):
    pairs = _pairs_of(db, owner)
    if idx >= len(pairs) or pairs[idx] != snapshot:
        return "Dữ liệu đã thay đổi, hãy tải lại trang rồi thử lại."
    del pairs[idx]
    save_db(db, path)
    return None


# =====================================================================
# 4. GIAO DIỆN
# =====================================================================
def _hero_select(label, key, names, default=None, optional=False):
    first = NONE_OPTION if optional else PLACEHOLDER
    options = [first] + names
    index = options.index(default) if default in options else 0
    value = st.selectbox(label, options, index=index, key=key)
    return None if value == first else value


def _entry_fields(prefix, names, n_enemy, counter_mode, default_enemy=(), default_counter=()):
    """
    Vẽ các dropdown. Trả về (enemy, counter, thiếu_gì).
      counter_mode: 'required2' (bắt buộc 2) | 'optional2' (Counter 2 tùy chọn) | 'single' (chỉ 1)
    """
    de = list(default_enemy) + [None, None]
    dc = list(default_counter) + [None, None]

    enemy = []
    for i in range(n_enemy):
        enemy.append(_hero_select(f"Tướng {i + 1}" if n_enemy > 1 else "Tướng bị counter",
                                  f"{prefix}_e{i}", names, de[i]))

    st.markdown("**Counter**")
    c1 = _hero_select("Counter 1", f"{prefix}_c0", names, dc[0])
    counter = [c1]
    if counter_mode == "required2":
        counter.append(_hero_select("Counter 2", f"{prefix}_c1", names, dc[1]))
    elif counter_mode == "optional2":
        counter.append(_hero_select("Counter 2", f"{prefix}_c1", names, dc[1], optional=True))

    missing = any(e is None for e in enemy) or c1 is None or (
        counter_mode == "required2" and counter[1] is None
    )
    counter = [c for c in counter if c]
    return [e for e in enemy if e], counter, missing


def _hero_chip(name, get_img):
    path = get_img(name)
    if path:
        st.image(path, width=44)
    st.caption(name)


def _render_add_tab(db, path, names):
    st.markdown("#### ➕ THÊM COUNTER")
    entry_type = st.radio("Loại nhập", ALL_TYPES, key="cm_add_type")

    if entry_type == TYPE_1:
        st.caption("Ví dụ: Marja → Alice + Hayate")
        n_enemy, mode = 1, "optional2"
    elif entry_type == TYPE_2:
        st.caption("Ví dụ: Eland'orr + Y'bneth → Taara + Lorion")
        n_enemy, mode = 2, "required2"
    else:
        st.caption("Ví dụ: Taara + Lorion → Billow")
        n_enemy, mode = 2, "single"

    prefix = f"cm_add_{ALL_TYPES.index(entry_type)}"
    with st.form(f"{prefix}_form", clear_on_submit=True):
        enemy, counter, missing = _entry_fields(prefix, names, n_enemy, mode)
        submitted = st.form_submit_button("💾 THÊM COUNTER", use_container_width=True)

    if submitted:
        if missing:
            st.error("Hãy chọn đủ các tướng còn thiếu.")
            return
        err = add_entry(db, path, enemy, counter)
        if err:
            st.error(err)
        else:
            st.success(f"✅ Đã lưu vào data.json:  {_entry_text(enemy, counter)}")


def _render_entry_row(entry, get_img):
    c_enemy, c_counter, c_edit, c_del = st.columns([5, 5, 1, 1])
    with c_enemy:
        st.markdown("**" + " + ".join(entry["enemy"]) + "**")
    with c_counter:
        st.markdown("→ " + " + ".join(entry["counter"]))
    key = f"{entry['owner']}_{entry['idx']}"
    if c_edit.button("✏️", key=f"cm_edit_{key}", help="Sửa"):
        st.session_state["cm_edit"] = (entry["owner"], entry["idx"], json.dumps(entry["raw"]))
        st.session_state.pop("cm_del", None)
        st.rerun()
    if c_del.button("🗑️", key=f"cm_del_{key}", help="Xóa"):
        st.session_state["cm_del"] = (entry["owner"], entry["idx"], json.dumps(entry["raw"]))
        st.session_state.pop("cm_edit", None)
        st.rerun()


def _render_edit_form(db, path, names):
    owner, idx, snap_json = st.session_state["cm_edit"]
    snapshot = json.loads(snap_json)
    entries = [e for e in iter_entries(db) if e["owner"] == owner and e["idx"] == idx]
    if not entries or entries[0]["raw"] != snapshot:
        st.session_state.pop("cm_edit", None)
        st.warning("Không tìm thấy mục cần sửa (dữ liệu đã thay đổi).")
        return
    entry = entries[0]

    st.markdown("##### ✏️ SỬA COUNTER")
    st.caption(f"Đang sửa: {_entry_text(entry['enemy'], entry['counter'])}")
    prefix = f"cm_editf_{owner}_{idx}"
    with st.form(f"{prefix}_form"):
        enemy, counter, missing = _entry_fields(
            prefix, names, len(entry["enemy"]), "optional2",
            default_enemy=entry["enemy"], default_counter=entry["counter"],
        )
        col_save, col_cancel = st.columns(2)
        saved = col_save.form_submit_button("💾 LƯU THAY ĐỔI", use_container_width=True)
        cancelled = col_cancel.form_submit_button("Hủy", use_container_width=True)

    if cancelled:
        st.session_state.pop("cm_edit", None)
        st.rerun()
    if saved:
        if missing:
            st.error("Hãy chọn đủ các tướng còn thiếu.")
            return
        err = update_entry(db, path, owner, idx, snapshot, enemy, counter)
        if err:
            st.error(err)
        else:
            st.session_state.pop("cm_edit", None)
            st.session_state["cm_flash"] = f"✅ Đã cập nhật:  {_entry_text(enemy, counter)}"
            st.rerun()


def _render_delete_confirm(db, path):
    owner, idx, snap_json = st.session_state["cm_del"]
    snapshot = json.loads(snap_json)
    entries = [e for e in iter_entries(db) if e["owner"] == owner and e["idx"] == idx]
    if not entries or entries[0]["raw"] != snapshot:
        st.session_state.pop("cm_del", None)
        return
    entry = entries[0]
    st.warning(f"Xóa counter này?  **{_entry_text(entry['enemy'], entry['counter'])}**")
    c_yes, c_no, _ = st.columns([2, 2, 6])
    if c_yes.button("🗑️ Xác nhận xóa", key="cm_del_yes"):
        err = delete_entry(db, path, owner, idx, snapshot)
        st.session_state.pop("cm_del", None)
        st.session_state["cm_flash"] = err or f"🗑️ Đã xóa:  {_entry_text(entry['enemy'], entry['counter'])}"
        st.rerun()
    if c_no.button("Hủy", key="cm_del_no"):
        st.session_state.pop("cm_del", None)
        st.rerun()


def _render_search_tab(db, path, names, get_img):
    st.markdown("#### 🔍 TÌM KIẾM / SỬA / XÓA")

    flash = st.session_state.pop("cm_flash", None)
    if flash:
        st.success(flash)

    hero = _hero_select("Tìm theo tướng (gõ tên để lọc)", "cm_search_hero", names)
    all_entries = list(iter_entries(db))

    if "cm_edit" in st.session_state:
        _render_edit_form(db, path, names)
        st.markdown("---")
    if "cm_del" in st.session_state:
        _render_delete_confirm(db, path)

    if not hero:
        total = len(all_entries)
        st.caption(f"Tổng cộng {total} counter trong data.json. Chọn một tướng để xem chi tiết.")
        owners = {}
        for e in all_entries:
            for h in e["enemy"]:
                owners[h] = owners.get(h, 0) + 1
        if owners:
            with st.expander("Danh sách tướng đã có dữ liệu counter"):
                for h in sorted(owners):
                    st.write(f"• {h}: {owners[h]} counter")
        return

    solo = [e for e in all_entries if e["kind"] == "solo" and e["owner"] == hero]
    combos = [e for e in all_entries if e["kind"] == "combo" and hero in e["enemy"]]

    st.markdown(f"##### 📋 COUNTER CỦA {hero.upper()}")
    path_img = get_img(hero)
    if path_img:
        st.image(path_img, width=60)

    if not solo and not combos:
        st.info("Chưa có dữ liệu counter cho tướng này. Qua tab ➕ Thêm để nhập.")
        return

    if solo:
        st.markdown("**Counter riêng:**")
        for e in solo:
            _render_entry_row(e, get_img)
    if combos:
        st.markdown("**Combo:**")
        for e in combos:
            _render_entry_row(e, get_img)


def render_counter_manager(db, data_path, get_img_path):
    """Gọi từ game.py: vẽ toàn bộ trang Quản lý Counter."""
    st.title("⚙️ QUẢN LÝ COUNTER")
    st.caption("Chọn bằng dropdown, bấm lưu là data.json tự cập nhật. Không cần viết JSON.")

    if not db:
        st.error("Không đọc được data.json.")
        return

    names = sorted(db.keys())
    section = st.radio(
        "Chức năng", ["➕ Thêm", "🔍 Tìm / Sửa / Xóa"],
        horizontal=True, key="cm_section", label_visibility="collapsed",
    )
    st.markdown("---")
    if section == "➕ Thêm":
        _render_add_tab(db, data_path, names)
    else:
        _render_search_tab(db, data_path, names, get_img_path)
