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
    "涠洲岛(票+船)": [400, 0, ["涠洲", "鳄鱼山"]], # 儿童票已设为0
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

# --- 第一步：智能识别区 ---
st.subheader("1. 粘贴行程 (自动识别)")
itinerary_text = st.text_area("请把微信里的行程/方案直接粘贴在这里：", height=100, placeholder="例如：D1 接机住明仕，D2 游览德天瀑布...")

# 自动分析
auto_selected = []
if itinerary_text:
    for name, data in SCENIC_DB.items():
        keywords = data[2]
        for kw in keywords:
            if kw in itinerary_text:
                auto_selected.append(name)
                break

# --- 第二步：成本与人数 ---
with st.expander("2. 输入核心成本与人数 (默认展开)", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        st.info("💰 硬成本输入")
        hotel_total_cost = st.number_input("🏨 酒店采购总价 (几间x几晚的总和)", value=0, help="例如：2间房住3晚，总共付给酒店的钱")
        car_total_cost = st.number_input("🚗 车辆采购总价 (全段车费)", value=2000)
        room_count = st.number_input("🔑 房间数量", value=2)
        nights = st.number_input("🌙 入住晚数", value=1)
        
    with col2:
        st.warning("👨‍👩‍👧‍👦 团队结构")
        adults = st.number_input("👨 成人 (18岁+)", value=2, min_value=1)
        # === 核心修改点：年龄分界线改为 6岁 ===
        big_kids = st.number_input("👦 大童 (6-17岁)", value=1, min_value=0, help="需分摊车费、补早餐")
        toddlers = st.number_input("👶 幼儿 (6岁以下)", value=0, min_value=0, help="6岁以下全免：不占床不分摊不买票")
        # ====================================
        
        st.write("---")
        special_room_split = st.checkbox("特殊情况：大童也分摊房费？", value=False, help="默认不勾选。只有当孩子单独占房且需付费时才勾选。")

# --- 第三步：景点核对 ---
st.subheader("3. 景点核对")
selected_scenics = st.multiselect("系统识别到的景点：", list(SCENIC_DB.keys()), default=auto_selected)

# ==========================================
# 3. 计算核心 (V4.3 6岁免费版)
# ==========================================
if st.button("🚀 开始精算报价", type="primary"):
    
    # A. 基础人数 (6岁以下不算在内)
    pay_pax = adults + big_kids 
    if pay_pax == 0: st.stop()

    # B. 房费计算 
    # 默认：成人承担。勾选特殊情况：成人+大童承担。
    hotel_split_pax = adults 
    if special_room_split:
        hotel_split_pax = adults + big_kids
    
    if hotel_split_pax == 0:
        avg_hotel = 0 
    else:
        avg_hotel = (hotel_total_cost * PROFIT_RATE) / hotel_split_pax

    # C. 车费计算 (成人 + 6岁以上大童均摊)
    avg_car = (car_total_cost * PROFIT_RATE) / pay_pax
    
    # D. 早餐补差
    included_bk = room_count * 2
    need_extra_bk = max(0, pay_pax - included_bk)
    total_bk_cost = need_extra_bk * BREAKFAST_UNIT * nights
    # 补差分摊给大童
    avg_bk = total_bk_cost / big_kids if big_kids > 0 else total_bk_cost / adults

    # E. 门票叠加
    adult_ticket_sum = 0
    kid_ticket_sum = 0
    scenic_names = []
    
    for item in selected_scenics:
        adult_ticket_sum += SCENIC_DB[item][0] * PROFIT_RATE
        kid_ticket_sum += SCENIC_DB[item][1] * PROFIT_RATE
        scenic_names.append(item)

    # F. 最终汇总
    final_adult = avg_hotel + avg_car + adult_ticket_sum
    
    # 大童总价
    kid_room_cost = avg_hotel if special_room_split else 0
    final_kid = kid_room_cost + avg_car + avg_bk + kid_ticket_sum
    
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
   (含: 房{int(avg_hotel)} + 车{int(avg_car)} + 门票{int(adult_ticket_sum)})
   
👦 儿童(6岁+)：¥ {int(final_kid)} /人
   (含: 房{int(kid_room_cost)} + 车{int(avg_car)} + 门票{int(kid_ticket_sum)} + 补早{int(avg_bk)})
   
👶 幼儿(6岁以下)：全免 (¥0)
------------------------
*价格已含行程策划、专属用车及服务费。
"""
    
    st.text_area("长按全选复制：", value=quote_text, height=350)
    
    with st.expander("🕵️‍♂️ 内部数据核对"):
        st.write(f"房费分摊人数: {hotel_split_pax} 人")
        st.write(f"车费分摊人数: {pay_pax} 人")
        st.info("✅ 政策已更新：6岁以下幼儿费用全免。")
# 3. 计算核心
# ==========================================
if st.button("🚀 开始精算报价", type="primary"):
    
    # A. 人数逻辑
    pay_pax = adults + big_kids # 计费人数
    
    if pay_pax == 0:
        st.error("人数不能为0")
        st.stop()

    # B. 硬成本分摊
    # 房费：总价 x 1.5 ÷ 成人 (儿童不摊房费)
    avg_hotel = (hotel_total_cost * PROFIT_RATE) / adults if adults > 0 else 0
    
    # 车费：总价 x 1.5 ÷ (成人+大童)
    avg_car = (car_total_cost * PROFIT_RATE) / pay_pax
    
    # 早餐：补差逻辑
    included_bk = room_count * 2
    need_extra_bk = max(0, pay_pax - included_bk)
    total_bk_cost = need_extra_bk * BREAKFAST_UNIT * nights
    # 分摊给大童
    avg_bk = total_bk_cost / big_kids if big_kids > 0 else total_bk_cost / adults

    # C. 门票叠加
    adult_ticket_sum = 0
    kid_ticket_sum = 0
    scenic_names = []
    
    for item in selected_scenics:
        adult_ticket_sum += SCENIC_DB[item][0] * PROFIT_RATE
        kid_ticket_sum += SCENIC_DB[item][1] * PROFIT_RATE
        scenic_names.append(item)

    # D. 最终汇总
    final_adult = avg_hotel + avg_car + adult_ticket_sum
    final_kid = avg_car + avg_bk + kid_ticket_sum
    
    # ==========================================
    # 4. 生成话术
    # ==========================================
    st.markdown("---")
    st.success("✅ 精算完成！请复制下方内容")
    
    quote_text = f"""【鲸鱼旅游 - 定制报价单】
------------------------
👥 团队：{adults}成人 + {big_kids}大童 + {toddlers}幼儿
📅 行程：{len(selected_scenics)}个景点 ({'、'.join(scenic_names)})
🏨 住宿：{room_count}间房 / {nights}晚
------------------------
💰 最终报价：
👨 成人：¥ {int(final_adult)} /人
   (含: 房{int(avg_hotel)} + 车{int(avg_car)} + 门票{int(adult_ticket_sum)})
   
👦 儿童(5岁+)：¥ {int(final_kid)} /人
   (含: 车{int(avg_car)} + 门票{int(kid_ticket_sum)} + 补早{int(avg_bk)})
   
👶 幼儿(4岁-)：全免 (¥0)
------------------------
*价格已含行程策划、专属用车及服务费。
"""
    
    st.text_area("长按全选复制：", value=quote_text, height=350)
    
    with st.expander("🕵️‍♂️ 查看内部核算底价 (机密)"):
        st.write(f"酒店采购总成本: {hotel_total_cost}")
        st.write(f"车辆采购总成本: {car_total_cost}")
        st.write(f"门票总成本(成人): {sum([SCENIC_DB[i][0] for i in selected_scenics])}")
