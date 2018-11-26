import re

TITLES = [
    "表紙",
    "第一部 ファンド情報",
    "第１ ファンドの状況",
    "１ 投資法人の概況",
    "(1) 主要な経営指標等の推移",
    "(2) 投資法人の目的及び基本的性格",
    "(3) 投資法人の仕組み",
    "(4) 投資法人の機構",
    "(5) 投資法人の出資総額",
    "(6) 主要な投資主の状況",
    "(7) 資産運用会社従業員等投資口所有制度の内容",
    "２ 投資方針",
    "(1) 投資方針",
    "(2) 投資対象",
    "(3) 分配方針",
    "(4) 投資制限",
    "３ 投資リスク",
    "４ 手数料等及び税金",
    "(1) 申込手数料",
    "(2) 買戻し手数料",
    "(3) 管理報酬等",
    "(4) その他の手数料等",
    "(5) 課税上の取扱い",
    "５ 運用状況",
    "(1) 投資状況",
    "(2) 投資資産",
    "① 投資有価証券の主要銘柄",
    "② 投資不動産物件",
    "③ その他投資資産の主要なもの",
    "(3) 運用実績",
    "① 純資産等の推移",
    "② 分配の推移",
    "③ 自己資本利益率（収益率）の推移",
    "第二部 投資法人の詳細情報",
    "第１ 投資法人の追加情報",
    "１ 投資法人の沿革",
    "２ 役員の状況",
    "３ その他",
    "第２ 手続等",
    "１ 申込（販売）手続等",
    "２ 買戻し手続等",
    "第３ 管理及び運営",
    "１ 資産管理等の概要",
    "(1) 資産の評価",
    "(2) 保管",
    "(3) 存続期間",
    "(4) 計算期間",
    "(5) その他",
    "２ 利害関係人との取引制限",
    "３ 投資主・投資法人債権者の権利",
    "第４ 関係法人の状況",
    "１ 資産運用会社の概況",
    "(1) 名称、資本金の額及び事業の内容",
    "(2) 運用体制",
    "(3) 大株主の状況",
    "(4) 役員の状況",
    "(5) 事業の内容及び営業の概況",
    "２ その他の関係法人の概況",
    "(1) 名称、資本金の額及び事業の内容",
    "(2) 関係業務の概要",
    "(3) 資本関係",
    "第５ 投資法人の経理状況",
    "１ 財務諸表",
    "(1) 貸借対照表",
    "(2) 損益計算書",
    "(3) 投資主資本等変動計算書",
    "(4) 金銭の分配に係る計算書",
    "(5) キャッシュ・フロー計算書",
    "(6) 注記表",
    "(7) 附属明細表",
    "２ 投資法人の現況",
    "純資産額計算書",
    "第６ 販売及び買戻しの実績",
    "第７ 参考情報",
    "独立監査人"
]

z_digit = ["０", "１", "２", "３", "４","５", "６", "７", "８", "９", "１０"]
m_digit = ["⓪", "①", "②", "③", "④","⑤", "⑥", "⑦", "⑧", "⑨", "⑩"]
h_digit = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

zh_digit = {z:h for z, h in zip(z_digit, h_digit)}
mh_digit = {m:h for m, h in zip(m_digit, h_digit)}
def zh_convert(s):
    for z in z_digit:
        s = s.replace(z, zh_digit[z])
    for m in m_digit:
        s = s.replace(m, mh_digit[m])
    return s

def title_normalize(t):
    #特殊文字
    t = re.sub("&#[\d]+;", "", t)
    t = re.sub("[ -/:-@\[-~\s【】、。．（）]", "", t)
    t = zh_convert(t)
    return t


_titles = [title_normalize(k) for k in TITLES]
# _titles_sub = {title_normalize(k):[title_normalize(x) for x in v] for k, v  in TITLES_SUB.items()}
# _sub_titles = {t:set([]) for t in _titles}
# for k, v in _titles_sub.items():
#     for _v in v:
#         _sub_titles[_v].add(k)




def title_filter(titles):
    if not titles:
        return [title_normalize(t) for t in ["表紙","第一部 ファンド情報","第二部 投資法人の詳細情報", "独立監査人"]]
        #return [title_normalize(t) for t in ["表紙","第一部 ファンド情報","第二部 投資法人の詳細情報", "独立監査人の監査報告書"]]
    normalized = [title_normalize(t) for t in titles]
    r = []
    for t in normalized:
        if t and not (_sub_titles[t] & set(normalized)):
            r.append(t)
    return r


def get_es_indexes(titles):
    return [_titles.index(t) for t in titles]
