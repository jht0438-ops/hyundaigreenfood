import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title='현대그린푸드 | 센트럴키친 원가분석',page_icon='🥗',layout='wide')
st.title('🥗 현대그린푸드 | 센트럴키친 원가절감 효과 분석기')
st.caption('생성형 AI 활용 구현 · 관리회계 시뮬레이션 · 실제 회사 내부 원가자료 아님')
st.info('**자료 구분:** 2026년 상반기 연결 매출 1조 2,165억원·영업이익 845억원은 첨부 심층분석보고서 및 공시 기반 참고치입니다. 아래 식수·단가·생산원가·가동률은 전부 분석용 가정이며 현대그린푸드 실제 내부 수치가 아닙니다.')
# 입력 가정은 모두 시뮬레이션용이며 실제 회사의 내부 원가가 아닙니다.
DEFAULTS = {
    'meals': 100000, 'field_mat': 2100, 'field_labor': 950,
    'field_other': 150, 'field_fixed': 18000000, 'ck_mat': 1900,
    'ck_labor': 330, 'ck_other': 190, 'ck_log': 280,
    'ck_field': 240, 'ck_fixed': 43000000,
}
SCENARIOS = ['기본 시나리오', '식수 변화 분석', '물류비 변화 분석']

def apply_scenario():
    """사용자가 지정한 기준값에 변화율을 적용해 분석 입력을 동기화한다."""
    mode = st.session_state.get('scenario', SCENARIOS[0])
    base_meals = st.session_state['base_meals']
    base_log = st.session_state['base_ck_log']
    meal_pct = st.session_state.get('meal_change_pct', 0) if mode == SCENARIOS[1] else 0
    log_pct = st.session_state.get('log_change_pct', 0) if mode == SCENARIOS[2] else 0
    st.session_state['input_meals'] = max(1000, round(base_meals * (1 + meal_pct / 100)))
    st.session_state['input_ck_log'] = max(0, round(base_log * (1 + log_pct / 100)))

def reset_inputs():
    st.session_state['scenario'] = SCENARIOS[0]
    st.session_state['meal_change_pct'] = 0
    st.session_state['log_change_pct'] = 0
    st.session_state['base_meals'] = DEFAULTS['meals']
    st.session_state['base_ck_log'] = DEFAULTS['ck_log']
    for key, value in DEFAULTS.items():
        st.session_state['input_' + key] = value

if 'scenario' not in st.session_state:
    st.session_state['scenario'] = SCENARIOS[0]
if 'meal_change_pct' not in st.session_state:
    st.session_state['meal_change_pct'] = 0
if 'log_change_pct' not in st.session_state:
    st.session_state['log_change_pct'] = 0
if 'base_meals' not in st.session_state:
    st.session_state['base_meals'] = DEFAULTS['meals']
if 'base_ck_log' not in st.session_state:
    st.session_state['base_ck_log'] = DEFAULTS['ck_log']
for key, value in DEFAULTS.items():
    if 'input_' + key not in st.session_state:
        st.session_state['input_' + key] = value
if 'applied_inputs' not in st.session_state:
    st.session_state['applied_inputs'] = DEFAULTS.copy()

with st.sidebar:
    st.header('⚙️ 분석 조건 설정')
    st.caption('① 기준값 입력 → ② 분석 유형 선택 → ③ 변화 조건 확인 → ④ 세부 원가 설정 → ⑤ 분석 실행')
    st.warning('초기 표시된 수치는 **설명용 가상 예시값**입니다. 현대그린푸드의 실제 식수·물류비가 아닙니다.', icon='ℹ️')

    st.subheader('STEP 1 · 기준값 입력')
    st.caption('분석을 시작하기 전에 비교의 출발점이 되는 값을 입력하세요.')
    st.number_input(
        '기준 월 공급 식수 (식/월)', min_value=1000, max_value=1000000,
        step=1000, key='base_meals', on_change=apply_scenario,
        help='변화가 발생하기 전 한 달 동안 공급하는 식사 수입니다. 최초 100,000식은 설명용 예시입니다.',
    )
    st.number_input(
        '기준 식수당 물류비 (원/식)', min_value=0, max_value=20000,
        step=10, key='base_ck_log', on_change=apply_scenario,
        help='변화가 발생하기 전 식사 한 끼당 배송·물류비입니다. 최초 280원은 설명용 예시입니다.',
    )
    st.caption('※ 실제 내부 자료가 있다면 위 예시값을 교체하세요. 물류비는 식수당 단가이며 월 물류비는 식수 × 단가로 계산합니다.')

    st.subheader('STEP 2 · 분석 유형 선택')
    scenario = st.radio(
        '어떤 상황을 분석할까요?', SCENARIOS,
        key='scenario', on_change=apply_scenario,
        help='STEP 1의 사용자 입력 기준값에 변화율을 적용합니다.',
    )
    if scenario == SCENARIOS[1]:
        st.slider('기준 대비 식수 변화율 (%)', min_value=-80, max_value=100,
                  step=5, key='meal_change_pct', on_change=apply_scenario,
                  help='STEP 1에서 입력한 기준 월 공급 식수에 적용합니다.')
    elif scenario == SCENARIOS[2]:
        st.slider('기준 대비 물류비 변화율 (%)', min_value=-80, max_value=200,
                  step=5, key='log_change_pct', on_change=apply_scenario,
                  help='STEP 1에서 입력한 기준 식수당 물류비에 적용합니다.')
    else:
        st.caption('변화율 없이 입력한 기준값 그대로 분석합니다.')
    st.caption('변화율은 사용자가 설정하는 민감도 분석 조건이며, 실제 회사의 전망치가 아닙니다.')

    st.subheader('STEP 3 · 적용값 확인')
    st.metric('분석에 적용되는 월 공급 식수', f"{st.session_state['input_meals']:,}식")
    st.metric('분석에 적용되는 식수당 물류비', f"{st.session_state['input_ck_log']:,}원/식")
    st.caption(f"월 물류비 합계: {st.session_state['input_meals'] * st.session_state['input_ck_log']:,}원 (식수 × 식수당 물류비)")
    st.caption('적용값은 STEP 1의 기준값과 STEP 2의 변화율로 자동 계산되므로 중복 입력하지 않습니다.')

    st.subheader('STEP 4 · 세부 원가 (선택)')
    st.caption('처음에는 수정하지 않아도 됩니다. 원가 구조를 직접 검토할 때만 펼쳐주세요.')
    with st.expander('🏠 기존 현장 조리 방식의 비용', expanded=False):
        st.caption('식사 1개를 현장에서 직접 조리하는 경우')
        st.number_input('식재료 구매비 (원/식)', 0, 20000, step=50, key='input_field_mat', help='식사 한 개에 투입되는 식재료의 구매원가')
        st.number_input('현장 조리 인건비 (원/식)', 0, 20000, step=50, key='input_field_labor', help='현장 조리 인력의 식사 한 개당 인건비')
        st.number_input('기타 변동비 (원/식)', 0, 20000, step=50, key='input_field_other', help='식수가 늘어날수록 함께 증가하는 기타 비용')
        st.number_input('월 고정비 (원/월)', 0, 1000000000, step=1000000, key='input_field_fixed', help='식수와 무관하게 매월 발생하는 임차료·설비비 등의 가정액')
    with st.expander('🏭 센트럴키친(중앙생산) 방식의 비용', expanded=False):
        st.caption('중앙시설에서 가공해 현장에 공급하는 경우')
        st.number_input('중앙생산 식재료비 (원/식)', 0, 20000, step=50, key='input_ck_mat', help='중앙시설에서 식사 한 개 분량을 생산할 때의 표준 식재료비')
        st.number_input('중앙생산 인건비 (원/식)', 0, 20000, step=10, key='input_ck_labor', help='중앙시설의 식사 한 개당 직접 인건비')
        st.number_input('포장·가공 변동비 (원/식)', 0, 20000, step=10, key='input_ck_other', help='포장재 및 가공 과정에서 발생하는 식사 한 개당 변동비')
        st.caption('배송·물류비는 STEP 1의 기준값과 STEP 2의 변화율에서 설정합니다. STEP 3에서 적용값을 확인하세요.')
        st.number_input('현장 마무리 조리비 (원/식)', 0, 20000, step=10, key='input_ck_field', help='중앙생산 후 현장에서 재가열·배식 등을 위해 발생하는 비용')
        st.number_input('중앙시설 월 고정비 배부액 (원/월)', 0, 1000000000, step=1000000, key='input_ck_fixed', help='중앙시설의 설비비·감가상각비 등에서 해당 분석 대상에 배분한 월 고정비')

    col_run, col_reset = st.columns([2, 1])
    with col_run:
        if st.button('📊 분석 실행', type='primary', use_container_width=True):
            st.session_state['applied_inputs'] = {k: st.session_state['input_' + k] for k in DEFAULTS}
            st.session_state['applied_scenario'] = st.session_state['scenario']
            st.toast('입력한 조건을 분석에 반영했습니다.')
    with col_reset:
        if st.button('↺ 초기화', use_container_width=True):
            reset_inputs()
            st.session_state['applied_inputs'] = DEFAULTS.copy()
            st.session_state['applied_scenario'] = '기본 시나리오'
            st.rerun()
    st.caption('STEP 5 · 분석 실행: 버튼을 누르기 전에는 기존 결과가 유지됩니다.')

inputs = st.session_state['applied_inputs']
meals = inputs['meals']
field_mat, field_labor = inputs['field_mat'], inputs['field_labor']
field_other, field_fixed = inputs['field_other'], inputs['field_fixed']
ck_mat, ck_labor = inputs['ck_mat'], inputs['ck_labor']
ck_other, ck_log = inputs['ck_other'], inputs['ck_log']
ck_field, ck_fixed = inputs['ck_field'], inputs['ck_fixed']
st.caption(f"현재 분석에 적용된 월 공급 식수: **{meals:,}식** · 세부 원가 단위: 원/식, 고정비는 원/월")
if any(st.session_state['input_' + k] != inputs[k] for k in DEFAULTS):
    st.info('왼쪽 입력값이 변경되었습니다. **분석 실행**을 눌러 결과에 반영하세요.')

field_var=field_mat+field_labor+field_other
ck_var=ck_mat+ck_labor+ck_other+ck_log+ck_field
field_total=meals*field_var+field_fixed
ck_total=meals*ck_var+ck_fixed
saving=field_total-ck_total
field_unit=field_total/meals
ck_unit=ck_total/meals

tabs=st.tabs(['① 종합진단','② 전환 전후 원가 비교','③ 원가 차이 분석','④ 손익분기점·민감도','⑤ 재경 개선과제·출처'])
with tabs[0]:
 st.subheader('왜 분석하는가?')
 st.write('중앙생산은 현장 인건비를 줄일 수 있지만, 중앙설비 고정비와 배송비가 새로 발생합니다. 총원가 기준으로 전환의 경제성을 검토합니다.')
 st.subheader('어떻게 분석하는가?')
 st.write('현장조리와 CK 방식의 월 총원가 및 식당 원가를 동일 식수에서 비교합니다. 공통비는 배부액으로 가정합니다.')
 a,b,c,d=st.columns(4)
 a.metric('현장 식당 원가',f'{field_unit:,.0f}원')
 b.metric('CK 식당 원가',f'{ck_unit:,.0f}원',f'{field_unit-ck_unit:+,.0f}원 절감',delta_color='inverse')
 c.metric('월 절감액',f'{saving/10000:,.1f}만원')
 d.metric('원가 절감률',f'{saving/field_total*100:.2f}%' if field_total else 'N/A')
 st.plotly_chart(px.bar(pd.DataFrame({'방식':['현장 조리','CK 중앙생산'],'월 총원가(원)':[field_total,ck_total]}),x='방식',y='월 총원가(원)',text_auto=',.0f',title='동일 식수 기준 월 총원가'),use_container_width=True)
 st.subheader('결론')
 st.success('현재 입력한 가정에서는 CK 전환이 원가 절감에 유리합니다.' if saving>0 else '현재 입력한 가정에서는 CK 전환이 비용 측면에서 불리하거나 동일합니다.')
 st.caption('주의: 이 결론은 입력한 가정에만 해당하며, 실제 회사의 전환 성과나 인과관계를 입증하지 않습니다.')
with tabs[1]:
 st.subheader('왜 분석하는가?')
 st.write('비용의 단순 감소뿐 아니라 현장에서 중앙센터·물류로 비용이 이동한 효과까지 확인해야 합니다.')
 st.subheader('어떻게 분석하는가?')
 detail=pd.DataFrame({'원가항목':['원재료','인건비','가공·기타 변동비','물류비','현장 마무리비','고정비 배부'], '현장 조리(원/식)':[field_mat,field_labor,field_other,0,0,field_fixed/meals], 'CK 전환(원/식)':[ck_mat,ck_labor,ck_other,ck_log,ck_field,ck_fixed/meals]})
 detail['차이(현장-CK)']=detail['현장 조리(원/식)']-detail['CK 전환(원/식)']
 st.dataframe(detail.style.format({x:'{:,.1f}' for x in detail.columns[1:]}),use_container_width=True,hide_index=True)
 fig=go.Figure()
 fig.add_bar(name='현장 조리',x=detail['원가항목'],y=detail['현장 조리(원/식)'])
 fig.add_bar(name='CK 전환',x=detail['원가항목'],y=detail['CK 전환(원/식)'])
 fig.update_layout(barmode='group',yaxis_title='원/식')
 st.plotly_chart(fig,use_container_width=True)
 st.subheader('결론')
 st.write('양(+)의 차이는 CK 전환 시 절감되는 비용, 음(-)의 차이는 CK 전환 시 추가되는 비용입니다. 총합은 식당 절감액과 일치합니다.')
with tabs[2]:
 st.subheader('왜 분석하는가?')
 st.write('실제 원재료비가 표준보다 높을 때 가격 상승 때문인지, 투입량 초과 때문인지 분리해야 개선 담당 부서를 정할 수 있습니다.')
 st.subheader('어떻게 분석하는가?')
 st.caption('아래 값은 CK 원재료 한 식분의 가상 표준/실제 투입량 및 구매단가입니다. 총액과 달리 원재료 가격·수량 차이를 정확히 분해합니다.')
 p,q,r=st.columns(3)
 with p: std_qty=st.number_input('표준 투입량 (kg/식)',0.01,10.0,0.50,0.01)
 with q: act_qty=st.number_input('실제 투입량 (kg/식)',0.01,10.0,0.53,0.01)
 with r: act_price=st.number_input('실제 구매단가 (원/kg)',0.0,100000.0,4000.0,100.0)
 std_price=ck_mat/std_qty
 price_var=(act_price-std_price)*act_qty*meals
 usage_var=(act_qty-std_qty)*std_price*meals
 total_var=price_var+usage_var
 st.metric('가격차이 (양수=불리)',f'{price_var/10000:+,.1f}만원')
 st.metric('수량차이 (양수=불리)',f'{usage_var/10000:+,.1f}만원')
 st.metric('총 원재료 차이',f'{total_var/10000:+,.1f}만원')
 st.latex(r'\text{가격차이}=(AP-SP)\times AQ,\quad \text{수량차이}=(AQ-SQ)\times SP')
 st.write(f'표준원가 {ck_mat:,.0f}원/식, 실제 원가 {act_qty*act_price:,.0f}원/식, 차이 {act_qty*act_price-ck_mat:+,.0f}원/식')
 st.subheader('결론')
 st.write('가격차이가 불리하면 구매단가·계약조건을, 수량차이가 불리하면 폐기율·수율·레시피 준수를 우선 점검합니다. 표준/실제 투입량이 공개되지 않아 실제 성과로 해석할 수 없습니다.')
with tabs[3]:
 st.subheader('왜 분석하는가?')
 st.write('CK는 고정비가 상대적으로 높을 수 있어 공급 식수가 충분할 때만 경제적일 수 있습니다.')
 st.subheader('어떻게 분석하는가?')
 diff=field_var-ck_var
 fixed_gap=ck_fixed-field_fixed
 if diff>0:
  threshold=max(0,fixed_gap/diff)
  st.metric('CK가 유리해지는 월 식수 임계치',f'{threshold:,.0f}식')
 else:
  st.warning('현재 가정에서 CK 식당 변동비가 현장 조리보다 낮지 않습니다. 단순한 양(+) 손익분기 식수는 성립하지 않을 수 있습니다.')
 values=sorted(set([max(1000,int(meals*x)) for x in [0.25,0.5,0.75,1,1.25,1.5,2]]))
 chart=pd.DataFrame({'월 식수':values,'현장 조리':[v*field_var+field_fixed for v in values],'CK 중앙생산':[v*ck_var+ck_fixed for v in values]})
 st.plotly_chart(px.line(chart,x='월 식수',y=['현장 조리','CK 중앙생산'],labels={'value':'월 총원가(원)','variable':'방식'},markers=True),use_container_width=True)
 st.write('**민감도: CK 물류비와 공급 식수 변화에 따른 월 절감액(만원)**')
 st.caption('아래 70%·100%·130% 식수는 계산 구조를 보여주기 위한 예시 구간입니다. 실제 수요 전망은 아닙니다.')
 scenarios=[]
 for m in [0.7,1.0,1.3]:
  row={'식수 변화':f'{m:.0%}'}
  for delta in [-100,0,100,200]:
   v=meals*m
   row[f'물류비 {delta:+}원']=(v*field_var+field_fixed-v*(ck_var+delta)-ck_fixed)/10000
  scenarios.append(row)
 st.dataframe(pd.DataFrame(scenarios).style.format({k:'{:,.1f}' for k in scenarios[0] if k!='식수 변화'}),use_container_width=True,hide_index=True)
 st.subheader('결론')
 st.write('수요가 낮거나 배송비가 증가할 때 절감 효과가 줄어드는지 확인하여, CK 전환 대상 사업장과 물류 동선을 선별하는 데 활용할 수 있습니다.')
with tabs[4]:
 st.subheader('왜 분석하는가?')
 st.write('원가분석을 실제 관리 의사결정에 연결하기 위해, 원인별 확인자료와 후속 조치를 정리합니다.')
 st.subheader('어떻게 분석하는가?')
 tasks=pd.DataFrame([
  ['CK 전환 경제성','사업장별 월 식수·메뉴 구성·배송거리','식수당 총원가 비교 후 전환 우선순위 설정'],
  ['원재료 가격차이','구매계약단가·입고가격·품목별 구매량','단가 인상 원인과 구매 조건 재검토'],
  ['원재료 수량차이','레시피 표준량·실제 투입량·폐기량','수율·폐기율 개선 대상 선정'],
  ['고정비 배부','CK 설비 감가상각·가동시간·공급량','공통비 배부 기준 검증'],
  ['내부거래·결산','CK 공급 내역·사업장 입고·부문간 거래','내부거래 대사 및 연결 제거 확인'],
 ],columns=['관리과제','추가 확보 자료','재경 담당자 행동'])
 st.dataframe(tasks,use_container_width=True,hide_index=True)
 st.subheader('결론')
 st.write('원가 절감액을 단정하는 대신, 내부 자료 확보 → 원가 차이 분해 → 배부기준 검증 → 사업장별 전환 판단 순으로 재경 관리체계를 설계합니다.')
 st.divider()
 st.markdown('**근거 자료와 한계**')
 st.markdown('- 현대그린푸드 2026년 반기보고서(2026.08.14), 연결재무제표 및 영업부문 주석\n- 현대그린푸드 2025년 사업보고서(2026.03.16)\n- 첨부 「26하 현대그린푸드 재경 심층분석보고서」 1장·5장\n- 2026.08.04 한스경제, 「현대그린푸드, 2분기 영업이익 23%↑」')
 st.warning('공시에서 센트럴키친 전환 전후 사업장별 원가, 식수, 고정비 배부액을 직접 확인할 수 없습니다. 시뮬레이션의 입력값·절감액·손익분기점은 실제 현대그린푸드 실적이 아니라 가상 사례입니다. 투자·회계 의사결정에는 검증된 내부 자료가 필요합니다.')
