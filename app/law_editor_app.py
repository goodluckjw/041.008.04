import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from utils import xml_parser
from utils.api_handler import fetch_law_list_and_detail

parse_law_xml = xml_parser.parse_law_xml
filter_by_logic = xml_parser.filter_by_logic

st.set_page_config(layout="wide")
st.title("📘 부칙 개정 도우미")

st.markdown(
    '''
    법령 본문 중 검색어를 포함하는 조문을 찾아줍니다.

    **연산자 안내**
    `&` → AND (그리고), `,` → OR (또는), `-` → NOT (제외)

    **예시**
    `A & B , C - D` → (A와 B가 모두 포함되거나 C가 포함된 항) 중에서 D는 제외  
    `A & (B , C)` → (A가 포함) 그리고 (B 또는 C 포함)  
    `A , (B - C)` → (A 포함) 또는 (B가 포함되고 C 제외)
    '''
)

query = st.text_input("🔍 찾을 검색어 (다중 검색 지원)", placeholder="예: 지방법원,가정법원 -지원")
unit = st.radio("검색 단위", ["법률", "조", "항"], horizontal=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("법률 검색") and query:
        print(f"[DEBUG] 🔍 검색 버튼 클릭됨! query = {query}, unit = {unit}")
        with st.spinner(f"🔎 '{query}'을(를) 포함하는 조문을 검색 중입니다..."):
            results = fetch_law_list_and_detail(query, unit)
            for law in results:
                with st.expander(f"{law['법령명한글']}"):
                    st.markdown(f"[원문 보기]({law['원문링크']})", unsafe_allow_html=True)
                    for 조 in law["조문"]:
                        st.markdown(조, unsafe_allow_html=True)

with col2:
    if st.button("초기화"):
        st.rerun()
