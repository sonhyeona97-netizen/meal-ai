import streamlit as st
import pandas as pd
import google.generativeai as genai

st.set_page_config(page_title="사내식당 식단 3초 검증기", layout="wide")

st.title("🔍 사내식당 조리실 충돌 및 색감 3초 검증기")
st.caption("엑셀 식단표를 업로드하거나 텍스트를 붙여넣으면, 조리 도구 과부하와 식판 색감 밸런스를 즉시 진단합니다.")

with st.sidebar:
    st.header("⚙ 환경 설정")
    api_key = st.text_input("Google Gemini API Key 입력", value="", type="password")

st.subheader("📋 식단 데이터 가져오기")
uploaded_file = st.file_uploader("📂 엑셀 식단표 파일 업로드 (.xlsx, .xls, .csv)", type=["xlsx", "xls", "csv"])

final_menu_text = ""

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.success("✅ 엑셀 식단표 파일을 성공적으로 불러왔습니다!")
        st.dataframe(df, use_container_width=True)
        final_menu_text = df.to_string(index=False)
    except Exception as e:
        st.error(f"엑셀 파일을 읽는 중 오류가 발생했습니다: {e}")
else:
    sample_text = """월: 백미밥, 시원한 콩나물국, LA 갈비찜, 상추&쌈무 쌈, 파채무침, 포기김치
화: 백미밥, 얼큰 소고기뭇국, 수제 매콤 등갈비찜, 계란찜, 청경채 겉절이, 포기김치
수: 백미밥, 양송이 크림수프, 수제 함박스테이크, 매시드 포테이토, 코울슬로 샐러드, 수제 피클
목: 흑미밥, 맑은 순두부국, 고등어 김치찜, 두부구이&양념장, 콩나물 무침, 포기김치
금: 백미밥, 황태해장국, 돈가스, 김말이 튀김, 단무지 무침, 포기김치"""
    final_menu_text = st.text_area("또는 식단표 텍스트를 직접 복사해서 붙여넣으세요:", value=sample_text, height=180)

if st.button("🚨 조리실 충돌 및 색감 검증 시작", type="primary", use_container_width=True):
    if not api_key:
        st.warning("사이드바에 Google Gemini API 키를 먼저 입력해 주세요.")
    elif not final_menu_text.strip():
        st.warning("검증할 식단 데이터가 없습니다.")
    else:
        try:
            genai.configure(api_key=api_key)
            target_model_name = None
            for m in genai.list_models():
                if "generateContent" in m.supported_generation_methods:
                    target_model_name = m.name
                    break
            if not target_model_name:
                target_model_name = "models/gemini-1.5-pro-latest"
                
            model = genai.GenerativeModel(target_model_name)
            
            prompt = f"""
당신은 베테랑 단체급식 총괄 조리장 겸 위생/공정 관리 전문가입니다.
아래 식단표 데이터를 분석하여 조리실 현장에서 발생할 수 있는 문제점을 날카롭게 검증하고 피드백을 제공하세요.

[검증 대상 식단표 데이터]:
{final_menu_text}

[필수 점검 항목]:
1. ⚠️ 조리 도구 및 공정 과부하 경고 (같은 날 튀김류 중복, 오븐/전 작업 과다, 전처리 과중 메뉴 동시 배치 등)
2. 🎨 식판 색감 및 밸런스 경고 (붉은색 계열 편중, 갈색/튀김 일색 등 시각적 단조로움)
3. 💡 개선 제안: 문제가 있는 요일의 메뉴를 어떤 반찬으로 교체하면 좋을지 구체적 대안 제시

[출력 형식]:
- 요일별 특이사항을 아이콘(⚠️, 🎨, ✅)과 함께 가독성 좋게 정리하고, 조화로운 날은 칭찬을 남겨주세요.
"""
            with st.spinner("조리실 동선과 식판 색감을 분석 중입니다..."):
                response = model.generate_content(prompt)
                st.subheader("🛠️ 조리실 검증 피드백 리포트")
                st.markdown(response.text)
        except Exception as e:
            st.error(f"검증 중 오류 발생: {e}")