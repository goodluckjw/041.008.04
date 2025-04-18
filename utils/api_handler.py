import re
import requests
import streamlit as st
from utils.xml_parser import parse_law_xml

OC = st.secrets["OC"]
API_KEY = st.secrets["API_KEY"]
BASE = "http://www.law.go.kr"

def fetch_law_list_and_detail(query, unit):
    from urllib.parse import quote

    keyword = re.split(r"[,&\-()]", query)[0].strip()
    encoded_query = quote(keyword)
    url = f"{BASE}/DRF/lawSearch.do?OC={OC}&APIKEY={API_KEY}&target=law&type=XML&display=10&search=2&knd=A0002&query={encoded_query}"

    res = requests.get(url)
    res.encoding = "utf-8"

    print(f"[DEBUG] ▶ 검색 요청 URL: {url}")
    print(f"[DEBUG] ▶ 응답 상태 코드: {res.status_code}")
    print(f"[DEBUG] ▶ 응답 본문 일부:\n{res.text[:500]}")

    if res.status_code != 200:
        return []

    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(res.content)
    except ET.ParseError:
        return []

    terms = [t.strip() for t in re.split(r"[,&\-()]", query or "") if t.strip()]
    results = []

    for law in root.findall("law"):
        name = law.findtext("법령명한글", "").strip()
        mst = law.findtext("법령일련번호", "").strip()
        detail = law.findtext("법령상세링크", "").strip()
        full_link = BASE + detail
        xml_data = fetch_law_xml_by_mst(mst)
        print(f"[DEBUG] ▶ {name} XML 본문 길이: {len(xml_data) if xml_data else 'None'}")

        if xml_data:
            articles = parse_law_xml(xml_data, terms, unit)
            if articles:
                results.append({
                    "법령명한글": name,
                    "원문링크": full_link,
                    "조문": articles
                })
    return results

def fetch_law_xml_by_mst(mst):
    url = f"{BASE}/DRF/lawService.do?OC={OC}&APIKEY={API_KEY}&target=law&type=XML&mst={mst}"
    res = requests.get(url)
    res.encoding = "utf-8"
    if res.status_code != 200:
        return None
    return res.text
