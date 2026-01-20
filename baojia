import streamlit as st
import pandas as pd

# ==========================================
# 1. 核心数据库 (在此处修改底价)
# ==========================================
# 格式：'景点名': [成人底价, 儿童底价(参考), '优惠备注']
SCENIC_DB = {
    "德天瀑布": [205, 75, "1.2m免, 1.2-1.5半"],
    "明仕骑行": [30, 30, "大小同价"],
    "古龙山漂流": [145, 60, "1m以下禁, 1-1.4半"],
    "旧州古镇": [100, 100, "大小同价"],
    "峒那屿湾": [100, 55, "1.2m免"],
    "白头叶猴": [85, 40, "1.2m免"],
    "鹅泉": [35, 24, "1.2m免"],
    "通灵大峡谷": [80, 50, "1.2m免, 1.2-1.4半"],
    "涠洲岛(票+船)": [400, 200, "1.2-1.5半(需核实)"],
    "BBQ/篝火": [70, 70, "按人头"],
    "观鲸": [220, 220, "大小同价"]
}

# 基础参数
PROFIT_RATE = 1.5  # 利润系数 (房/车/票)
BREAKFAST_UNIT = 68  # 早餐净价

# ==========================================
# 2. 页面布局与输入
# ==========================================
st.set_page_config(page_title="鲸鱼旅游精算师", page_icon="🐳")

st.title("🐳 鲸鱼旅游报价精算器")
st.markdown("**(V3.6 标准分摊版)**")

# --- 侧边栏：基础成本输入 ---
with st.sidebar:
    st.header("1. 基础硬成本 (底价)")
    car_total_price = st.number_input("🚗 车辆总底价 (元)", value=2000, step=100)
    hotel_unit_price = st.number_input("🏨 酒店单间底价 (元/晚)", value=700, step=50)
    
    st.header("2. 团队配置")
    room_count = st.number_input("🔑 房间数", value=2, min_value=1)
    nights = st.number_input("🌙 入住晚数", value=1, min_value=1)

# --- 主界面：人员与景点 ---
st.subheader("1. 人员结构")
col1, col2, col3 = st.columns(3)
with col1:
    adults = st.number_input("👨 成人 (18岁+)", value=2, min_value=1)
with col2:
    big_kids = st.number_input("👦 大童 (5-17岁)", value=1, min_value=0, help="需分摊车费、补早餐、买儿童票")
with col3:
    toddlers = st.number_input("👶 幼儿 (≤4岁)", value=0, min_value=0, help="全免：不占床不分摊不买票")

st.subheader("2. 景点积木 (勾选行程)")
# 创建多选框
all_scenics = list(SCENIC_DB.keys())
selected_scenics = st.multiselect("请选择要去的地方：", all_scenics, default=["德天瀑布"])

# ==========================================
# 3. V3.6 核心精算逻辑
# ==========================================

# A. 人数定义
pay_pax = adults + big_kids # 计费人数 (剔除幼儿)
if pay_pax == 0:
    st.stop() # 防止除以0

# B. 车费计算 (人人均摊)
total_car_cost_with_profit = car_total_price * PROFIT_RATE
avg_car = total_car_cost_with_profit / pay_pax

# C. 房费计算 (仅成人承担)
total_hotel_cost_with_profit = hotel_unit_price * room_count * nights * PROFIT_RATE
avg_hotel = total_hotel_cost_with_profit / adults

# D. 早餐补差 (精准配额)
total_eaters = pay_pax # 只有付钱的人才算早餐人头，幼儿蹭饭
included_bk = room_count * 2 # 房间自带
need_extra_bk = max(0, total_eaters - included_bk) # 需要补几份
total_bk_cost = need_extra_bk * BREAKFAST_UNIT * nights # 总补差金额

# 早餐分摊逻辑：平均分摊给所有大童 (如果没有大童，就分摊给成人)
if big_kids > 0:
    avg_bk_per_kid = total_bk_cost / big_kids
    avg_bk_per_adult = 0
else:
    avg_bk_per_kid = 0
    avg_bk_per_adult = total_bk_cost / adults

# E. 门票计算 (积木叠加)
adult_ticket_sum = 0
kid_ticket_sum = 0

for item in selected_scenics:
    base_adult = SCENIC_DB[item][0]
    base_kid = SCENIC_DB[item][1]
    
    adult_ticket_sum += base_adult * PROFIT_RATE
    kid_ticket_sum += base_kid * PROFIT_RATE

# ==========================================
# 4. 输出报价单
# ==========================================
st.markdown("---")
st.subheader("💰 最终精算报价")

# 准备数据展示
col_a, col_b, col_c = st.columns(3)

# --- 成人报价 ---
final_adult_price = avg_hotel + avg_car + adult_ticket_sum + avg_bk_per_adult
with col_a:
    st.success(f"成人报价\n# ¥ {int(final_adult_price)}")
    st.caption(f"房费: {int(avg_hotel)}")
    st.caption(f"车费: {int(avg_car)}")
    st.caption(f"门票: {int(adult_ticket_sum)}")
    if avg_bk_per_adult > 0:
        st.caption(f"补早: {int(avg_bk_per_adult)}")

# --- 大童报价 ---
final_kid_price = avg_car + kid_ticket_sum + avg_bk_per_kid
with col_b:
    st.info(f"大童报价\n# ¥ {int(final_kid_price)}")
    st.caption(f"房费: ¥ 0")
    st.caption(f"车费: {int(avg_car)}")
    st.caption(f"门票: {int(kid_ticket_sum)}")
    st.caption(f"补早: {int(avg_bk_per_kid)}")

# --- 幼儿报价 ---
with col_c:
    st.warning(f"幼儿报价\n# ¥ 0")
    st.caption("全免熔断")

# --- 详细明细折叠区 ---
with st.expander("查看详细计算过程 (内部核对)"):
    st.write(f"**1. 基础参数**：{adults}大 {big_kids}小 {toddlers}幼，共住 {room_count} 间房 {nights} 晚。")
    st.write(f"**2. 早餐判定**：付费 {pay_pax} 人，含早 {included_bk} 份，需补 {need_extra_bk} 份。总补费 {total_bk_cost} 元。")
    st.write(f"**3. 车费池**：底价 {car_total_price} x 1.5 = {total_car_cost_with_profit} ÷ {pay_pax}人 = {int(avg_car)}/人。")
    st.write(f"**4. 房费池**：底价 {hotel_unit_price} x {room_count}间 x {nights}晚 x 1.5 = {total_hotel_cost_with_profit} ÷ {adults}成人 = {int(avg_hotel)}/人。")
    st.write("**5. 选中景点明细**：")
    for item in selected_scenics:
        st.write(f"- {item}: 成人底价{SCENIC_DB[item][0]} / 儿童底价{SCENIC_DB[item][1]}")

