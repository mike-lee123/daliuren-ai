import io
import os
from datetime import date, datetime, time

import streamlit as st
from lunar_python import Lunar, Solar
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(
    page_title="玄機閣 · 大六壬起課",
    page_icon="☯",
    layout="wide",
)

# ----------------- 中文字型載入處理 -----------------
def get_chinese_font(size: int):
    """依序尋找可用的中文字型；Streamlit Cloud 需搭配 packages.txt 安裝 fonts-noto-cjk。"""
    font_candidates = [
        # Windows
        "C:/Windows/Fonts/msjh.ttc",
        "C:/Windows/Fonts/msjhbd.ttc",
        "C:/Windows/Fonts/mingliu.ttc",
        "msjh.ttc",
        # macOS
        "/System/Library/Fonts/PingFang.ttc",
        "/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        # Linux / Streamlit Cloud (fonts-noto-cjk)
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/arphic/uming.ttc",
    ]
    for path in font_candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    # 最後退路：至少不讓程式崩潰（英數字仍可顯示）
    for fallback in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "DejaVuSans.ttf",
        "arial.ttf",
    ):
        try:
            return ImageFont.truetype(fallback, size)
        except Exception:
            continue
    return ImageFont.load_default()


# ----------------- 排盤核心演算法 -----------------
STEMS = "甲乙丙丁戊己庚辛壬癸"
BRANCHES = "子丑寅卯辰巳午未申酉戌亥"
STEM_ELEMENTS = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
}
BRANCH_ELEMENTS = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
    "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水",
}
STEM_RESIDENCES = {
    "甲": "寅", "乙": "辰", "丙": "巳", "丁": "未", "戊": "巳",
    "己": "未", "庚": "申", "辛": "戌", "壬": "亥", "癸": "丑",
}
CONTROLS = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
GENERATES = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}


def get_relative(day_stem: str, target_branch: str) -> str:
    s_ele = STEM_ELEMENTS[day_stem]
    b_ele = BRANCH_ELEMENTS[target_branch]
    if b_ele == s_ele:
        return "兄弟"
    if CONTROLS[b_ele] == s_ele:
        return "官鬼"
    if CONTROLS[s_ele] == b_ele:
        return "妻財"
    if GENERATES[b_ele] == s_ele:
        return "父母"
    return "子孫"


def calculate_chart(d: date, t: time, division: str, is_lunar: bool = False):
    if is_lunar:
        lunar = Lunar.fromYmdHms(d.year, d.month, d.day, t.hour, t.minute, 0)
        solar = lunar.getSolar()
    else:
        solar = Solar.fromYmdHms(d.year, d.month, d.day, t.hour, t.minute, 0)
        lunar = solar.getLunar()

    ganzhi = (
        f"{lunar.getYearInGanZhi()}年 {lunar.getMonthInGanZhi()}月 "
        f"{lunar.getDayInGanZhi()}日 {lunar.getTimeInGanZhi()}時"
    )
    lunar_str = (
        f"{lunar.getYearInChinese()}年 {lunar.getMonthInChinese()}月 "
        f"{lunar.getDayInChinese()}日 {lunar.getTimeInGanZhi()[-1]}時"
    )

    m_branch = lunar.getMonthInGanZhi()[-1]
    m_to_jiang = {
        "寅": "亥", "卯": "戌", "辰": "酉", "巳": "申", "午": "未", "未": "午",
        "申": "巳", "酉": "辰", "戌": "卯", "亥": "寅", "子": "丑", "丑": "子",
    }
    jiang = m_to_jiang[m_branch]

    day_pair = lunar.getDayInGanZhi()
    day_idx = next(i for i in range(60) if STEMS[i % 10] + BRANCHES[i % 12] == day_pair[:2])
    xun_start = day_idx - (day_idx % 10)
    day_void = f"{BRANCHES[(xun_start + 10) % 12]}、{BRANCHES[(xun_start + 11) % 12]}"

    hour_pair = lunar.getTimeInGanZhi()
    hour_idx = next(i for i in range(60) if STEMS[i % 10] + BRANCHES[i % 12] == hour_pair[:2])
    hxun_start = hour_idx - (hour_idx % 10)
    hour_void = f"{BRANCHES[(hxun_start + 10) % 12]}、{BRANCHES[(hxun_start + 11) % 12]}"

    day_stem, day_branch = day_pair[0], day_pair[1]
    hour_branch = hour_pair[1]

    offset = (BRANCHES.index(jiang) - BRANCHES.index(hour_branch)) % 12
    heaven_plate = {earth: BRANCHES[(BRANCHES.index(earth) + offset) % 12] for earth in BRANCHES}

    d_resi = STEM_RESIDENCES[day_stem]
    four_lessons = [
        {"label": "一課", "top": heaven_plate[d_resi], "bottom": day_stem},
        {"label": "二課", "top": heaven_plate[heaven_plate[d_resi]], "bottom": heaven_plate[d_resi]},
        {"label": "三課", "top": heaven_plate[day_branch], "bottom": day_branch},
        {"label": "四課", "top": heaven_plate[heaven_plate[day_branch]], "bottom": heaven_plate[day_branch]},
    ]

    day_guides = {
        "甲": "丑", "戊": "丑", "庚": "丑", "乙": "子", "己": "子",
        "丙": "亥", "丁": "亥", "辛": "午", "壬": "巳", "癸": "巳",
    }
    night_guides = {
        "甲": "未", "戊": "未", "庚": "未", "乙": "申", "己": "申",
        "丙": "酉", "丁": "酉", "辛": "寅", "壬": "卯", "癸": "卯",
    }
    noble = (day_guides if division == "晝占" else night_guides)[day_stem]
    noble_idx = BRANCHES.index(noble)
    general_names = [
        "貴神", "螣蛇", "朱雀", "六合", "勾陳", "青龍",
        "天空", "白虎", "太常", "玄武", "太陰", "天后",
    ]

    generals = {}
    for hb in BRANCHES:
        generals[hb] = general_names[(BRANCHES.index(hb) - noble_idx) % 12]

    for item in four_lessons:
        item["general"] = generals[item["top"]]

    lowers = [
        l for l in four_lessons
        if CONTROLS[STEM_ELEMENTS.get(l["bottom"], BRANCH_ELEMENTS.get(l["bottom"]))] == BRANCH_ELEMENTS[l["top"]]
    ]
    uppers = [
        l for l in four_lessons
        if CONTROLS[BRANCH_ELEMENTS[l["top"]]] == STEM_ELEMENTS.get(l["bottom"], BRANCH_ELEMENTS.get(l["bottom"]))
    ]

    if lowers:
        first = lowers[0]["bottom"]
        if first in STEM_ELEMENTS:
            first = STEM_RESIDENCES[first]
    elif uppers:
        first = uppers[0]["top"]
    else:
        first = heaven_plate["巳"]

    second = heaven_plate[first]
    third = heaven_plate[second]

    transmissions = [
        {"rank": "初傳", "branch": first, "general": generals[first], "relative": get_relative(day_stem, first)},
        {"rank": "中傳", "branch": second, "general": generals[second], "relative": get_relative(day_stem, second)},
        {"rank": "末傳", "branch": third, "general": generals[third], "relative": get_relative(day_stem, third)},
    ]

    plate_full = [
        {"heaven": heaven_plate[e], "earth": e, "general": generals[heaven_plate[e]]}
        for e in BRANCHES
    ]

    meta_result = {
        "ganzhi": ganzhi,
        "lunar": lunar_str,
        "solar": f"{solar.getYear()} 年 {solar.getMonth()} 月 {solar.getDay()} 日 {t.hour} 時 {t.minute} 分",
        "jiang": jiang,
        "day_void": day_void,
        "hour_void": hour_void,
    }
    return meta_result, four_lessons, transmissions, plate_full


# ----------------- 產生 AI Prompt 函式 -----------------
def generate_ai_prompt(meta: dict, lessons: list, transmissions: list, plate_full: list) -> str:
    first, sec, third = transmissions
    four_lessons_str = "\n".join(
        [f"{l['label']}：{l['general']}、{l['top']}、{l['bottom']}" for l in lessons]
    )
    plate_str = "\n".join(
        [f"天盤{p['heaven']} + 地盤{p['earth']} + {p['general']}" for p in plate_full]
    )

    prompt = f"""※以下內容是根據目前大六壬日期所產生的相關問題提示詞，供 AI 分析使用。 請自行複製下面內容後，前往各 AI App (如: ChatGPT, Grok, DeepSeek...等) 對提示詞貼上進行提問，即可獲得個人化的分析結果。

註：以下內容僅為基本資訊，並作為展示 AI 提示詞的範例使用。

大六壬日期：
陽曆：{meta['solar']}
農曆：{meta['lunar']}
干支：{meta['ganzhi']}
占別：{meta['division']}
月將：{meta['jiang']}將
日空：{meta['day_void']}
時空：{meta['hour_void']}
檔案／姓名：{meta.get('name', '未提供')}
年命行年：{meta.get('year_life', '自填')}

【三傳】
初傳： {first['relative']}  {first['branch']}  {first['general']}
中傳： {sec['relative']}  {sec['branch']}  {sec['general']}
末傳： {third['relative']}  {third['branch']}  {third['general']}

【四課】
{four_lessons_str}

【天地盤及貴神】
{plate_str}

事由：{meta['question']}

【提問指引】
請用繁體中文回答，身為精通《畢法賦》、《大六壬大全》等古籍的大師，請依據上述四課式進行深度學理解析：
1. 針對事由選定對應用神，評估用神之旺相休囚與空破結構。
2. 解構三傳進程（初傳起因、中傳演變、末傳結尾歸宿）。
3. 針對具體問題（如失物地點、失蹤方向、人事糾紛），推算室內外方位、樓層層次、環境特徵與周遭物件。
4. 提供現實應對建議與轉機把握時機。"""
    return prompt


# ----------------- 繪圖函式 -----------------
def generate_mobile_style_chart(meta: dict, lessons: list, transmissions: list):
    w, h = 600, 1000
    img = Image.new("RGB", (w, h), color="#FFFFFF")
    draw = ImageDraw.Draw(img)

    font_title = get_chinese_font(20)
    font_sub = get_chinese_font(14)
    font_body = get_chinese_font(16)
    font_big = get_chinese_font(26)

    draw.rectangle([10, 10, w - 10, 120], outline="#CCCCCC", fill="#F8F9FA")
    draw.text((25, 20), f"大六壬檔案：{meta.get('name', '客戶起課')}", fill="#111827", font=font_title)
    draw.text((25, 55), f"陽曆：{meta['solar']}   農曆：{meta['lunar']}", fill="#4B5563", font=font_sub)
    draw.text((25, 85), f"干支：{meta['ganzhi']} （{meta['division']}・{meta['jiang']}將）", fill="#B91C1C", font=font_body)

    draw.rectangle([10, 130, w - 10, 175], outline="#F59E0B", fill="#FEF3C7")
    draw.text((25, 142), f"事由：{meta['question']}", fill="#92400E", font=font_body)

    draw.rectangle([10, 190, w - 10, 310], outline="#D1D5DB", fill="#F9FAFB")
    draw.text((25, 200), "【 三 傳 】", fill="#4B5563", font=font_sub)
    for i, tr in enumerate(transmissions):
        x = 45 + i * 180
        draw.rectangle([x, 225, x + 165, 295], outline="#9CA3AF", fill="#FFFFFF")
        draw.text((x + 12, 248), f"{tr['relative']}", fill="#059669", font=font_body)
        draw.text((x + 65, 240), f"{tr['branch']}", fill="#1D4ED8", font=font_big)
        draw.text((x + 112, 248), f"{tr['general']}", fill="#DC2626", font=font_body)

    draw.rectangle([10, 325, w - 10, 475], outline="#D1D5DB", fill="#F9FAFB")
    draw.text((25, 335), "【 四 課 】", fill="#4B5563", font=font_sub)
    for i, l in enumerate(reversed(lessons)):
        x = 30 + i * 140
        draw.rectangle([x, 360, x + 120, 460], outline="#9CA3AF", fill="#FFFFFF")
        draw.text((x + 40, 368), l["general"], fill="#DC2626", font=font_body)
        draw.text((x + 48, 395), l["top"], fill="#1D4ED8", font=font_big)
        draw.line([x + 25, 425, x + 95, 425], fill="#CCCCCC", width=1)
        draw.text((x + 48, 430), l["bottom"], fill="#111827", font=font_body)

    draw.rectangle([10, 490, w - 10, 530], fill="#EFF6FF")
    draw.text(
        (25, 502),
        f"日空：{meta['day_void']} ｜ 時空：{meta['hour_void']} ｜ 月將：{meta['jiang']}將",
        fill="#1E40AF",
        font=font_sub,
    )

    return img


# ----------------- Streamlit 介面渲染 -----------------
def main():
    st.title("玄機閣 · 大六壬起課")
    st.caption("輸入事由與時間後，系統自動排盤、繪製命盤並即時產出 AI Prompt。")

    col_form, col_display = st.columns([1, 1.2], gap="large")

    with col_form:
        name_input = st.text_input("檔案名稱 / 姓名", value="李建成")
        question_input = st.text_area("輸入事由", value="妻子離家出走在哪裡", height=70)
        note_input = st.text_input("備註（選填）", value="")

        r1_c1, r1_c2, r1_c3 = st.columns(3)
        with r1_c1:
            division = st.radio("占法", ["晝占", "夜占"], horizontal=True)
        with r1_c2:
            cal_type = st.radio("曆法", ["陽曆", "農曆"], horizontal=True)
        with r1_c3:
            year_life = st.text_input("行年 / 年命", value="自填")

        st.markdown("---")
        now = datetime.now()
        r2_c1, r2_c2 = st.columns(2)
        with r2_c1:
            input_date = st.date_input("日期", value=now.date())
        with r2_c2:
            input_time = st.time_input("時間", value=time(now.hour, now.minute))

        submit = st.button(
            "✅ 確認起課・生成命盤與 AI Prompt", type="primary", use_container_width=True
        )

    # 執行排盤計算：畫面載入或按下按鈕時皆重新計算，確保資料最新
    meta, lessons, transmissions, plate_full = calculate_chart(
        input_date, input_time, division, is_lunar=(cal_type == "農曆")
    )
    meta["name"] = name_input
    meta["question"] = question_input
    meta["division"] = division
    meta["year_life"] = year_life
    meta["note"] = note_input

    # 產出命盤圖片及 Prompt
    chart_img = generate_mobile_style_chart(meta, lessons, transmissions)
    ai_prompt_text = generate_ai_prompt(meta, lessons, transmissions, plate_full)

    with col_display:
        st.subheader("📱 自動生成之命盤圖片")
        st.image(chart_img, caption="系統根據上方設定自動推導繪製", use_container_width=True)

        img_byte = io.BytesIO()
        chart_img.save(img_byte, format="PNG")
        st.download_button(
            "📥 下載命盤圖片 (PNG)",
            data=img_byte.getvalue(),
            file_name="liuren_chart.png",
            mime="image/png",
            use_container_width=True,
        )

    # AI Prompt 固定渲染於網頁下方，不因重新計算而消失
    st.markdown("---")
    st.subheader("📋 系統自動生成之 AI 提示詞 (Prompt)")
    st.caption(
        "已將您排盤的結果完整轉為標準結構。請點選下方框格複製內容，"
        "貼入 ChatGPT、Grok 或 DeepSeek 進行分析："
    )

    st.text_area(
        label="AI Prompt（可全選複製）",
        value=ai_prompt_text,
        height=380,
    )

    st.download_button(
        label="📝 下載提示詞文字檔 (.txt)",
        data=ai_prompt_text,
        file_name="liuren_prompt.txt",
        mime="text/plain",
        use_container_width=True,
    )


if __name__ == "__main__":
    main()
