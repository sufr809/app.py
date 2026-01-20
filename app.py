import streamlit as st

# ==========================================
# 1. 核心数据库
# ==========================================
SCENIC_DB = {
    "德天瀑布": [205, 75, ["德天", "跨国瀑布"]],
    "明仕骑行": [30, 30, ["骑行", "单车"]],
    "古龙山漂流": [145, 60, ["古龙山", "漂流"]],
    "旧州古镇": [100, 100, ["旧州"]],
    "峒那屿湾": [100, 55, ["峒那", "仙山"]],
    "白头叶猴": [85, 40, ["白头叶猴", "生态公园"]],
    "鹅泉": [35, 24, ["鹅泉"]],
    "通灵大峡谷": [80, 50, ["通灵"]],
    "涠洲岛(票+船)": [400, 0, ["涠洲", "鳄鱼山"]],
    "BBQ/篝火": [70, 70, ["篝火", "烧烤", "BBQ"]],
    "观鲸": [220, 220, ["观鲸"]],
    "仁寿源": [70, 48, ["仁寿源"]]
}

PROFIT_RATE = 1.5  # 利润系数
BREAKFAST_UNIT = 68  # 早餐净价

# ==========================================
# 2. 界面逻辑
# ==========================================
st.set_page_config(page_title="鲸鱼智能精算", page_icon="🐳")
st.title("🐳 鲸鱼旅游智能报价系统")

# --- 第一步：智能识别 ---
st.subheader("1. 粘贴行程 (自动识别)")
itinerary_text = st.text_area("请把微信里的行程/方案直接粘贴在这里：", height=100)

auto_selected = []
if itinerary_text:
    for name, data in SCENIC_DB.items():
        if any(kw in itinerary_text for kw in data[2]):
            auto_selected.append(name)

# --- 第二步：成本与人数 ---
with st.expander("2. 输入核心成本与人数", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        st.info("💰 硬成本输入")
        hotel_total_cost = st.number_input("🏨 酒店采购总价", value=0)
        car_total_cost = st.number_input("🚗 车辆采购总价", value=2000)
        room_count = st.number_input("🔑 房间数量", value=2)
        nights = st.number_input("🌙 入住晚数", value=1)
        
    with col2:
        st.warning("👨‍👩‍👧‍👦 团队结构")
        adults = st.number_input("👨 成人 (18岁+)", value=2, min_value=1)
        big_kids = st.number_input("👦 大童 (6-17岁)", value=1, min_value=0)
        toddlers = st.number_input("👶 幼儿 (6岁以下)", value=0, min_value=0)
        
        # === 核心开关 ===
        st.write("---")
        is_aa_mode = st.checkbox("特殊情况：按人头AA分摊？", value=False, help="勾选后，大童将分摊房费和车费。不勾选则全部由成人承担。")

# --- 第三步：景点核对 ---
st.subheader("3. 景点核对")
selected_scenics = st.multiselect("系统识别到的景点：", list(SCENIC_DB.keys()), default=auto_selected)

# ==========================================
# 3. 计算核心 (V4.4 家长兜底版)
# ==========================================
if st.button("🚀 开始精算报价", type="primary"):
    
    # === A. 早餐补差逻辑 (通用) ===
    total_people = adults + big_kids # 6岁以上人数
    included_bk = room_count * 2
    need_extra_bk = max(0, total_people - included_bk)
    total_bk_cost = need_extra_bk * BREAKFAST_UNIT * nights

    # === B. 门票叠加 (通用) ===
    adult_ticket_sum = 0
    kid_ticket_sum = 0
    scenic_names = []
    for item in selected_scenics:
        adult_ticket_sum += SCENIC_DB[item][0] * PROFIT_RATE
        kid_ticket_sum += SCENIC_DB[item][1] * PROFIT_RATE
        scenic_names.append(item)

    # === C. 房费与车费分摊 (根据模式切换) ===
    
    if not is_aa_mode:
        # 【默认模式：家长兜底】
        # 逻辑：房费、车费、早餐补差，全加在成人身上
        # 儿童只付：门票
        
        # 分摊基数：仅成人
        split_base = adults
        
        # 成人承担所有硬成本
        avg_hotel = (hotel_total_cost * PROFIT_RATE) / split_base
        avg_car = (car_total_cost * PROFIT_RATE) / split_base
        avg_bk_add_on = total_bk_cost / split_base # 早餐钱也给大人出
        
        # 最终单价
        final_adult = avg_hotel + avg_car + avg_bk_add_on + adult_ticket_sum
        final_kid = kid_ticket_sum # 孩子只剩门票钱
        
        # 用于展示的明细变量
        kid_car_cost = 0
        kid_room_cost = 0
        kid_bk_cost = 0
        
    else:
        # 【特殊模式：AA制分摊】
        # 逻辑：大家一起摊车费、房费
        
        split_base = adults + big_kids # 全员分摊
        
        if split_base == 0: st.stop()

        avg_hotel = (hotel_total_cost * PROFIT_RATE) / split_base
        avg_car = (car_total_cost * PROFIT_RATE) / split_base
        
        # 早餐费分摊给大童 (或者平摊，这里算在大童头上比较清晰)
        kid_bk_cost = total_bk_cost / big_kids if big_kids > 0 else 0
        avg_bk_add_on = 0 # 大人不用补，算孩子的

        final_adult = avg_hotel + avg_car + adult_ticket_sum
        final_kid = avg_hotel + avg_car + kid_bk_cost + kid_ticket_sum
        
        kid_car_cost = avg_car
        kid_room_cost = avg_hotel

    # ==========================================
    # 4. 生成话术
    # ==========================================
    st.markdown("---")
    st.success("✅ 精算完成！")
    
    quote_text = f"""【鲸鱼旅游 - 定制报价单】
------------------------
👥 团队：{adults}成人 + {big_kids}大童 + {toddlers}幼儿
📅 行程：{len(selected_scenics)}个景点 ({'、'.join(scenic_names)})
🏨 住宿：{room_count}间房 / {nights}晚
------------------------
💰 最终报价：
👨 成人：¥ {int(final_adult)} /人
   (含: 房{int(avg_hotel)} + 车{int(avg_car)} + 门票{int(adult_ticket_sum)} + 补早{int(avg_bk_add_on)})
   
👦 儿童(6岁+)：¥ {int(final_kid)} /人
   (含: 门票{int(kid_ticket_sum)} + 车{int(kid_car_cost)} + 房{int(kid_room_cost)})
   
👶 幼儿(6岁以下)：全免 (¥0)
------------------------
*价格已含行程策划、专属用车及服务费。
"""
    
    st.text_area("长按全选复制：", value=quote_text, height=350)
    
    with st.expander("🕵️‍♂️ 内部数据核对"):
        st.write(f"当前模式: {'特殊AA制' if is_aa_mode else '默认家长兜底'}")
        st.write(f"车房分摊人数: {split_base} 人")
        if not is_aa_mode:
            st.info("💡 提示：所有硬成本已转移至成人，儿童仅含门票。")
