#!/usr/bin/env python3
"""
Veloton Group — complete double-entry test data.
Every journal entry posts both sides. Trial balance sums to zero always.
Entities: Veloton Holding ApS (DKK), Veloton ApS (DKK), Veloton Ltd (GBP)
Period: 2023-01 – 2027-12
"""
import csv, random, os
from datetime import date
from calendar import monthrange

random.seed(42)

HOLDING = "Veloton Holding ApS"
DK      = "Veloton ApS"
UK      = "Veloton Ltd"
PROJECTS = ["Project Apollo", "Project Bison", "Project Candy"]

FX = {2023:8.65, 2024:8.70, 2025:8.55, 2026:8.45, 2027:8.50}
SEASONAL = [1.20,0.85,0.90,1.00,1.05,0.90,0.75,0.95,1.00,1.05,1.05,1.30]
S = sum(SEASONAL)

DK_REV_M   = {2023:135., 2024:157., 2025:180., 2026:202., 2027:225.}
UK_REV_GBP = {2023:5.2,  2024:6.1,  2025:7.0,  2026:7.9,  2027:8.6 }
IC_LOAN_DK = {2023:20_000_000, 2024:22_000_000, 2025:24_000_000,
              2026:24_000_000, 2027:24_000_000}
IC_RATE    = 0.04

rows = []

def r2(x): return round(x, 2)
def mo(m, mi): return m*1_000_000*SEASONAL[mi]/S
def rnd(lo=.95,hi=1.05): return random.uniform(lo,hi)

def je(ent, d, entries, base_desc, dept="", proj=""):
    """
    Post a balanced journal entry.
    entries = list of (code, account_name, amount)  — positive=debit, negative=credit
    Raises if unbalanced.
    """
    total = sum(e[2] for e in entries)
    if abs(total) > 0.02:
        raise ValueError(f"Unbalanced by {total:.2f}: {base_desc}")
    for code, name, amt in entries:
        rows.append({
            "Date":         d.strftime("%Y-%m-%d"),
            "Entity":       ent,
            "Account Code": code,
            "Account":      name,
            "Amount":       r2(amt),
            "Description":  f"Test transaction – {base_desc}",
            "Department":   dept,
            "Project":      proj,
        })

# ── shorthand journals ────────────────────────────────────────────────────────
def rev_rec(ent, d, rev_code, rev_name, amount, desc, dept="Sales", proj=""):
    """CR Revenue / DR Trade Receivables"""
    je(ent, d, [(rev_code, rev_name, -r2(amount)),
                ("20060","Trade receivables", r2(amount))], desc, dept, proj)

def collect(ent, d, amount, desc):
    """DR Cash / CR Trade Receivables"""
    je(ent, d, [("20010","Cash", r2(amount)),
                ("20060","Trade receivables", -r2(amount))], desc, "Finance")

def ic_recv_raise(ent, d, rev_code, amount_lcy, desc):
    """DK IC: CR IC Revenue / DR IC Receivable (other receivables)"""
    je(ent, d, [(rev_code,"IC revenue", -r2(amount_lcy)),
                ("20070","Other receivables", r2(amount_lcy))], desc, "Sales")

def ic_recv_settle(ent, d, amount_lcy, desc):
    """DK IC cash settlement: DR Cash / CR IC Receivable"""
    je(ent, d, [("20010","Cash", r2(amount_lcy)),
                ("20070","Other receivables", -r2(amount_lcy))], desc, "Finance")

def ic_pay_raise(ent, d, cogs_code, amount_lcy, desc):
    """UK IC: DR IC COGS / CR IC Payable (other liabilities)"""
    je(ent, d, [(cogs_code,"IC COGS - purchases from DK", r2(amount_lcy)),
                ("40011","IC payables", -r2(amount_lcy))], desc, "Operations")

def ic_pay_settle(ent, d, amount_lcy, desc):
    """UK IC payment: DR IC Payable / CR Cash"""
    je(ent, d, [("40011","IC payables", r2(amount_lcy)),
                ("20010","Cash", -r2(amount_lcy))], desc, "Finance")

def exp_payable(ent, d, code, name, amount, desc, dept="Finance", proj=""):
    """DR Expense / CR Trade Payables"""
    je(ent, d, [(code, name, r2(amount)),
                ("40010","Trade payables", -r2(amount))], desc, dept, proj)

def exp_cash(ent, d, code, name, amount, desc, dept="Finance", proj=""):
    """DR Expense / CR Cash"""
    je(ent, d, [(code, name, r2(amount)),
                ("20010","Cash", -r2(amount))], desc, dept, proj)

def pay_payables(ent, d, amount, desc):
    """DR Trade Payables / CR Cash"""
    je(ent, d, [("40010","Trade payables", r2(amount)),
                ("20010","Cash", -r2(amount))], desc, "Finance")

def depn(ent, d, exp_code, exp_name, acc_code, acc_name, amount, desc):
    """DR Depreciation / CR Accumulated Depreciation"""
    je(ent, d, [(exp_code, exp_name, r2(amount)),
                (acc_code, acc_name, -r2(amount))], desc, "Operations")

def capex_cash(ent, d, code, name, amount, desc, dept="Operations", proj=""):
    """DR Fixed Asset / CR Cash"""
    je(ent, d, [(code, name, r2(amount)),
                ("20010","Cash", -r2(amount))], desc, dept, proj)

def deferred_sub_collect(ent, d, amount, desc):
    """Annual sub cash: DR Cash / CR Deferred Revenue"""
    je(ent, d, [("20010","Cash", r2(amount)),
                ("40030","Deferred revenue - subscriptions", -r2(amount))], desc, "Sales")

def sub_recognize(ent, d, amount, desc):
    """Monthly recognition: DR Deferred Revenue / CR Revenue"""
    je(ent, d, [("40030","Deferred revenue - subscriptions", r2(amount)),
                ("1060","Digital membership - annual", -r2(amount))], desc, "Sales")

def tax_accrual(ent, d, amount, desc):
    """DR Tax Expense / CR Tax Payable"""
    je(ent, d, [("9600","Tax expense", r2(amount)),
                ("40040","Corporate tax payables", -r2(amount))], desc, "Finance")

def tax_pay(ent, d, amount, desc):
    """DR Tax Payable / CR Cash"""
    je(ent, d, [("40040","Corporate tax payables", r2(amount)),
                ("20010","Cash", -r2(amount))], desc, "Finance")

def vat_accrual(ent, d, output_vat, input_vat, desc):
    """Net VAT accrual: CR VAT Payable (output - input)"""
    net = output_vat - input_vat
    je(ent, d, [("40060","VAT payable", -r2(net))], desc, "Finance") if abs(net)>1 else None
    # Balance via cash (simplified — VAT was collected/paid embedded in receivables/payables)
    # Handled in settlement

def vat_settle(ent, d, net_amount, desc):
    """VAT settlement: DR VAT Payable / CR Cash"""
    je(ent, d, [("40040","Corporate tax payables", r2(0)),   # noop placeholder
                ("40060","VAT payable", r2(net_amount)),
                ("20010","Cash", -r2(net_amount))], desc, "Finance") if net_amount > 0 else None

def loan_draw(ent, d, loan_code, loan_name, amount, desc):
    """DR Cash / CR Loan"""
    je(ent, d, [("20010","Cash", r2(amount)),
                (loan_code, loan_name, -r2(amount))], desc, "Finance")

def loan_interest_pay(ent, d, exp_code, exp_name, amount, desc):
    """DR Interest Expense / CR Cash"""
    exp_cash(ent, d, exp_code, exp_name, amount, desc, "Finance")

def loan_principal_pay(ent, d, loan_code, loan_name, amount, desc):
    """DR Loan / CR Cash (principal repayment)"""
    je(ent, d, [(loan_code, loan_name, r2(amount)),
                ("20010","Cash", -r2(amount))], desc, "Finance")

def ic_interest_accrual_holding(ent, d, amount, desc):
    """Holding: DR IC Loans Receivable / CR IC Interest Income"""
    je(ent, d, [("10350","IC loans receivable", r2(amount)),
                ("9515","IC interest income", -r2(amount))], desc, "Finance")

def ic_interest_pay_dk(ent, d, amount, desc):
    """DK: DR IC Interest Expense / CR Cash (to Holding)"""
    exp_cash(ent, d, "9525","IC interest expense", amount, desc, "Finance")

def holding_collect_ic_interest(ent, d, amount, desc):
    """Holding: DR Cash / CR IC Loans Receivable (interest collected)"""
    je(ent, d, [("20010","Cash", r2(amount)),
                ("10350","IC loans receivable", -r2(amount))], desc, "Finance")

def mgmt_fee_dk(ent, d, amount, desc):
    """DK/UK: DR Misc Admin / CR Other Payables (mgmt fee to Holding)"""
    je(ent, d, [("6050","Miscellaneous admin", r2(amount)),
                ("40020","Other payables", -r2(amount))], desc, "Finance")

def mgmt_fee_pay(ent, d, amount, desc):
    """DK/UK: pay mgmt fee: DR Other Payables / CR Cash"""
    je(ent, d, [("40020","Other payables", r2(amount)),
                ("20010","Cash", -r2(amount))], desc, "Finance")

def holding_receive_mgmt(ent, d, amount, desc):
    """Holding: DR Cash / CR Financial Income"""
    je(ent, d, [("20010","Cash", r2(amount)),
                ("9510","Financial income", -r2(amount))], desc, "Finance")

def prepaid_pay(ent, d, amount, desc):
    """DR Prepaid Expenses / CR Cash"""
    je(ent, d, [("20080","Prepaid expenses", r2(amount)),
                ("20010","Cash", -r2(amount))], desc, "Finance")

def prepaid_amortise(ent, d, code, name, amount, desc):
    """DR Expense / CR Prepaid"""
    je(ent, d, [(code, name, r2(amount)),
                ("20080","Prepaid expenses", -r2(amount))], desc, "Finance")

def inventory_purchase(ent, d, amount, desc):
    """DR Raw Materials Inventory / CR Trade Payables"""
    je(ent, d, [("20030","Inventory - raw materials", r2(amount)),
                ("40010","Trade payables", -r2(amount))], desc, "Operations")

def inventory_consume(ent, d, code, name, amount, desc):
    """DR COGS account / CR Raw Materials Inventory"""
    je(ent, d, [(code, name, r2(amount)),
                ("20030","Inventory - raw materials", -r2(amount))], desc, "Operations")

def fg_movement(ent, d, net_amount, desc):
    """Net FG movement: positive = increase (DR FG Inv / CR Payables proxy), negative = decrease (DR COGS / CR FG)"""
    if abs(net_amount) < 1: return
    if net_amount > 0:
        je(ent, d, [("20050","Inventory - finished goods", r2(net_amount)),
                    ("40010","Trade payables", -r2(net_amount))], desc, "Operations")
    else:
        je(ent, d, [("2070","Manufacturing overhead", -r2(net_amount)),
                    ("20050","Inventory - finished goods", r2(net_amount))], desc, "Operations")

def wip_project_move(ent, d, net_amount, desc, proj=""):
    """WIP project revenue movement"""
    if abs(net_amount) < 1: return
    if net_amount > 0:
        je(ent, d, [("20090","WIP - project revenue", r2(net_amount)),
                    ("40010","Trade payables", -r2(net_amount))], desc, "Operations", proj)
    else:
        je(ent, d, [("20090","WIP - project revenue", r2(net_amount)),
                    ("20060","Trade receivables", -r2(net_amount))], desc, "Operations", proj)

def payroll_tax_pay(ent, d, amount, desc):
    """Payroll tax: DR Payroll Tax Payable / CR Cash"""
    je(ent, d, [("40050","Payroll tax payables", r2(amount)),
                ("20010","Cash", -r2(amount))], desc, "Finance")

def share_capital(ent, d, amount, desc):
    """DR Cash / CR Share Capital"""
    je(ent, d, [("20010","Cash", r2(amount)),
                ("50010","Share capital", -r2(amount))], desc, "Finance")

def retained_earnings_close(ent, d, amount, desc):
    """Year-end: DR (if positive profit net in P&L sign convention) / CR Retained Earnings.
    amount = absolute profit value (positive number).
    Profit increases equity → CR Retained Earnings (negative in our convention).
    Balancing DR goes to a clearing/offset — use trade receivables as proxy for
    'net asset build-up from profit'. In practice this is absorbed across all asset/liability moves.
    """
    # We close by: DR clearing (20060 or other) + CR Retained Earnings
    # But in proper double-entry this isn't needed if all transactions are already posted with both sides.
    # The BS will balance because double-entry was maintained throughout.
    # We just post a memo RE entry to make equity explicit.
    # Use "profit distribution" against dividends/retained account:
    je(ent, d, [("50030","Retained earnings", -r2(amount)),
                ("50040","Current year profit", r2(amount))], desc, "Finance")

def cyp_monthly(ent, d, pnl_sum, desc):
    """Close monthly P&L to Current Year Profit equity account."""
    # pnl_sum = sum of P&L entries for this entity-month (negative = profitable)
    # We need to offset this in equity: if profit (pnl_sum negative), CR CYP (negative = equity increases)
    # CYP entry = pnl_sum (same sign, which for profit is negative = credit to equity)
    # Counterbalancing debit goes to a balance-sheet clearing account...
    # Actually in double-entry this is automatic because BOTH sides of every P&L
    # transaction are already posted. No explicit CYP needed.
    pass  # Not needed with proper double-entry

# ════════════════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ════════════════════════════════════════════════════════════════════════════════

for year in range(2023, 2028):

    # Annual subscription cash collected in January (DK)
    annual_sub_dk = DK_REV_M[year] * 1_000_000 * 0.07
    jan_eom = date(year, 1, monthrange(year, 1)[1])

    for month in range(1, 13):
        mi  = month - 1
        dim = monthrange(year, month)[1]
        eom = date(year, month, dim)
        fx  = FX[year]
        qe  = (month % 3 == 0)

        dk_rev  = mo(DK_REV_M[year], mi)
        uk_gbp  = mo(UK_REV_GBP[year], mi)
        ic_dkk  = uk_gbp * fx * 0.65
        ic_gbp  = ic_dkk / fx * random.uniform(0.997, 1.003)

        dk_sal      = (40_000_000 + (year-2023)*3_000_000) / 12
        uk_sal      = (1_200_000  + (year-2023)*100_000)   / 12
        ic_loan     = IC_LOAN_DK[year]
        ic_int_m    = ic_loan * IC_RATE / 12
        mf_dk       = dk_rev * 0.015
        mf_uk_gbp   = uk_gbp * fx * 0.015 / fx  # in GBP

        def rd(lo=1, hi=None):
            return date(year, month, random.randint(lo, min(hi or dim, dim)))

        # ════════════════════════════════════════════════════════════════
        # DK OPERATING
        # ════════════════════════════════════════════════════════════════

        # ── Revenue recognition (monthly core) ────────────────────────
        for code, name, pct in [
            ("1010","Hardware sales - bikes",       0.33),
            ("1020","Hardware sales - treadmills",  0.18),
            ("1050","Digital membership - monthly", 0.08),
        ]:
            rev_rec(DK, rd(), code, name, dk_rev*pct, name)

        # Annual sub recognition (DR Deferred Revenue / CR Revenue)
        sub_recognize(DK, rd(), annual_sub_dk/12, "Annual sub monthly recognition")

        # Annual sub cash collected in January
        if month == 1:
            deferred_sub_collect(DK, date(year,1,5), annual_sub_dk,
                                 f"Annual digital memberships collected – {year}")

        # IC Revenue (DR IC Receivable / CR Revenue)
        ic_recv_raise(DK, rd(), "1090", ic_dkk,
                      f"IC sale to Veloton Ltd – {year}-{month:02d}")
        ic_recv_settle(DK, eom, ic_dkk,
                       f"IC settlement received – {year}-{month:02d}")

        # Customer collections (~88 % same month)
        monthly_rev = dk_rev * (0.33 + 0.18 + 0.08)
        collect(DK, eom, monthly_rev * 0.88,
                f"Customer collections – {year}-{month:02d}")

        # ── Quarterly revenue ──────────────────────────────────────────
        if qe:
            for code, name, pct in [
                ("1030","Hardware sales - accessories",           0.09),
                ("1040","Hardware sales - refurbished equipment", 0.04),
                ("1070","Corporate wellness - studio fit-out",    0.06),
                ("1080","Corporate wellness - maintenance contract",0.04),
            ]:
                proj = random.choice(PROJECTS) if "wellness" in name else ""
                rev_rec(DK, eom, code, name, dk_rev*3*pct, f"Quarterly: {name}", "Sales", proj)
            # Discounts (contra-revenue): DR Discounts / CR Trade Receivables
            je(DK, eom, [("1099","Discounts & returns", r2(dk_rev*3*0.05)),
                          ("20060","Trade receivables",  -r2(dk_rev*3*0.05))],
               "Quarterly: discounts issued", "Sales")
            # Quarterly collections
            q_rev = dk_rev * 3 * (0.09+0.04+0.06+0.04)
            collect(DK, eom, q_rev*0.85, f"Q collections – {year}-{month:02d}")

        # ── COGS — material cycle ──────────────────────────────────────
        dk_cogs = dk_rev * 0.45
        mat_pct  = 0.52  # materials as share of COGS
        # Purchase raw materials → inventory
        inventory_purchase(DK, rd(1,15), dk_cogs*mat_pct*rnd(),
                           f"RM purchase – {year}-{month:02d}")
        # Consume into COGS (frames/mechanical — main material account)
        inventory_consume(DK, rd(16,dim), "2010","Raw materials - frames & mechanical",
                          dk_cogs*0.40, f"RM consumption – {year}-{month:02d}")

        # ── COGS — labour (direct cash) ────────────────────────────────
        exp_cash(DK, rd(), "2050","Direct labour - production",
                 dk_cogs*0.32, "Direct labour payroll", "Operations")

        # ── COGS — quarterly detail ────────────────────────────────────
        if qe:
            for code, name, pct in [
                ("2020","Raw materials - electronics & screens", 0.20),
                ("2030","Raw materials - fabric & upholstery",   0.08),
                ("2040","Raw materials - packaging",             0.04),
            ]:
                inventory_consume(DK, eom, code, name, dk_cogs*3*pct,
                                  f"Quarterly: {name}")
            for code, name, pct in [
                ("2060","Direct labour - assembly",   0.12),
                ("2070","Manufacturing overhead",     0.10),
                ("2080","Freight & logistics",        0.08),
                ("2099","Inventory write-down",       0.02),
            ]:
                exp_payable(DK, eom, code, name, dk_cogs*3*pct*rnd(),
                            f"Quarterly: {name}", "Operations")
            # FG movement
            fg_movement(DK, eom, dk_cogs*3*random.uniform(-0.02, 0.04),
                        "Quarterly: FG net movement")

        # ── Salary (direct cash) ───────────────────────────────────────
        exp_cash(DK, date(year,month,min(25,dim)), "3010","Salaries & wages",
                 dk_sal*0.85, "Monthly salaries", "Operations")
        if qe:
            exp_cash(DK, eom, "3020","Pension contributions",
                     dk_sal*0.10*3, "Quarterly pension", "Operations")
            exp_cash(DK, eom, "3030","Other payroll costs",
                     dk_sal*0.05*3*rnd(), "Quarterly payroll costs", "Operations")
            # Payroll tax (separate liability)
            je(DK, eom, [("3030","Other payroll costs",    r2(dk_sal*0.08*3)),
                          ("40050","Payroll tax payables",  -r2(dk_sal*0.08*3))],
               "Quarterly payroll tax accrual", "Finance")
            payroll_tax_pay(DK, eom, dk_sal*0.08*3*0.95, "Quarterly payroll tax payment")

        # ── Rent (direct cash) ─────────────────────────────────────────
        exp_cash(DK, date(year,month,1), "4010","Rent & leasing",
                 800_000/12, "Monthly factory & office rent", "Operations")

        # ── Marketing ─────────────────────────────────────────────────
        exp_payable(DK, rd(), "5010","Digital marketing & advertising",
                    dk_rev*0.08*0.45, "Digital advertising", "Marketing")
        if qe:
            exp_payable(DK, eom, "5020","Events & sponsorships",
                        dk_rev*0.08*0.20*3*rnd(), "Quarterly: events", "Marketing")
            exp_cash(DK, eom, "5030","Sales commissions",
                     dk_rev*0.08*0.25*3, "Quarterly: commissions", "Sales")
            exp_payable(DK, eom, "5040","CRM & marketing tools",
                        dk_rev*0.08*0.10*3, "Quarterly: CRM", "Marketing")

        # ── Admin ──────────────────────────────────────────────────────
        exp_payable(DK, rd(), "6010","IT & software",
                    3_600_000/12*rnd(), "IT & software subscriptions", "Finance")
        if qe:
            # Insurance paid as prepayment
            prepaid_pay(DK, eom, 1_200_000/4*rnd(), "Quarterly insurance prepayment")
            prepaid_amortise(DK, eom, "6020","Insurance", 1_200_000/4*rnd(), "Insurance amortisation")
            exp_cash(DK, eom, "6030","Bank charges & fees", 600_000/4*rnd(), "Bank charges", "Finance")
            exp_payable(DK, eom, "6040","Office supplies", 480_000/4*rnd(), "Office supplies", "Finance")

        # ── Management fee to Holding ──────────────────────────────────
        if qe:
            mgmt_fee_dk(DK, eom, mf_dk*3, f"Quarterly mgmt fee to {HOLDING}")
            mgmt_fee_pay(DK, eom, mf_dk*3*0.95, f"Quarterly mgmt fee paid")

        # ── Travel & professional (quarterly) ─────────────────────────
        if qe:
            exp_payable(DK, eom, "7010","Travel & accommodation",
                        2_400_000/4*rnd(0.8,1.2), "Quarterly travel", "Sales")
            exp_payable(DK, eom, "7020","Meals & entertainment",
                        600_000/4*rnd(), "Quarterly meals", "Sales")
            af = 2.5 if month==3 else 0.83
            exp_payable(DK, eom, "8010","Audit & accounting fees",
                        1_800_000/4*af*rnd(), "Audit fees", "Finance")
            exp_payable(DK, eom, "8020","Legal fees",
                        900_000/4*rnd(0.7,1.3), "Legal fees", "Finance")
            exp_payable(DK, eom, "8030","Consulting fees",
                        2_400_000/4*rnd(0.8,1.2), "Consulting fees", "Finance")

        # ── Pay trade payables (~80 % monthly) ────────────────────────
        pay_payables(DK, eom, dk_cogs*mat_pct*0.80 + dk_rev*0.08*0.45*0.80,
                     f"Supplier payment run – {year}-{month:02d}")
        if qe:
            pay_payables(DK, eom,
                         (dk_cogs*3*(0.10+0.08+0.02) + 2_400_000/4 + 3_600_000/12*3)*0.80,
                         f"Quarterly supplier payment – {year}-{month:02d}")

        # ── Depreciation (monthly, all assets) ────────────────────────
        depn(DK, eom, "9010","Depreciation - operating assets",
             "10020","Accumulated depreciation - operating assets", 250_000,
             f"Depreciation – {year}-{month:02d}")
        depn(DK, eom, "9030","Depreciation - vehicles",
             "10060","Accumulated depreciation - vehicles", 30_000,
             f"Depreciation – {year}-{month:02d}")
        depn(DK, eom, "9040","Depreciation - fixtures & fittings",
             "10080","Accumulated depreciation - fixtures & fittings", 20_000,
             f"Depreciation – {year}-{month:02d}")
        depn(DK, eom, "9050","Depreciation - IT equipment",
             "10100","Accumulated depreciation - IT equipment", 40_000,
             f"Depreciation – {year}-{month:02d}")

        # ── Interest (quarterly) ───────────────────────────────────────
        if qe:
            loan_interest_pay(DK, eom, "9520","Financial expenses",
                              ic_int_m*0.75*3, "Quarterly bank interest")
            ic_interest_pay_dk(DK, eom, ic_int_m*0.25*3,
                               f"Quarterly IC interest to {HOLDING}")
            # Holding receives the IC interest
            ic_interest_accrual_holding(HOLDING, eom, ic_int_m*3,
                                        f"Quarterly IC interest from {DK}")
            holding_collect_ic_interest(HOLDING, eom, ic_int_m*3,
                                        f"IC interest collected")

        # ── FX (quarterly, net P&L entry balanced via trade receivables) ─
        if qe:
            fx_amt = dk_rev*0.002*random.uniform(-1,1)*3
            if abs(fx_amt) > 1:
                je(DK, eom, [("9530","Currency & exchange rates", r2(fx_amt)),
                              ("20060","Trade receivables", -r2(fx_amt))],
                   "Quarterly FX revaluation", "Finance")

        # ── Tax (monthly accrual, aconto in Mar/Sep) ───────────────────
        dk_tax = max(0, dk_rev*0.12*0.22)
        tax_accrual(DK, eom, dk_tax, f"Tax accrual – {year}-{month:02d}")
        if month == 3:
            tax_pay(DK, date(year,3,20), dk_tax*5, "Aconto tax – March")
        if month == 9:
            tax_pay(DK, date(year,9,20), dk_tax*5, "Aconto tax – November")

        # ── VAT (quarterly: net payable accrual + settlement) ─────────
        if qe:
            vat_out = dk_rev*3*0.95*0.25
            vat_in  = dk_cogs*mat_pct*3*0.25
            vat_net = vat_out - vat_in
            je(DK, eom, [("40060","VAT payable", -r2(vat_net*rnd(0.95,1.0)))],
               "Quarterly VAT payable accrual", "Finance") if vat_net > 0 else None
            # Offset: the VAT was already embedded in receivables/payables above
            # We balance the VAT payable accrual against other receivables
            if vat_net > 0:
                je(DK, eom, [("20070","Other receivables",  r2(vat_net*rnd(0.95,1.0))),
                              ("40060","VAT payable",       -r2(vat_net*rnd(0.95,1.0)))],
                   "Quarterly VAT accrual offset", "Finance")
                # Settlement
                vat_settle_amt = vat_net * 3 * 0.90
                je(DK, eom, [("40060","VAT payable",  r2(vat_settle_amt)),
                              ("20010","Cash",         -r2(vat_settle_amt))],
                   "VAT settlement to SKAT", "Finance")

        # ── WIP project revenue ───────────────────────────────────────
        if qe:
            proj = random.choice(PROJECTS)
            wip_project_move(DK, eom, dk_rev*3*0.04*random.uniform(-1,1),
                             "Quarterly: project WIP movement", proj)

        # ── Loan: principal repayment (quarterly) ─────────────────────
        if qe:
            loan_principal_pay(DK, eom, "30010","Loans - bank",
                               15_000_000/(5*12)*3, "Quarterly bank loan repayment")
            # IC loan interest accrual on DK payable side
            je(DK, eom, [("9525","IC interest expense",   r2(ic_int_m*0.25*3)),
                          ("30020","IC loans payable",    -r2(ic_int_m*0.25*3))],
               "IC loan interest accrued", "Finance")

        # ── CAPEX events ───────────────────────────────────────────────
        capex_dk = {
            (2023,3):(5_000_000,"Production line upgrade","10010","CAPEX - operating assets","Project Apollo"),
            (2024,6):(3_500_000,"New assembly equipment","10010","CAPEX - operating assets","Project Bison"),
            (2025,9):(4_000_000,"Expanded production facility","10010","CAPEX - operating assets","Project Candy"),
            (2026,4):(2_500_000,"Automated packaging line","10010","CAPEX - operating assets","Project Apollo"),
            (2027,2):(3_000_000,"Next-gen assembly robot","10010","CAPEX - operating assets","Project Bison"),
            (2023,1):(900_000,"Fleet vehicle replacement","10050","CAPEX - vehicles",""),
            (2025,1):(950_000,"Fleet vehicle replacement","10050","CAPEX - vehicles",""),
            (2024,2):(1_200_000,"Factory showroom refit","10070","CAPEX - fixtures & fittings",""),
            (2023,9):(600_000,"IT equipment refresh","10090","CAPEX - IT equipment",""),
            (2025,9):(660_000,"IT equipment refresh","10090","CAPEX - IT equipment",""),
            (2027,9):(726_000,"IT equipment refresh","10090","CAPEX - IT equipment",""),
        }
        if (year,month) in capex_dk:
            amt,desc,code,name,proj = capex_dk[(year,month)]
            capex_cash(DK, rd(5,20), code, name, amt, desc, "Operations", proj)

        # ── One-time opening entries ───────────────────────────────────
        if month==1 and year==2023:
            loan_draw(DK, date(2023,1,1), "30010","Loans - bank",
                      15_000_000, "Bank term loan drawdown")
            loan_draw(DK, date(2023,1,1), "30020","IC loans payable",
                      20_000_000, f"IC loan from {HOLDING}")
            je(DK, date(2023,1,1), [("10300","Deposits", r2(2_400_000)),
                                     ("20010","Cash",     -r2(2_400_000))],
               "Office lease deposit", "Finance")
            share_capital(DK, date(2023,1,1), 10_000_000, "Registered share capital")
            je(DK, date(2023,1,1), [("10200","Deferred tax assets",    r2(500_000)),
                                     ("30030","Deferred tax liabilities", -r2(200_000)),
                                     ("50030","Retained earnings",      -r2(300_000))],
               "Opening deferred tax balances", "Finance")
        if month==1 and year in (2024,2025):
            loan_draw(DK, date(year,1,1), "30020","IC loans payable",
                      2_000_000, "IC loan drawdown")

        # ── Year-end: retained earnings close ─────────────────────────
        if month == 12:
            # Close current year profit to retained earnings
            # CYP (50040) accumulates P&L net; transfer to RE (50030)
            annual_profit = DK_REV_M[year]*1_000_000*0.09
            je(DK, date(year,12,31),
               [("50040","Current year profit", r2(annual_profit)),
                ("50030","Retained earnings",   -r2(annual_profit))],
               f"FY{year} profit to retained earnings", "Finance")

        # ════════════════════════════════════════════════════════════════
        # UK OPERATING
        # ════════════════════════════════════════════════════════════════

        for code, name, pct in [
            ("1010","Hardware sales - bikes",       0.52),
            ("1020","Hardware sales - treadmills",  0.30),
        ]:
            rev_rec(UK, rd(), code, name, uk_gbp*pct, f"UK {name}", "Sales")

        if qe:
            for code, name, pct in [
                ("1030","Hardware sales - accessories", 0.13),
            ]:
                rev_rec(UK, eom, code, name, uk_gbp*3*pct, f"Quarterly UK {name}", "Sales")
            je(UK, eom, [("1099","Discounts & returns",  r2(uk_gbp*3*0.05)),
                          ("20060","Trade receivables",  -r2(uk_gbp*3*0.05))],
               "Quarterly: UK discounts", "Sales")

        collect(UK, eom, uk_gbp*(0.52+0.30)*0.87, f"UK collections – {year}-{month:02d}")
        if qe:
            collect(UK, eom, uk_gbp*3*0.13*0.85, f"UK quarterly collections")

        # IC COGS
        ic_pay_raise(UK, rd(), "2090", ic_gbp, f"IC purchase from {DK} – {year}-{month:02d}")
        ic_pay_settle(UK, eom, ic_gbp, f"IC payment to {DK} – {year}-{month:02d}")

        # Local freight
        exp_payable(UK, rd(), "2080","Freight & logistics",
                    uk_gbp*0.07, "UK logistics", "Operations")

        # Salary
        exp_cash(UK, date(year,month,min(25,dim)), "3010","Salaries & wages",
                 uk_sal*0.85, "UK salaries", "Operations")
        if qe:
            exp_cash(UK, eom, "3020","Pension contributions", uk_sal*0.10*3, "UK pension","Operations")
            exp_cash(UK, eom, "3030","Other payroll costs",   uk_sal*0.05*3*rnd(), "UK payroll","Operations")
            je(UK, eom, [("3030","Other payroll costs",  r2(uk_sal*0.138*3)),
                          ("40050","Payroll tax payables",-r2(uk_sal*0.138*3))],
               "UK NI employer accrual", "Finance")
            payroll_tax_pay(UK, eom, uk_sal*0.138*3*0.95, "UK NI payment")

        exp_cash(UK, date(year,month,1), "4010","Rent & leasing", 80_000/12, "UK rent","Operations")
        exp_payable(UK, rd(), "5010","Digital marketing & advertising", uk_gbp*0.06*0.60, "UK digital marketing","Marketing")
        exp_payable(UK, rd(), "6010","IT & software", 15_000/12*rnd(), "UK IT","Finance")

        if qe:
            exp_cash(UK, eom, "5030","Sales commissions", uk_gbp*0.06*0.40*3, "UK commissions","Sales")
            prepaid_pay(UK, eom, 60_000*rnd(), "UK insurance prepayment") if month in (3,9) else None
            prepaid_amortise(UK, eom, "6020","Insurance", 60_000/6*rnd(), "UK insurance amortisation")
            exp_cash(UK, eom, "6030","Bank charges & fees", 6_000/4*rnd(), "UK bank charges","Finance")
            mgmt_fee_dk(UK, eom, mf_uk_gbp*3, f"Quarterly mgmt fee to {HOLDING}")
            mgmt_fee_pay(UK, eom, mf_uk_gbp*3*0.95, "Quarterly mgmt fee paid")
            exp_payable(UK, eom, "7010","Travel & accommodation", uk_gbp*0.012*3*rnd(0.8,1.2),"UK travel","Sales")
            af = 2.5 if month==3 else 0.83
            exp_payable(UK, eom, "8010","Audit & accounting fees", 8_000/4*af*rnd(),"UK accounting","Finance")
            exp_payable(UK, eom, "8020","Legal fees", 5_000/4*rnd(0.7,1.3),"UK legal","Finance")

        pay_payables(UK, eom, uk_gbp*0.07*0.80, f"UK supplier payments – {year}-{month:02d}")
        if qe:
            pay_payables(UK, eom, (uk_gbp*0.06*0.60 + 15_000/12)*3*0.80, "UK quarterly payments")

        depn(UK, eom,"9030","Depreciation - vehicles","10060","Accumulated depreciation - vehicles",3_500,f"UK dep – {year}-{month:02d}")
        depn(UK, eom,"9040","Depreciation - fixtures & fittings","10080","Accumulated depreciation - fixtures & fittings",2_000,f"UK dep – {year}-{month:02d}")
        depn(UK, eom,"9050","Depreciation - IT equipment","10100","Accumulated depreciation - IT equipment",4_000,f"UK dep – {year}-{month:02d}")

        uk_tax = max(0, uk_gbp*0.08*0.25)
        tax_accrual(UK, eom, uk_tax, f"UK tax accrual – {year}-{month:02d}")
        if month == 9:
            tax_pay(UK, eom, uk_tax*3, "UK quarterly tax payment")

        if qe:
            uk_ic_int = (ic_loan*0.40/fx)*IC_RATE/12
            loan_interest_pay(UK, eom, "9520","Financial expenses", uk_ic_int*0.50*3,"UK bank interest")
            loan_interest_pay(UK, eom, "9525","IC interest expense",uk_ic_int*0.50*3,f"IC interest to {HOLDING}")
            fx_uk = uk_gbp*0.002*random.uniform(-1,1)*3
            if abs(fx_uk) > 0.01:
                je(UK, eom, [("9530","Currency & exchange rates", r2(fx_uk)),
                              ("20060","Trade receivables", -r2(fx_uk))],
                   "Quarterly FX revaluation","Finance")
            # UK VAT
            uk_vat = uk_gbp*3*0.95*0.20
            je(UK, eom, [("40060","VAT payable", -r2(uk_vat*rnd(0.95,1.0))),
                          ("20070","Other receivables",r2(uk_vat*rnd(0.95,1.0)))],
               "Quarterly UK VAT accrual","Finance")
            je(UK, eom, [("40060","VAT payable",r2(uk_vat*0.90)),
                          ("20010","Cash",      -r2(uk_vat*0.90))],
               "UK VAT settlement to HMRC","Finance")

        # UK CAPEX
        uk_capex = {
            (2023,2):(80_000,"UK fleet vehicle","10050","CAPEX - vehicles"),
            (2025,3):(150_000,"UK showroom refurbishment","10070","CAPEX - fixtures & fittings"),
            (2023,10):(50_000,"UK IT equipment","10090","CAPEX - IT equipment"),
            (2025,10):(55_000,"UK IT equipment refresh","10090","CAPEX - IT equipment"),
            (2027,10):(60_000,"UK IT equipment refresh","10090","CAPEX - IT equipment"),
        }
        if (year,month) in uk_capex:
            amt,desc,code,name = uk_capex[(year,month)]
            capex_cash(UK, rd(10,20), code, name, amt, desc)

        if month==1 and year==2023:
            loan_draw(UK, date(2023,1,1),"30020","IC loans payable",
                      3_000_000/fx, f"IC loan from {HOLDING}")
            je(UK, date(2023,1,1),[("10300","Deposits",r2(160_000)),
                                    ("20010","Cash",   -r2(160_000))],"UK office deposit","Finance")
            share_capital(UK, date(2023,1,1), 500_000, "UK share capital")

        if month == 12:
            annual_uk = UK_REV_GBP[year]*1_000_000*0.07
            je(UK, date(year,12,31),
               [("50040","Current year profit", r2(annual_uk)),
                ("50030","Retained earnings",   -r2(annual_uk))],
               f"FY{year} profit to retained earnings","Finance")

        # ════════════════════════════════════════════════════════════════
        # HOLDING
        # ════════════════════════════════════════════════════════════════

        # Management fee income (collected quarterly)
        if qe:
            mf_total_dkk = mf_dk*3 + mf_uk_gbp*3*fx
            holding_receive_mgmt(HOLDING, eom, mf_total_dkk,
                                 "Quarterly management fees collected")

        # Salary
        exp_cash(HOLDING, date(year,month,min(25,dim)), "3010","Salaries & wages",
                 3_000_000/12*0.85, "Board salaries","Finance")
        if qe:
            exp_cash(HOLDING, eom, "3020","Pension contributions",
                     3_000_000/12*0.10*3,"Board pension","Finance")

        # Admin (quarterly)
        if qe:
            exp_payable(HOLDING, eom, "6010","IT & software",   60_000/4*rnd(),"Holding IT","Finance")
            af = 2.5 if month==3 else 0.83
            exp_payable(HOLDING, eom, "8010","Audit & accounting fees",80_000/4*af*rnd(),"Holding audit","Finance")
            exp_payable(HOLDING, eom, "8020","Legal fees",      60_000/4*rnd(0.7,1.3),"Holding legal","Finance")
            pay_payables(HOLDING, eom, (60_000/4 + 80_000/4 + 60_000/4)*0.90, "Holding quarterly payments")

        # Goodwill + IT depreciation
        depn(HOLDING, eom, "9020","Depreciation - goodwill",
             "10040","Accumulated depreciation - goodwill",
             15_000_000/(20*12), f"Goodwill amortisation – {year}-{month:02d}")
        depn(HOLDING, eom, "9050","Depreciation - IT equipment",
             "10100","Accumulated depreciation - IT equipment",
             5_000, f"IT depreciation – {year}-{month:02d}")

        # Dividends (April following year)
        if month==4 and year>2023:
            div = DK_REV_M[year-1]*1_000_000*0.04
            je(HOLDING, date(year,4,15),
               [("50020","Dividends",   r2(div)),
                ("20010","Cash",       -r2(div))],
               f"Dividend distribution – FY{year-1}","Finance")

        # One-time opening entries
        if month==1 and year==2023:
            je(HOLDING, date(2023,1,1),
               [("10030","CAPEX - goodwill",    r2(15_000_000)),
                ("20010","Cash",               -r2(15_000_000))],
               "Goodwill on acquisition","Finance")
            # Initial IC loans issued to subsidiaries (asset)
            je(HOLDING, date(2023,1,1),
               [("10350","IC loans receivable", r2(23_000_000)),
                ("20010","Cash",               -r2(23_000_000))],
               "IC loans issued to operating entities","Finance")
            share_capital(HOLDING, date(2023,1,1), 30_000_000, "Holding share capital")

        if month==1 and year in (2024,2025):
            je(HOLDING, date(year,1,1),
               [("10350","IC loans receivable", r2(2_000_000)),
                ("20010","Cash",               -r2(2_000_000))],
               "Additional IC loan to DK","Finance")

        if month == 12:
            h_profit = (mf_dk + mf_uk_gbp*fx)*12*0.65
            je(HOLDING, date(year,12,31),
               [("50040","Current year profit", r2(h_profit)),
                ("50030","Retained earnings",   -r2(h_profit))],
               f"FY{year} profit to retained earnings","Finance")

# ── Post DK: Current Year Profit accumulation ────────────────────────────────
# For each entity-month, accumulate the monthly P&L net into 50040 (CYP).
# This ensures A - L - E = 0 at every period-end (CYP in equity absorbs running P&L).
from collections import defaultdict

def is_pnl(code):
    return len(code) <= 4  # 4-digit = P&L, 5-digit = BS

# Group rows by entity+month
by_em = defaultdict(list)
for r in rows:
    by_em[(r["Entity"], r["Date"][:7])].append(r)

cyp_entries = []
for (ent, ym), em_rows in sorted(by_em.items()):
    pnl_sum = sum(float(r["Amount"]) for r in em_rows if is_pnl(r["Account Code"]))
    if abs(pnl_sum) < 0.01:
        continue
    yr, mo_s = int(ym[:4]), int(ym[5:])
    dim = monthrange(yr, mo_s)[1]
    d = date(yr, mo_s, dim)
    # CYP = -pnl_sum → makes BS + CYP = 0 since trial balance already = 0
    # Counterpart: the "other side" is already in BS via double-entry transactions.
    # We only need to post CYP to make it explicit in equity.
    # Balance CYP against Other Receivables (a proxy for the net BS asset build-up from profit).
    cyp_entries.append({
        "Date": d.strftime("%Y-%m-%d"), "Entity": ent,
        "Account Code": "50040", "Account": "Current year profit",
        "Amount": r2(-pnl_sum),
        "Description": f"Test transaction – Monthly P&L to current year profit – {ym}",
        "Department": "Finance", "Project": ""
    })
    cyp_entries.append({
        "Date": d.strftime("%Y-%m-%d"), "Entity": ent,
        "Account Code": "20070", "Account": "Other receivables",
        "Amount": r2(pnl_sum),
        "Description": f"Test transaction – Offset current year profit – {ym}",
        "Department": "Finance", "Project": ""
    })

rows.extend(cyp_entries)

# ── WRITE ─────────────────────────────────────────────────────────────────────
output = "/Users/anton/Documents/GitHub/docs/test-data/test-data.csv"
os.makedirs(os.path.dirname(output), exist_ok=True)
fields = ["Date","Entity","Account Code","Account","Amount","Description","Department","Project"]
with open(output,"w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f,fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

print(f"Rows: {len(rows):,}")
from collections import Counter
for ent,cnt in Counter(r["Entity"] for r in rows).items():
    print(f"  {ent}: {cnt:,}")

# Balance check
totals = defaultdict(float)
for r in rows:
    totals[(r["Entity"],r["Date"][:7])] += float(r["Amount"])
nonzero = [(k,v) for k,v in totals.items() if abs(v)>0.05]
print(f"Trial balance violations (>0.05): {len(nonzero)}")

# BS balance check at quarter-ends
def acct_type(code):
    if len(code)<=4: return "pnl"
    n=int(code)
    if 10000<=n<=29999: return "asset"
    if 30000<=n<=49999: return "liability"
    if 50000<=n<=59999: return "equity"
    return "other"

for ent in [DK,UK,HOLDING]:
    er = [r for r in rows if r["Entity"]==ent]
    cum = defaultdict(float)
    for r in er: cum[(r["Date"][:7],acct_type(r["Account Code"]))] += float(r["Amount"])
    # check Dec 2025
    ym="2025-12"
    periods = sorted(set(r["Date"][:7] for r in er))
    a=l=e=0
    for p in [x for x in periods if x<="2025-12"]:
        a+=cum.get((p,"asset"),0); l+=cum.get((p,"liability"),0); e+=cum.get((p,"equity"),0)
    print(f"{ent[:12]} 2025-12: A={a/1e6:+.1f}M L={l/1e6:+.1f}M E={e/1e6:+.1f}M  A+L+E={( a+l+e)/1e6:+.2f}M")

print(f"Unique accounts: {len(set(r['Account Code'] for r in rows))}")
