import re
import xml.etree.ElementTree as ET

def clean(text):
    return re.sub(r"\s+", "", text or "")

def highlight(text, terms):
    if not text:
        return ""
    for term in terms:
        if term in text:
            text = text.replace(term, f"<span style='color:red'>{term}</span>")
    return text

def match_logic(text, terms):
    cleaned = clean(text)
    include = [t for t in terms if not t.startswith('-') and t in cleaned]
    exclude = [t[1:] for t in terms if t.startswith('-')]

    print(f"[DEBUG] ▶ 검사 중 텍스트: {cleaned}")
    print(f"[DEBUG] ▶ 포함 조건: {include}")
    print(f"[DEBUG] ▶ 제외 조건: {exclude}")

    return all(i in cleaned for i in include) and not any(e in cleaned for e in exclude)

def parse_law_xml(xml_data, terms, unit):
    tree = ET.fromstring(xml_data)
    articles = tree.findall(".//조문")

    print(f"[DEBUG] ▶ 총 조문 수: {len(articles)}")
    print(f"[DEBUG] ▶ 검색 단위: {unit}")
    print(f"[DEBUG] ▶ 검색어 terms: {terms}")

    results = []

    for article in articles:
        jo = article.findtext("조번호", "").strip()
        title = article.findtext("조문제목", "") or ""
        content = article.findtext("조문내용", "") or ""
        항들 = article.findall("항")

        조출력 = False
        항목들 = []

        # 조 단위 매칭
        if unit == "조" and match_logic(title + content, terms):
            조출력 = True

        # 항 단위 매칭
        for 항 in 항들:
            항번호 = 항.findtext("항번호", "").strip()
            항내용 = 항.findtext("항내용", "") or ""

            text_to_check = 항내용

            # 호 + 목 내용 포함
            for 호 in 항.findall("호"):
                text_to_check += 호.findtext("호내용", "") or ""
                for 목 in 호.findall("목"):
                    text_to_check += 목.findtext("목내용", "") or ""

            if unit == "항" and match_logic(text_to_check, terms):
                조출력 = True

            항목들.append((항번호, text_to_check))

        # 법률 단위는 모든 항목 포함 여부 확인
        if unit == "법률":
            for _, text in 항목들:
                if match_logic(text, terms):
                    조출력 = True
                    break

        if 조출력:
            html = f"<b>제{jo}조 {title}</b><br>"
            for 항번호, text in 항목들:
                if match_logic(text, terms):
                    html += f"  ⓞ{항번호} {highlight(text, terms)}<br>"
            results.append(html)

    return results

def filter_by_logic(parsed_laws, query, unit):
    terms = [t.strip() for t in re.split(r"[,&\-()]", query or "") if t.strip()]
    return parse_law_xml(parsed_laws, terms, unit)

