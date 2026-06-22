#!/usr/bin/env python3
"""
Veloton Group — proper double-entry test data.

Every P&L entry posts its exact BS counterpart so the balance sheet
reconciles naturally (Assets - Liabilities - Equity = 0).

Revenue recognised → DR Receivables / CR Income
Cash collected    → DR Cash / CR Receivables
Inventory bought  → DR Inventory / CR Payables
COGS consumed     → DR COGS / CR Inventory
Cash expenses     → DR Expense / CR Cash
Accrued expenses  → DR Expense / CR Payables, then DR Payables / CR Cash
Depreciation      → DR Depreciation / CR Accumulated Dep
Tax               → DR Tax / CR Tax Payable
RE                → 5030 Retained earnings = monthly P&L net (negative = profit)

Account ranges:
  Income:      1000–1999
  Expenses:    2000–2999
  Assets:      3000–3999
  Liabilities: 4000–4999
  Equity:      5000–5999
"""
import csv, random, os
from datetime import date
from calendar import monthrange
from collections import defaultdict

random.seed(42)

HOLDING = "Veloton Holding ApS"
DK      = "Veloton ApS"
UK      = "Veloton Ltd"
PROJECTS = ["Project Apollo", "Project Bison", "Project Candy"]

FX = {2023:8.65, 2024:8.70, 2025:8.55, 2026:8.45, 2027:8.50}
SEASONAL = [1.20,0.85,0.90,1.00,1.05,0.90,0.75,0.95,1.00,1.05,1.05,1.30]
S = sum(SEASONAL)

DK_REV_M   = {2023:135., 2024:157., 2025:180., 2026:202., 2027:225.}
UK_REV_GBP = {2023:5.2,  2024:6.1,  2025:7.0,  2026:7.9,  2027:8.6}
IC_LOAN_DK = {2023:20_000_000, 2024:22_000_000, 2025:24_000_000,
              2026:24_000_000, 2027:24_000_000}
IC_RATE = 0.04
PAY_RATE     = 0.82   # % of payables paid same month

def collect_rate(mi):
    """Seasonal DSO: peak months leave more outstanding (lower collection rate)."""
    s = SEASONAL[mi]
    if s >= 1.15:   return 0.72   # Dec/Jan peak — lots of outstanding AR
    elif s >= 1.00: return 0.80   # Above-average months
    elif s >= 0.90: return 0.87   # Near-average
    else:           return 0.93   # Low season — easier to collect

def purchase_ratio(mi):
    """Seasonal inventory build/draw: stock up before peak, draw down after."""
    # SEASONAL pattern: builds toward Dec peak, draws down Jan-Mar
    if mi in (7, 8, 9, 10):  return rnd(1.12, 1.20)  # Aug-Nov: pre-peak build
    elif mi in (0, 1, 2):    return rnd(0.85, 0.95)  # Jan-Mar: post-peak draw-down
    else:                    return rnd(1.00, 1.07)   # normal replenishment

rows = []

def r2(x): return round(x, 2)
def mo(m, mi): return m * 1_000_000 * SEASONAL[mi] / S
def rnd(lo=.95, hi=1.05): return random.uniform(lo, hi)
def fmt(x): return f"{x:.2f}".replace(".", ",")

def add(ent, d, code, name, amt, dept="", proj=""):
    rows.append({
        "Date":        date(d.year, d.month, 1).strftime("%Y-%m-%d"),
        "Account":     f"{code} {name}",
        "Amount":      r2(amt),
        "Description": "Test transaction",
        "Entity":      ent,
        "Department":  dept,
        "Project":     proj,
    })

def is_pnl(account_field):
    code = int(account_field.split()[0])
    return 1000 <= code <= 2999

# helpers: post an income entry AND its receivables counterpart
def income(ent, d, code, name, amount, dept="Sales", proj=""):
    """CR Income / DR Receivables"""
    add(ent, d, code,  name,               -r2(amount), dept, proj)
    add(ent, d, 3340, "Trade receivables",  r2(amount), dept, proj)

def income_ic(ent, d, amount):
    """CR IC Revenue / DR IC Receivable, then settle to Cash"""
    add(ent, d, 1090, "IC revenue",        -r2(amount), "Sales")
    add(ent, d, 3350, "Other receivables",  r2(amount), "Sales")
    # Settle IC in same month
    add(ent, d, 3900, "Cash",               r2(amount), "Finance")
    add(ent, d, 3350, "Other receivables", -r2(amount), "Finance")

def collect_receivables(ent, d, total_invoiced, rate=None):
    """DR Cash / CR Receivables — rate defaults to seasonal DSO."""
    if rate is None: rate = collect_rate(d.month - 1)
    collected = r2(total_invoiced * rate)
    add(ent, d, 3900, "Cash",               collected, "Finance")
    add(ent, d, 3340, "Trade receivables", -collected, "Finance")

def expense_cash(ent, d, code, name, amount, dept="Finance"):
    """DR Expense / CR Cash"""
    add(ent, d, code, name,   r2(amount), dept)
    add(ent, d, 3900, "Cash", -r2(amount), "Finance")  # cash always Finance dept

def expense_payable(ent, d, code, name, amount, dept="Finance"):
    """DR Expense / CR Trade Payables, then pay PAY_RATE of it same month"""
    add(ent, d, code,  name,               r2(amount), dept)
    add(ent, d, 4310, "Trade payables",   -r2(amount), dept)
    paid = r2(amount * PAY_RATE)
    add(ent, d, 4310, "Trade payables",    paid, dept)
    add(ent, d, 3900, "Cash",             -paid, "Finance")  # cash always Finance

def cogs_material(ent, d, code, name, amount, mi=None):
    """DR COGS / CR Inventory (consume), DR Inventory / CR Payables (purchase)."""
    add(ent, d, code, name,                   r2(amount), "Operations")
    add(ent, d, 3310, "Inventory - raw materials", -r2(amount), "Operations")
    # Seasonal purchase ratio: build stock pre-peak, draw down post-peak
    ratio = purchase_ratio(mi) if mi is not None else rnd(1.00, 1.08)
    purchase = r2(amount * ratio)
    add(ent, d, 3310, "Inventory - raw materials",  purchase,  "Operations")
    add(ent, d, 4310, "Trade payables",            -purchase,  "Operations")
    paid = r2(purchase * PAY_RATE)
    add(ent, d, 4310, "Trade payables",  paid, "Operations")
    add(ent, d, 3900, "Cash",           -paid, "Finance")

def depreciation(ent, d, exp_code, exp_name, acc_code, acc_name, amount):
    """DR Depreciation / CR Accumulated Dep"""
    add(ent, d, exp_code, exp_name,   r2(amount), "Operations")
    add(ent, d, acc_code, acc_name,  -r2(amount), "Operations")

def tax_accrual(ent, d, amount):
    """DR Tax Expense / CR Tax Payable"""
    add(ent, d, 2900, "Tax expense",            r2(amount), "Finance")
    add(ent, d, 4350, "Corporate tax payables", -r2(amount), "Finance")

def tax_pay(ent, d, amount):
    """DR Tax Payable / CR Cash"""
    add(ent, d, 4350, "Corporate tax payables",  r2(amount), "Finance")
    add(ent, d, 3900, "Cash",                   -r2(amount), "Finance")

def capex(ent, d, code, name, amount, proj=""):
    """DR Asset / CR Cash"""
    add(ent, d, code, name,    r2(amount), "Operations", proj)
    add(ent, d, 3900, "Cash", -r2(amount), "Finance")

def loan_draw(ent, d, code, name, amount):
    """DR Cash / CR Loan (liability increases)"""
    add(ent, d, 3900, "Cash",  r2(amount), "Finance")
    add(ent, d, code, name,   -r2(amount), "Finance")

def loan_repay(ent, d, code, name, amount):
    """DR Loan / CR Cash"""
    add(ent, d, code, name,    r2(amount), "Finance")
    add(ent, d, 3900, "Cash", -r2(amount), "Finance")

# ─────────────────────────────────────────────────────────────────────────────
for year in range(2023, 2028):
    for month in range(1, 13):
        mi  = month - 1
        dim = monthrange(year, month)[1]
        eom = date(year, month, dim)
        fx  = FX[year]
        qe  = (month % 3 == 0)

        dk   = mo(DK_REV_M[year], mi)
        uk   = mo(UK_REV_GBP[year], mi)
        ic_d = uk * fx * 0.65
        ic_g = ic_d / fx * random.uniform(0.997, 1.003)

        dk_sal  = (40_000_000 + (year-2023)*3_000_000) / 12
        uk_sal  = (1_200_000  + (year-2023)*100_000)   / 12
        loan    = IC_LOAN_DK[year]
        ic_int  = loan * IC_RATE / 12
        mf_dk   = dk  * 0.015
        mf_uk   = uk * fx * 0.015
        mf_uk_g = mf_uk / fx

        # ══════════════════════════════════════════════════════════════════
        # DK OPERATING
        # ══════════════════════════════════════════════════════════════════

        # Revenue — monthly core
        # 1010/1020: product sales → receivables then cash collection
        monthly_rev_dk = 0
        for code, name, pct in [
            (1010,"Hardware sales - bikes",       0.33),
            (1020,"Hardware sales - treadmills",  0.18),
        ]:
            amt = dk * pct
            income(DK, eom, code, name, amt)   # CR Income / DR Receivables
            monthly_rev_dk += amt

        # 1050: digital monthly sub → direct cash (recurring auto-debit, no AR)
        sub_m = dk * 0.08
        add(DK, eom, 1050,"Digital membership - monthly", -r2(sub_m), "Sales")
        add(DK, eom, 3900,"Cash",                          r2(sub_m), "Sales")

        # 1060 annual sub: handled entirely via deferred revenue below — do NOT post here

        # IC revenue (income + IC receivable + cash settlement)
        income_ic(DK, eom, ic_d)

        # Revenue — product/subscription monthly (direct recognition)
        for code, name, pct in [
            (1030,"Hardware sales - accessories",          0.09),
            (1040,"Hardware sales - refurbished equipment",0.04),
            (1080,"Corporate wellness - maintenance contract",0.04),
        ]:
            amt = dk * pct
            income(DK, eom, code, name, amt, "Sales")
            monthly_rev_dk += amt

        # 1070 Studio fit-out → goes through WIP (not direct revenue)
        # Monthly: costs accumulate in WIP (3370); project completes quarterly
        wip_project_rev = dk * 0.06   # revenue value of ongoing projects
        wip_cost_ratio  = 0.65        # costs = 65% of revenue value
        wip_cost_m = r2(wip_project_rev * wip_cost_ratio)
        proj = random.choice(PROJECTS)
        add(DK, eom, 3370,"WIP - project revenue",  wip_cost_m, "Operations", proj)
        add(DK, eom, 4310,"Trade payables",         -wip_cost_m, "Operations", proj)
        paid_wip = r2(wip_cost_m * PAY_RATE)
        add(DK, eom, 4310,"Trade payables",  paid_wip, "Operations", proj)
        add(DK, eom, 3900,"Cash",           -paid_wip, "Finance",    proj)

        # Quarterly project completion: release WIP → recognise revenue + COGS
        # Use actual sum of the 3 months in the quarter (not 3× current month)
        if qe:
            dk_m1 = mo(DK_REV_M[year], (mi-2) % 12)
            dk_m2 = mo(DK_REV_M[year], (mi-1) % 12)
            q_proj_rev = r2((dk_m1 + dk_m2 + dk) * 0.06)
            q_wip_cost = r2(q_proj_rev * wip_cost_ratio)
            add(DK, eom, 3340,"Trade receivables",          r2(q_proj_rev), "Sales",      proj)
            add(DK, eom, 1070,"Corporate wellness - studio fit-out", -r2(q_proj_rev), "Sales", proj)
            add(DK, eom, 3370,"WIP - project revenue",     -r2(q_wip_cost), "Operations", proj)
            add(DK, eom, 2070,"Manufacturing overhead",     r2(q_wip_cost), "Operations",  proj)
            monthly_rev_dk += q_proj_rev  # include in collections this quarter-end

        # Discounts — monthly
        disc = dk * 0.05
        add(DK, eom, 1099, "Discounts & returns",  disc, "Sales")
        add(DK, eom, 3340, "Trade receivables",   -disc, "Sales")

        # Collections: cash in, receivables down — seasonal DSO
        collect_receivables(DK, eom, monthly_rev_dk, rate=collect_rate(mi))

        # DK pays management fee to Holding — monthly
        expense_cash(DK, eom, 2450,"Miscellaneous admin", mf_dk, "Finance")

        # COGS — monthly with seasonal purchase ratio
        dk_cogs = dk * 0.45
        cogs_material(DK, eom, 2010,"Raw materials - frames & mechanical",    dk_cogs*0.28, mi)
        cogs_material(DK, eom, 2020,"Raw materials - electronics & screens",  dk_cogs*0.16, mi)
        cogs_material(DK, eom, 2030,"Raw materials - fabric & upholstery",    dk_cogs*0.07, mi)
        cogs_material(DK, eom, 2040,"Raw materials - packaging",              dk_cogs*0.03, mi)
        expense_cash(DK, eom,  2050,"Direct labour - production",             dk_cogs*0.23, "Operations")
        expense_cash(DK, eom,  2060,"Direct labour - assembly",               dk_cogs*0.10, "Operations")
        expense_payable(DK, eom, 2080,"Freight & logistics",                  dk_cogs*0.11*rnd(), "Operations")
        expense_payable(DK, eom, 2099,"Inventory write-down",                 dk_cogs*0.02*rnd(0.7,1.3), "Operations")

        # Salary — split across departments
        dk_sal_gross = dk_sal * 0.85
        for dept, pct in [("Sales",0.25),("Marketing",0.15),("Finance",0.15),("Operations",0.35),("HR",0.10)]:
            add(DK, eom, 2110,"Salaries & wages",     r2(dk_sal_gross*pct), dept)
            add(DK, eom, 3900,"Cash",                -r2(dk_sal_gross*pct), "Finance")
        # Pension and payroll costs
        expense_cash(DK, eom, 2120,"Pension contributions",  dk_sal*0.10, "Operations")
        expense_cash(DK, eom, 2130,"Other payroll costs",    dk_sal*0.05*rnd(), "Operations")

        # Payroll tax — monthly expense + liability accrual + cash settlement
        prt = r2(dk_sal * 0.08)
        add(DK, eom, 2130,"Other payroll costs",    prt, "Operations")
        add(DK, eom, 4360,"Payroll tax payables",  -prt, "Finance")
        paid_prt = r2(prt * 0.95)
        add(DK, eom, 4360,"Payroll tax payables",  paid_prt, "Finance")
        add(DK, eom, 3900,"Cash",                 -paid_prt, "Finance")

        # Rent & office — monthly
        expense_cash(DK, eom, 2210,"Rent & leasing",  800_000/12, "Operations")
        expense_payable(DK, eom, 2220,"Office expenses", 150_000/12*rnd(), "Operations")

        # Marketing — monthly
        dk_mktg = dk * 0.08
        expense_payable(DK, eom, 2310,"Digital marketing & advertising", dk_mktg*0.45, "Marketing")
        expense_payable(DK, eom, 2320,"Events & sponsorships",  dk_mktg*0.20*rnd(), "Marketing")
        expense_cash(DK, eom,    2330,"Sales commissions",       dk_mktg*0.25, "Sales")
        expense_payable(DK, eom, 2340,"CRM & marketing tools",   dk_mktg*0.10, "Marketing")

        # Admin — monthly
        expense_payable(DK, eom, 2410,"IT & software",        3_600_000/12*rnd(), "Finance")
        expense_payable(DK, eom, 2420,"Insurance",             1_200_000/12*rnd(), "Finance")
        expense_cash(DK, eom,    2430,"Bank charges & fees",     600_000/12*rnd(), "Finance")
        expense_payable(DK, eom, 2440,"Office supplies",         480_000/12*rnd(), "Finance")

        # Travel & professional — monthly
        expense_payable(DK, eom, 2510,"Travel & accommodation", 2_400_000/12*rnd(0.8,1.2), "Sales")
        expense_payable(DK, eom, 2520,"Meals & entertainment",    600_000/12*rnd(), "Sales")
        expense_payable(DK, eom, 2610,"Audit & accounting fees", 1_800_000/12*rnd(), "Finance")
        expense_payable(DK, eom, 2620,"Legal fees",               900_000/12*rnd(0.7,1.3), "Finance")
        expense_payable(DK, eom, 2630,"Consulting fees",         2_400_000/12*rnd(0.8,1.2), "Finance")

        # Depreciation (monthly)
        depreciation(DK, eom, 2710,"Depreciation - operating assets",
                              3112,"Accumulated dep - operating assets, delta", 250_000)
        depreciation(DK, eom, 2730,"Depreciation - vehicles",
                              3152,"Accumulated dep - vehicles, delta", 30_000)
        depreciation(DK, eom, 2740,"Depreciation - fixtures & fittings",
                              3172,"Accumulated dep - fixtures & fittings, delta", 20_000)
        depreciation(DK, eom, 2750,"Depreciation - IT equipment",
                              3192,"Accumulated dep - IT equipment, delta", 40_000)

        # Financial expenses — monthly
        expense_cash(DK, eom, 2810,"Financial expenses",  ic_int*0.75, "Finance")
        expense_cash(DK, eom, 2820,"IC interest expense", ic_int*0.25, "Finance")
        fx_amt = r2(dk*0.002*random.uniform(-1,1))
        if abs(fx_amt) > 1:
            if fx_amt > 0:
                add(DK, eom, 2830,"Currency & exchange rates",  fx_amt, "Finance")
                add(DK, eom, 3900,"Cash",                      -fx_amt, "Finance")
            else:
                add(DK, eom, 1930,"Currency & exchange rates",  fx_amt, "Finance")
                add(DK, eom, 3900,"Cash",                      -fx_amt, "Finance")

        # Tax
        dk_tax = max(0, dk*0.12*0.22)
        tax_accrual(DK, eom, dk_tax)
        if month == 3:
            tax_pay(DK, date(year,3,1),  dk_tax*5)
        if month == 9:
            tax_pay(DK, date(year,9,1),  dk_tax*5)

        # VAT (quarterly): net VAT payable accrual + cash settlement
        # Output VAT > input VAT = net liability. Settle from cash.
        if qe:
            vat_net = r2((dk*0.95*0.25 - dk_cogs*0.52*0.25)*3*rnd(0.9,1.0))
            if vat_net > 0:
                add(DK, eom, 4370,"VAT payable",  -vat_net, "Finance")   # CR VAT payable
                add(DK, eom, 3900,"Cash",           vat_net, "Finance")   # DR Cash (embedded in payables)
                # Settlement to tax authority
                settle = r2(vat_net*0.92)
                add(DK, eom, 4370,"VAT payable",   settle, "Finance")    # DR VAT payable
                add(DK, eom, 3900,"Cash",          -settle, "Finance")   # CR Cash

        # Deferred revenue — subscriptions (cash in, defer, recognise)
        if month == 1:
            annual_sub = dk * 12 * 0.07  # full year collected in Jan
            add(DK, date(year,1,1), 3900, "Cash",                        r2(annual_sub), "Sales")
            add(DK, date(year,1,1), 4340,"Deferred revenue - subscriptions", -r2(annual_sub), "Sales")
        # Monthly recognition: DR Deferred Revenue / CR Income (not cash)
        sub_recog = dk * 0.07
        add(DK, eom, 4340,"Deferred revenue - subscriptions",  r2(sub_recog), "Sales")
        add(DK, eom, 1060,"Digital membership - annual",       -r2(sub_recog), "Sales")

        # CAPEX additions (DR Asset / CR Cash)
        # CAPEX additions — separate account per asset class (3x01 = addition)
        # DR CAPEX addition / CR Cash
        capex_dk = {
            (2023,3):(5_000_000, 3101,"CAPEX - operating assets, addition","Project Apollo"),
            (2024,6):(3_500_000, 3101,"CAPEX - operating assets, addition","Project Bison"),
            (2025,9):(4_000_000, 3101,"CAPEX - operating assets, addition","Project Candy"),
            (2026,4):(2_500_000, 3101,"CAPEX - operating assets, addition","Project Apollo"),
            (2027,2):(3_000_000, 3101,"CAPEX - operating assets, addition","Project Bison"),
            (2023,1):(900_000,   3141,"CAPEX - vehicles, addition",""),
            (2025,1):(950_000,   3141,"CAPEX - vehicles, addition",""),
            (2024,2):(1_200_000, 3161,"CAPEX - fixtures & fittings, addition",""),
            (2023,9):(600_000,   3181,"CAPEX - IT equipment, addition",""),
            (2025,9):(660_000,   3181,"CAPEX - IT equipment, addition",""),
            (2027,9):(726_000,   3181,"CAPEX - IT equipment, addition",""),
        }
        if (year,month) in capex_dk:
            amt,code,name,proj = capex_dk[(year,month)]
            capex(DK, eom, code, name, amt, proj)

        # CAPEX detractions — separate account per asset class (3x02 = detraction)
        # DR Accumulated Dep / CR CAPEX detraction (removes asset at cost)
        capex_detr_dk = {
            # Dispose 2023 fleet vehicle (cost 900k, fully depreciated → net 0)
            (2026,1): [(3150,"Accumulated dep - vehicles",          900_000),
                       (3142,"CAPEX - vehicles, detraction",       -900_000)],
            # Dispose 2023 IT equipment (cost 600k, fully depreciated → net 0)
            (2026,9): [(3190,"Accumulated dep - IT equipment",      600_000),
                       (3182,"CAPEX - IT equipment, detraction",   -600_000)],
            # Dispose 2024 showroom fixtures (cost 1.2M, NBV 720k → loss on disposal, no cash proceeds)
            # DR Accum dep 480k / DR Loss on disposal 720k / CR CAPEX detraction -1.2M
            (2027,6): [(3170,"Accumulated dep - fixtures & fittings", 480_000),
                       (3162,"CAPEX - fixtures & fittings, detraction", -1_200_000),
                       (2740,"Depreciation - fixtures & fittings",  720_000)],
        }
        if (year,month) in capex_detr_dk:
            for c, n, a in capex_detr_dk[(year,month)]:
                add(DK, eom, c, n, a, "Operations" if n.startswith("3") else "Finance")

        # Opening entries
        if month==1 and year==2023:
            loan_draw(DK, date(2023,1,1), 4110,"Loans - bank",     15_000_000)
            loan_draw(DK, date(2023,1,1), 4120,"IC loans payable", 20_000_000)
            add(DK, date(2023,1,1), 3210,"Deposits",              2_400_000, "Finance")
            add(DK, date(2023,1,1), 3900,"Cash",                 -2_400_000, "Finance")
            add(DK, date(2023,1,1), 5010,"Share capital",        -10_000_000, "Finance")
            add(DK, date(2023,1,1), 3900,"Cash",                 10_000_000, "Finance")
            # Immediately invest the IC loan in factory and production line
            capex(DK, date(2023,1,1), 3101,"CAPEX - operating assets, addition", 18_000_000, "Project Apollo")
            # DK provides working capital IC loan to UK (6M DKK = ~694k GBP at opening FX)
            add(DK, date(2023,1,1), 3221,"IC loan to subsidiary - UK",  6_000_000, "Finance")
            add(DK, date(2023,1,1), 3900,"Cash",                       -6_000_000, "Finance")
        if month==1 and year in (2024,2025):
            loan_draw(DK, date(year,1,1), 4120,"IC loans payable", 2_000_000)

        # Regular annual equipment CAPEX (production capacity and replacement)
        annual_equip = {
            (2023,7): 2_000_000, (2024,3): 3_500_000, (2024,10): 2_000_000,
            (2025,5): 4_000_000, (2025,11): 2_000_000,
            (2026,2): 4_000_000, (2026,8):  2_000_000,
            (2027,4): 4_000_000, (2027,10): 2_000_000,
        }
        if (year,month) in annual_equip:
            capex(DK, eom, 3101,"CAPEX - operating assets, addition",
                  annual_equip[(year,month)], "Project Bison" if year in (2024,2025) else "Project Candy")

        # Loan repayment (monthly — bank loan over 5 years)
        loan_repay(DK, eom, 4110,"Loans - bank", 15_000_000/(5*12))

        # IC loan repayment to Holding (annual, July) — returning capital as profits build
        ic_repayments_dk = {2024:4_000_000, 2025:5_000_000, 2026:5_000_000, 2027:5_000_000}
        if month==7 and year in ic_repayments_dk:
            repay = ic_repayments_dk[year]
            add(DK, date(year,7,1), 4120,"IC loans payable",       repay, "Finance")
            add(DK, date(year,7,1), 3900,"Cash",                  -repay, "Finance")
            # Mirror in Holding
            add(HOLDING, date(year,7,1), 3220,"IC loans receivable", -repay, "Finance")
            add(HOLDING, date(year,7,1), 3900,"Cash",                 repay, "Finance")

        # Annual dividend DK → Holding (April, for prior year profit)
        dk_dividends = {2024:4_000_000, 2025:14_000_000, 2026:20_000_000, 2027:25_000_000}
        if month==4 and year in dk_dividends:
            div = dk_dividends[year]
            add(DK, date(year,4,1), 5020,"Dividends",  r2(div), "Finance")
            add(DK, date(year,4,1), 3900,"Cash",       -r2(div), "Finance")

        # ══════════════════════════════════════════════════════════════════
        # UK OPERATING
        # ══════════════════════════════════════════════════════════════════

        monthly_rev_uk = 0
        for code, name, pct in [
            (1010,"Hardware sales - bikes",       0.52),
            (1020,"Hardware sales - treadmills",  0.30),
        ]:
            amt = uk * pct
            income(UK, eom, code, name, amt)
            monthly_rev_uk += amt

        # UK accessories revenue — monthly
        amt = uk * 0.13
        income(UK, eom, 1030,"Hardware sales - accessories", amt)
        disc = uk * 0.05
        add(UK, eom, 1099,"Discounts & returns",  disc, "Sales")
        add(UK, eom, 3340,"Trade receivables",   -disc, "Sales")

        collect_receivables(UK, eom, monthly_rev_uk + uk*0.13, rate=collect_rate(mi))

        # IC COGS (payable to DK)
        add(UK, eom, 2090,"IC COGS - purchases from DK",  r2(ic_g), "Operations")
        add(UK, eom, 4320,"IC payables",                 -r2(ic_g), "Operations")
        paid_ic = r2(ic_g * 0.95)
        add(UK, eom, 4320,"IC payables",  paid_ic, "Finance")
        add(UK, eom, 3900,"Cash",         -paid_ic, "Finance")

        expense_payable(UK, eom, 2080,"Freight & logistics", uk*0.07, "Operations")
        # UK salary — split across departments
        uk_sal_gross = uk_sal * 0.85
        for dept, pct in [("Sales",0.40),("Operations",0.35),("Finance",0.25)]:
            add(UK, eom, 2110,"Salaries & wages",    r2(uk_sal_gross*pct), dept)
            add(UK, eom, 3900,"Cash",               -r2(uk_sal_gross*pct), "Finance")
        expense_cash(UK, eom, 2120,"Pension contributions", uk_sal*0.10, "Operations")
        expense_cash(UK, eom, 2130,"Other payroll costs",   uk_sal*0.05*rnd(), "Operations")
        # UK NI payroll tax — monthly
        uk_ni = r2(uk_sal * 0.138)
        add(UK, eom, 2130,"Other payroll costs",    uk_ni, "Operations")
        add(UK, eom, 4360,"Payroll tax payables",  -uk_ni, "Finance")
        paid_ni = r2(uk_ni * 0.95)
        add(UK, eom, 4360,"Payroll tax payables",  paid_ni, "Finance")
        add(UK, eom, 3900,"Cash",                 -paid_ni, "Finance")

        expense_cash(UK, eom, 2210,"Rent & leasing", 80_000/12, "Operations")
        expense_payable(UK, eom, 2310,"Digital marketing & advertising", uk*0.06*0.60, "Marketing")
        expense_cash(UK, eom,    2330,"Sales commissions",   uk*0.06*0.40, "Sales")
        expense_payable(UK, eom, 2410,"IT & software",       15_000/12*rnd(), "Finance")
        expense_payable(UK, eom, 2420,"Insurance",           12_000/12*rnd(), "Finance")
        expense_cash(UK, eom,    2430,"Bank charges & fees",  6_000/12*rnd(), "Finance")
        expense_cash(UK, eom,    2450,"Miscellaneous admin",  mf_uk_g, "Finance")
        expense_payable(UK, eom, 2510,"Travel & accommodation", uk*0.012*rnd(0.8,1.2), "Sales")
        expense_payable(UK, eom, 2610,"Audit & accounting fees", 8_000/12*rnd(), "Finance")
        expense_payable(UK, eom, 2620,"Legal fees", 5_000/12*rnd(0.7,1.3), "Finance")

        depreciation(UK, eom, 2730,"Depreciation - vehicles",           3152,"Accumulated dep - vehicles, delta", 3_500)
        depreciation(UK, eom, 2740,"Depreciation - fixtures & fittings",3172,"Accumulated dep - fixtures & fittings, delta", 2_000)
        depreciation(UK, eom, 2750,"Depreciation - IT equipment",       3192,"Accumulated dep - IT equipment, delta", 4_000)

        uk_tax = max(0, uk*0.08*0.25)
        tax_accrual(UK, eom, uk_tax)
        if month == 9:
            tax_pay(UK, eom, uk_tax*3)

        # UK financial — monthly
        uk_ic_int = (loan*0.40/fx)*IC_RATE/12
        expense_cash(UK, eom, 2810,"Financial expenses",  uk_ic_int*0.50, "Finance")
        expense_cash(UK, eom, 2820,"IC interest expense", uk_ic_int*0.50, "Finance")

        # UK VAT — quarterly (legal settlement cycle)
        if qe:
            uk_vat = r2(uk*0.95*0.20*3*rnd(0.9,1.0))
            add(UK, eom, 4370,"VAT payable",  -uk_vat, "Finance")
            add(UK, eom, 3900,"Cash",          uk_vat, "Finance")
            settle_vat = r2(uk_vat*0.90)
            add(UK, eom, 4370,"VAT payable",   settle_vat, "Finance")
            add(UK, eom, 3900,"Cash",          -settle_vat, "Finance")

        uk_capex = {
            (2023,2):(80_000, 3140,"CAPEX - vehicles"),
            (2025,3):(150_000,3160,"CAPEX - fixtures & fittings"),
            (2023,10):(50_000,3180,"CAPEX - IT equipment"),
            (2025,10):(55_000,3180,"CAPEX - IT equipment"),
            (2027,10):(60_000,3180,"CAPEX - IT equipment"),
        }
        if (year,month) in uk_capex:
            amt,code,name = uk_capex[(year,month)]
            capex(UK, eom, code, name, amt)

        if month==1 and year==2023:
            loan_draw(UK, date(2023,1,1), 4120,"IC loans payable", 3_000_000/fx)
            add(UK, date(2023,1,1), 3210,"Deposits",  160_000, "Finance")
            add(UK, date(2023,1,1), 3900,"Cash",      -160_000, "Finance")
            # UK SC = 1M GBP (realistic startup distribution subsidiary)
            # Funded by Holding as equity investment
            add(UK, date(2023,1,1), 5010,"Share capital",  -1_000_000, "Finance")
            add(UK, date(2023,1,1), 3900,"Cash",            1_000_000, "Finance")
            # Working capital IC loan from DK to UK (covers UK cash needs)
            add(UK, date(2023,1,1), 4120,"IC loans payable",  -6_000_000/fx, "Finance")
            add(UK, date(2023,1,1), 3900,"Cash",               6_000_000/fx, "Finance")

        # ══════════════════════════════════════════════════════════════════
        # HOLDING
        # ══════════════════════════════════════════════════════════════════

        # Management fee income — monthly
        total_mf = mf_dk + mf_uk
        add(HOLDING, eom, 3900, "Cash",               r2(total_mf), "Finance")
        add(HOLDING, eom, 1910, "Financial income",  -r2(total_mf), "Finance")
        # IC interest income — monthly
        add(HOLDING, eom, 3900, "Cash",               r2(ic_int), "Finance")
        add(HOLDING, eom, 1920, "IC interest income", -r2(ic_int), "Finance")

        # Holding costs — all monthly
        expense_cash(HOLDING, eom, 2110,"Salaries & wages",      3_000_000/12*0.85, "Finance")
        expense_cash(HOLDING, eom, 2120,"Pension contributions",  3_000_000/12*0.10, "Finance")
        expense_payable(HOLDING, eom, 2410,"IT & software",       60_000/12*rnd(), "Finance")
        expense_payable(HOLDING, eom, 2610,"Audit & accounting fees", 80_000/12*rnd(), "Finance")
        expense_payable(HOLDING, eom, 2620,"Legal fees",          60_000/12*rnd(0.7,1.3), "Finance")

        gw = 15_000_000/(20*12)
        depreciation(HOLDING, eom, 2720,"Depreciation - goodwill",  3132,"Accumulated dep - goodwill, delta", gw)
        depreciation(HOLDING, eom, 2750,"Depreciation - IT equipment",3192,"Accumulated dep - IT equipment, delta", 5_000)

        # Dividends (April)
        if month==4 and year>2023:
            div = DK_REV_M[year-1]*1_000_000*0.04
            add(HOLDING, date(year,4,1), 5020,"Dividends",  r2(div), "Finance")
            add(HOLDING, date(year,4,1), 3900,"Cash",       -r2(div), "Finance")

        # Dividend received from DK (April, same timing as DK payment)
        if month==4 and year in dk_dividends:
            div_h = dk_dividends[year]
            add(HOLDING, date(year,4,1), 3900,"Cash",              r2(div_h), "Finance")
            add(HOLDING, date(year,4,1), 1950,"Dividend income",  -r2(div_h), "Finance")

        if month==1 and year==2023:
            # Goodwill acquisition paid in cash (premium over book value of subsidiaries)
            add(HOLDING, date(2023,1,1), 3120,"CAPEX - goodwill",   15_000_000, "Finance")
            add(HOLDING, date(2023,1,1), 3900,"Cash",               -15_000_000, "Finance")
            # IC loans issued to operating subsidiaries
            add(HOLDING, date(2023,1,1), 3220,"IC loans receivable", 23_000_000, "Finance")
            add(HOLDING, date(2023,1,1), 3900,"Cash",               -23_000_000, "Finance")
            # Investment in subsidiaries (at cost = their share capital in DKK)
            # DK ApS: 10M DKK share capital
            # UK Ltd: 1M GBP × 8.65 = 8.65M DKK share capital
            inv_dk = 10_000_000
            inv_uk = r2(1_000_000 * fx)   # 1M GBP at opening FX
            add(HOLDING, date(2023,1,1), 3240,"Investment in subsidiaries", inv_dk + inv_uk, "Finance")
            add(HOLDING, date(2023,1,1), 3900,"Cash",                      -(inv_dk + inv_uk), "Finance")
            # Share capital (larger to fund all investments: 15M goodwill + 18.65M subs + 23M IC loans = 56.65M)
            add(HOLDING, date(2023,1,1), 5010,"Share capital",      -60_000_000, "Finance")
            add(HOLDING, date(2023,1,1), 3900,"Cash",                60_000_000, "Finance")
        if month==1 and year in (2024,2025):
            add(HOLDING, date(year,1,1), 3220,"IC loans receivable",  2_000_000, "Finance")
            add(HOLDING, date(year,1,1), 3900,"Cash",                -2_000_000, "Finance")

# ─────────────────────────────────────────────────────────────────────────────
# POST-PROCESSING: add Retained Earnings = monthly P&L net
# RE = pnl (same sign: negative for profitable month = credit to equity)
# With proper pairs, BS already = 0 from the transaction entries alone.
# RE closes the P&L into equity. No cash plug needed.
# ─────────────────────────────────────────────────────────────────────────────
by_em = defaultdict(list)
for r in rows:
    by_em[(r["Entity"], r["Date"][:7])].append(r)

extra = []
for (ent, ym), em_rows in sorted(by_em.items()):
    pnl = sum(float(r["Amount"]) for r in em_rows if is_pnl(r["Account"]))
    if abs(pnl) > 0.01:
        extra.append({
            "Date": f"{ym}-01", "Account": "5030 Retained earnings",
            "Amount": r2(pnl), "Description": "Test transaction",
            "Entity": ent, "Department": "Finance", "Project": ""
        })

rows.extend(extra)

# ─── CAPEX opening balances ───────────────────────────────────────────────────
# At January 1 of each year (2024-2027), carry forward the prior cumulative
# gross cost and accumulated depreciation into dedicated "opening" accounts.
# Each pair is balanced:
#   DR 3x00 "opening" = +prior_net_capex  (asset opening increases)
#   CR 3x01 "addition" = -prior_net_capex  (removes prior from addition account)
# And for accumulated dep:
#   DR 3x12 "delta" = +prior_dep           (removes prior charges from delta)
#   CR 3x10 "opening" = -prior_dep         (contra-asset opening increases)

CAPEX_OPENING_MAP = {
    # (entity, addition_code, opening_code, dep_delta_code, dep_opening_code, detraction_code)
    DK: [
        (3101,"CAPEX - operating assets, addition",    3100,"CAPEX - operating assets, opening",
         3112,"Accumulated dep - operating assets, delta", 3110,"Accumulated dep - operating assets, opening", 3102),
        (3141,"CAPEX - vehicles, addition",            3140,"CAPEX - vehicles, opening",
         3152,"Accumulated dep - vehicles, delta",      3150,"Accumulated dep - vehicles, opening", 3142),
        (3161,"CAPEX - fixtures & fittings, addition", 3160,"CAPEX - fixtures & fittings, opening",
         3172,"Accumulated dep - fixtures & fittings, delta", 3170,"Accumulated dep - fixtures & fittings, opening", 3162),
        (3181,"CAPEX - IT equipment, addition",        3180,"CAPEX - IT equipment, opening",
         3192,"Accumulated dep - IT equipment, delta",  3190,"Accumulated dep - IT equipment, opening", 3182),
    ],
    UK: [
        (3141,"CAPEX - vehicles, addition",            3140,"CAPEX - vehicles, opening",
         3152,"Accumulated dep - vehicles, delta",      3150,"Accumulated dep - vehicles, opening", 3142),
        (3161,"CAPEX - fixtures & fittings, addition", 3160,"CAPEX - fixtures & fittings, opening",
         3172,"Accumulated dep - fixtures & fittings, delta", 3170,"Accumulated dep - fixtures & fittings, opening", 3162),
        (3181,"CAPEX - IT equipment, addition",        3180,"CAPEX - IT equipment, opening",
         3192,"Accumulated dep - IT equipment, delta",  3190,"Accumulated dep - IT equipment, opening", 3182),
    ],
    HOLDING: [
        (3181,"CAPEX - IT equipment, addition",        3180,"CAPEX - IT equipment, opening",
         3192,"Accumulated dep - IT equipment, delta",  3190,"Accumulated dep - IT equipment, opening", 3182),
    ],
}

opening_entries = []
for ent, classes in CAPEX_OPENING_MAP.items():
    for (add_c, add_n, open_c, open_n, dep_delta_c, dep_delta_n, dep_open_c, dep_open_n, detr_c) in classes:
        # Compute cumulative by year-end for each year 2023-2026
        cum_add = 0.0
        cum_dep = 0.0
        for yr in range(2023, 2027):
            # Sum all addition and detraction entries for this year
            yr_add = sum(float(r["Amount"]) for r in rows
                         if r["Entity"]==ent and r["Date"][:4]==str(yr)
                         and (int(r["Account"].split()[0]) in (add_c, detr_c)))
            yr_dep = sum(float(r["Amount"]) for r in rows
                         if r["Entity"]==ent and r["Date"][:4]==str(yr)
                         and int(r["Account"].split()[0]) == dep_delta_c)
            cum_add += yr_add
            cum_dep += yr_dep
            # Post opening entries on Jan 1 of next year
            next_yr = yr + 1
            d = f"{next_yr}-01-01"
            if abs(cum_add) > 0.01:
                opening_entries.append({
                    "Date": d, "Account": f"{open_c} {open_n}",
                    "Amount": fmt(cum_add), "Description": "Test transaction",
                    "Entity": ent, "Department": "Operations", "Project": ""
                })
                opening_entries.append({
                    "Date": d, "Account": f"{add_c} {add_n}",
                    "Amount": fmt(-cum_add), "Description": "Test transaction",
                    "Entity": ent, "Department": "Operations", "Project": ""
                })
            if abs(cum_dep) > 0.01:
                opening_entries.append({
                    "Date": d, "Account": f"{dep_open_c} {dep_open_n}",
                    "Amount": fmt(cum_dep), "Description": "Test transaction",
                    "Entity": ent, "Department": "Operations", "Project": ""
                })
                opening_entries.append({
                    "Date": d, "Account": f"{dep_delta_c} {dep_delta_n}",
                    "Amount": fmt(-cum_dep), "Description": "Test transaction",
                    "Entity": ent, "Department": "Operations", "Project": ""
                })

# ─── Verification ────────────────────────────────────────────────────────────
total_rows = len(rows) + len(opening_entries)
print(f"Rows: {total_rows:,}  ({len(rows):,} transactional + {len(opening_entries)} CAPEX opening)")
from collections import Counter
for ent,cnt in Counter(r["Entity"] for r in rows+opening_entries).items():
    print(f"  {ent}: {cnt:,}")

# BS balance check: sum of asset+liability+equity accounts should = 0 per period
def acct_range(acct):
    c = int(acct.split()[0])
    if 1000 <= c <= 2999: return "pnl"
    if 3000 <= c <= 3999: return "asset"
    if 4000 <= c <= 4999: return "liability"
    if 5000 <= c <= 5999: return "equity"

cum_bs = defaultdict(float)
for r in rows:
    t = acct_range(r["Account"])
    if t in ("asset","liability","equity"):
        cum_bs[(r["Entity"], r["Date"][:7], t)] += float(r["Amount"])

print("\nBS check (Dec-2025):")
for ent in [DK, UK, HOLDING]:
    periods = sorted(set(k[1] for k in cum_bs if k[0]==ent and k[1]<="2025-12"))
    a = l = e = 0
    for p in periods:
        a += cum_bs.get((ent,p,"asset"),0)
        l += cum_bs.get((ent,p,"liability"),0)
        e += cum_bs.get((ent,p,"equity"),0)
    print(f"  {ent[:12]}: A={a/1e6:+.1f}M  L={l/1e6:+.1f}M  E={e/1e6:+.1f}M  A+L+E={( a+l+e)/1e3:+.0f}k")

# ─── Write ────────────────────────────────────────────────────────────────────
output = "/Users/anton/Documents/GitHub/docs/test-data/test-data.csv"
os.makedirs(os.path.dirname(output), exist_ok=True)
fields = ["Date","Account","Amount","Description","Entity","Department","Project"]
all_rows = sorted(rows + opening_entries, key=lambda r: r["Date"])
with open(output,"w",newline="",encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=fields, delimiter=";")
    w.writeheader()
    for r in all_rows:
        # opening_entries already have amounts as formatted strings; rows still have floats
        if isinstance(r["Amount"], float):
            r["Amount"] = fmt(r["Amount"])
        w.writerow(r)
print(f"\nWritten: {output}")
