from classify_jd import classify_text

def test_quant_equity():
    jd = "We are hiring a researcher to design factor models, backtest signals, and manage portfolio construction."
    out = classify_text(jd)
    assert out["role_category"] == "Quant Equity Research"

def test_risk():
    jd = "Responsibilities include VaR calculations, stress testing, scenario analysis and exposure reporting."
    out = classify_text(jd)
    assert out["role_category"] == "Risk"

def test_ba():
    jd = "Work with stakeholders on dashboards, KPI design, SQL and Tableau for business insights."
    out = classify_text(jd)
    assert out["role_category"] == "Business Analyst"

if __name__ == '__main__':
    test_quant_equity()
    test_risk()
    test_ba()
    print('All tests passed')
