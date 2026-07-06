"""
Fix test-data.csv:

1. IC Interest — align Holding's monthly income so it equals
   ApS expense (DKK) + Ltd expense × 8.5 DKK/GBP per year.

2. CAPEX — add missing Jan 2023 opening balances for fixtures &
   fittings, IT equipment, and vehicles across all entities, then
   update or add the annual roll-forward entries in Jan 2024-2027.

3. IC Receivables — add a matching 3320 IC receivables account in
   Veloton ApS for every 4320 IC payables entry in Veloton Ltd.
   Amounts are converted GBP → DKK using year-specific FX rates
   derived from the IC Revenue / IC COGS ratio.
"""

INPUT  = 'test-data/test-data-original-backup.csv'
OUTPUT = 'test-data/test-data.csv'

# ---------------------------------------------------------------------------
# 1. IC INTEREST
#    The Holding's interest income and corresponding cash are left at their
#    original values. The rate mismatch between Holding income and ApS+Ltd
#    expenses is an FX/rate difference that belongs in the FX currency line
#    of the group consolidation model in Francis — not in the entity data.
# ---------------------------------------------------------------------------
HOLDING_INCOME_BY_YEAR = {}   # no changes

# ---------------------------------------------------------------------------
# 2a. NEW ROWS — inserted after the last line for that date.
#     Each entry: (date, account, amount, entity)
#     Department defaults to Finance throughout.
# ---------------------------------------------------------------------------
NEW_ROWS = {

    '2023-01-01': [
        # Fixtures & fittings opening balances (20 000/month dep → 5yr life)
        ('2023-01-01', '3161 CAPEX - fixtures & fittings, addition', '1200000,00', 'Veloton ApS'),
        ('2023-01-01', '3160 CAPEX - fixtures & fittings',           '120000,00',  'Veloton Ltd'),
        # IT equipment opening balances (40 000 / 4 000 / 5 000 per month → 5yr)
        ('2023-01-01', '3181 CAPEX - IT equipment, addition', '2400000,00', 'Veloton ApS'),
        ('2023-01-01', '3180 CAPEX - IT equipment',           '240000,00',  'Veloton Ltd'),
        # Vehicles opening balance for Ltd (3 500/month dep → 5yr life)
        ('2023-01-01', '3140 CAPEX - vehicles', '210000,00', 'Veloton Ltd'),
        # Retained earnings credits — opening balance offsets for the new CAPEX assets above.
        # These assets existed pre-model and were previously funded by equity.
        # Holding is excluded: dep without gross CAPEX was the original state and it balanced.
        ('2023-01-01', '5030 Retained earnings', '-3600000,00', 'Veloton ApS'),  # 1 200K fixtures + 2 400K IT
        ('2023-01-01', '5030 Retained earnings', '-570000,00',  'Veloton Ltd'),  # 120K fixtures + 240K IT + 210K vehicles (GBP)
    ],

    '2024-01-01': [
        # Veloton Ltd bank loan drawdown — eliminates all negative cash months.
        # 831K clears Apr-Nov 2024. Extra 180K covers Dec 2024-2027 (worst = -179 358 GBP).
        ('2024-01-01', '3900 Cash',       '1011000,00',  'Veloton Ltd'),
        ('2024-01-01', '4110 Bank loans', '-1011000,00', 'Veloton Ltd'),
        # Fixtures ApS — roll forward Jan-2023 opening (1 200K)
        ('2024-01-01', '3160 CAPEX - fixtures & fittings, opening', '1200000,00',  'Veloton ApS'),
        ('2024-01-01', '3161 CAPEX - fixtures & fittings, addition', '-1200000,00', 'Veloton ApS'),
        # Fixtures Ltd — roll forward Jan-2023 opening (120K)
        ('2024-01-01', '3160 CAPEX - fixtures & fittings, opening', '120000,00',   'Veloton Ltd'),
        ('2024-01-01', '3161 CAPEX - fixtures & fittings, addition', '-120000,00',  'Veloton Ltd'),
        # IT Ltd — Jan-2023 240K + Oct-2023 50K = 290K
        ('2024-01-01', '3180 CAPEX - IT equipment, opening', '290000,00',  'Veloton Ltd'),
        ('2024-01-01', '3181 CAPEX - IT equipment, addition', '-290000,00', 'Veloton Ltd'),
        # Vehicles Ltd — Jan-2023 210K + Feb-2023 80K = 290K
        ('2024-01-01', '3140 CAPEX - vehicles, opening', '290000,00',  'Veloton Ltd'),
        ('2024-01-01', '3141 CAPEX - vehicles, addition', '-290000,00', 'Veloton Ltd'),
    ],

    '2025-01-01': [
        # Veloton ApS bank loan drawdown — eliminates all negative cash months.
        # 3.2M clears Jul-Oct and Dec 2025. Extra 2.795M covers Nov 2025-2027 (worst = -2 794 722 DKK).
        # Because this injection carries forward, it also clears Nov 2026 and Nov 2027.
        ('2025-01-01', '3900 Cash',       '5995000,00',  'Veloton ApS'),
        ('2025-01-01', '4110 Bank loans', '-5995000,00', 'Veloton ApS'),
        # Veloton Ltd bank loan drawdown — keeps cash ≥ 0 except Dec 2025
        # Cumulative Ltd deficit grows; inject 1.686M GBP so only Dec 2025 is negative.
        ('2025-01-01', '3900 Cash',       '1686000,00',  'Veloton Ltd'),
        ('2025-01-01', '4110 Bank loans', '-1686000,00', 'Veloton Ltd'),
        # Fixtures Ltd — unchanged from 2024 (still 120K)
        ('2025-01-01', '3160 CAPEX - fixtures & fittings, opening', '120000,00',   'Veloton Ltd'),
        ('2025-01-01', '3161 CAPEX - fixtures & fittings, addition', '-120000,00',  'Veloton Ltd'),
        # IT Ltd — unchanged from 2024 (still 290K)
        ('2025-01-01', '3180 CAPEX - IT equipment, opening', '290000,00',  'Veloton Ltd'),
        ('2025-01-01', '3181 CAPEX - IT equipment, addition', '-290000,00', 'Veloton Ltd'),
        # Vehicles Ltd — unchanged (still 290K)
        ('2025-01-01', '3140 CAPEX - vehicles, opening', '290000,00',  'Veloton Ltd'),
        ('2025-01-01', '3141 CAPEX - vehicles, addition', '-290000,00', 'Veloton Ltd'),
    ],

    '2026-01-01': [
        # Veloton ApS bank loan drawdown — keeps cash ≥ 0 except Nov 2026
        # Inject 13.52M DKK (cumulative with Jan-2025 injection = 16.72M DKK total shift).
        # Only Nov 2026 remains negative (-628 512 DKK).
        ('2026-01-01', '3900 Cash',       '13520000,00',  'Veloton ApS'),
        ('2026-01-01', '4110 Bank loans', '-13520000,00', 'Veloton ApS'),
        # Veloton Ltd bank loan drawdown — keeps cash ≥ 0 except Dec 2026
        # Inject 1.556M GBP (cumulative = 4.073M GBP total shift).
        # Only Dec 2026 remains negative (-167 185 GBP).
        ('2026-01-01', '3900 Cash',       '1556000,00',  'Veloton Ltd'),
        ('2026-01-01', '4110 Bank loans', '-1556000,00', 'Veloton Ltd'),
        # Fixtures Ltd — now 270K (120K + Mar-2025 150K)
        ('2026-01-01', '3160 CAPEX - fixtures & fittings, opening', '270000,00',   'Veloton Ltd'),
        ('2026-01-01', '3161 CAPEX - fixtures & fittings, addition', '-270000,00',  'Veloton Ltd'),
        # IT Ltd — now 345K (290K + Oct-2025 55K)
        ('2026-01-01', '3180 CAPEX - IT equipment, opening', '345000,00',  'Veloton Ltd'),
        ('2026-01-01', '3181 CAPEX - IT equipment, addition', '-345000,00', 'Veloton Ltd'),
        # Vehicles Ltd — unchanged (still 290K)
        ('2026-01-01', '3140 CAPEX - vehicles, opening', '290000,00',  'Veloton Ltd'),
        ('2026-01-01', '3141 CAPEX - vehicles, addition', '-290000,00', 'Veloton Ltd'),
    ],

    '2027-01-01': [
        # Veloton ApS bank loan drawdown — keeps cash ≥ 0 except Nov 2027
        # Inject 11.365M DKK (cumulative = 28.085M DKK total shift).
        # Only Nov 2027 remains negative (-373 904 DKK).
        ('2027-01-01', '3900 Cash',       '11365000,00',  'Veloton ApS'),
        ('2027-01-01', '4110 Bank loans', '-11365000,00', 'Veloton ApS'),
        # Veloton Ltd bank loan drawdown — keeps cash ≥ 0 except Dec 2027
        # Inject 1.713M GBP (cumulative = 5.786M GBP total shift).
        # Only Dec 2027 remains negative (-179 348 GBP).
        ('2027-01-01', '3900 Cash',       '1713000,00',  'Veloton Ltd'),
        ('2027-01-01', '4110 Bank loans', '-1713000,00', 'Veloton Ltd'),
        # Fixtures Ltd — unchanged from 2026 (still 270K)
        ('2027-01-01', '3160 CAPEX - fixtures & fittings, opening', '270000,00',   'Veloton Ltd'),
        ('2027-01-01', '3161 CAPEX - fixtures & fittings, addition', '-270000,00',  'Veloton Ltd'),
        # IT Ltd — unchanged from 2026 (still 345K; Oct-2027 60K addition is during 2027)
        ('2027-01-01', '3180 CAPEX - IT equipment, opening', '345000,00',  'Veloton Ltd'),
        ('2027-01-01', '3181 CAPEX - IT equipment, addition', '-345000,00', 'Veloton Ltd'),
        # Vehicles Ltd — unchanged (still 290K)
        ('2027-01-01', '3140 CAPEX - vehicles, opening', '290000,00',  'Veloton Ltd'),
        ('2027-01-01', '3141 CAPEX - vehicles, addition', '-290000,00', 'Veloton Ltd'),
    ],
}

# ---------------------------------------------------------------------------
# 2b. MODIFY EXISTING ROWS — keyed by (date, account, entity): new_amount
# ---------------------------------------------------------------------------
MODIFY = {
    # IT ApS roll-forward: each year's opening must include original 2 400K
    #   Jan 2024: end-2023 = 2400 + 600 = 3000K
    ('2024-01-01', '3180 CAPEX - IT equipment, opening',   'Veloton ApS'): '3000000,00',
    ('2024-01-01', '3181 CAPEX - IT equipment, addition',  'Veloton ApS'): '-3000000,00',
    #   Jan 2025: end-2024 = 3000K (no new additions)
    ('2025-01-01', '3180 CAPEX - IT equipment, opening',   'Veloton ApS'): '3000000,00',
    ('2025-01-01', '3181 CAPEX - IT equipment, addition',  'Veloton ApS'): '-3000000,00',
    #   Jan 2026: end-2025 = 3000 + 660 (Sep-2025) = 3660K
    ('2026-01-01', '3180 CAPEX - IT equipment, opening',   'Veloton ApS'): '3660000,00',
    ('2026-01-01', '3181 CAPEX - IT equipment, addition',  'Veloton ApS'): '-3660000,00',
    #   Jan 2027: end-2026 = 3660 − 600 (Sep-2026 detraction) = 3060K
    ('2027-01-01', '3180 CAPEX - IT equipment, opening',   'Veloton ApS'): '3060000,00',
    ('2027-01-01', '3181 CAPEX - IT equipment, addition',  'Veloton ApS'): '-3060000,00',

    # Fixtures ApS roll-forward: each year's opening must include original 1 200K
    #   Jan 2025: end-2024 = 1200 (original) + 1200 (Feb-2024) = 2400K
    ('2025-01-01', '3160 CAPEX - fixtures & fittings, opening',  'Veloton ApS'): '2400000,00',
    ('2025-01-01', '3161 CAPEX - fixtures & fittings, addition', 'Veloton ApS'): '-2400000,00',
    #   Jan 2026: end-2025 = 2400K (no changes)
    ('2026-01-01', '3160 CAPEX - fixtures & fittings, opening',  'Veloton ApS'): '2400000,00',
    ('2026-01-01', '3161 CAPEX - fixtures & fittings, addition', 'Veloton ApS'): '-2400000,00',
    #   Jan 2027: end-2026 = 2400K (Jun-2027 detraction is during 2027, not before)
    ('2027-01-01', '3160 CAPEX - fixtures & fittings, opening',  'Veloton ApS'): '2400000,00',
    ('2027-01-01', '3161 CAPEX - fixtures & fittings, addition', 'Veloton ApS'): '-2400000,00',
}

HOLDING_CASH_OLD = {}   # no cash changes needed
HOLDING_CASH_NEW = {}

# ---------------------------------------------------------------------------
# 3. IC RECEIVABLES FIX
#    Year-specific DKK/GBP rates from IC Revenue / IC COGS ratio analysis.
#    For each 4320 IC payables entry in Veloton Ltd (GBP), insert a mirrored
#    3320 IC receivables entry in Veloton ApS (DKK) with the sign flipped.
# ---------------------------------------------------------------------------
FX_RATE_BY_YEAR = {
    '2023': 8.656,
    '2024': 8.707,
    '2025': 8.559,
    '2026': 8.458,
    '2027': 8.493,
}

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def make_row(date, account, amount, entity):
    return f'{date};{account};{amount};Test transaction;{entity};Finance;\n'

def gbp_to_dkk(gbp_str, year):
    rate = FX_RATE_BY_YEAR.get(year, 8.5)
    gbp = float(gbp_str.replace(',', '.'))
    dkk = -gbp * rate          # flip sign: payable in Ltd → receivable in ApS
    return f'{dkk:.2f}'.replace('.', ',')

with open(INPUT, 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()

out = []
dates_inserted = set()

for i, line in enumerate(lines):
    parts = line.rstrip('\n').split(';')

    if len(parts) >= 5:
        date, account, amount, entity = parts[0], parts[1], parts[2], parts[4]

        # Fix 1: IC interest — update Holding income
        if account == '1920 IC interest income' and entity == 'Veloton Holding ApS':
            year = date[:4]
            if year in HOLDING_INCOME_BY_YEAR:
                parts[2] = HOLDING_INCOME_BY_YEAR[year]
                line = ';'.join(parts) + '\n'

        # Fix 1b: also update Holding's cash receipt that pairs with the income
        if account == '3900 Cash' and entity == 'Veloton Holding ApS':
            year = date[:4]
            if year in HOLDING_CASH_OLD and amount == HOLDING_CASH_OLD[year]:
                parts[2] = HOLDING_CASH_NEW[year]
                line = ';'.join(parts) + '\n'

        # Fix 2: CAPEX — modify existing roll-forward values
        key = (date, account, entity)
        if key in MODIFY:
            parts[2] = MODIFY[key]
            line = ';'.join(parts) + '\n'

    out.append(line)

    if len(parts) >= 5:
        # Fix 2: CAPEX — insert new rows after last line for each target date
        if date in NEW_ROWS and date not in dates_inserted:
            next_date = lines[i + 1].split(';')[0] if i + 1 < len(lines) else ''
            if next_date != date:
                for new_row in NEW_ROWS[date]:
                    out.append(make_row(*new_row))
                dates_inserted.add(date)

        # Fix 3: IC receivables — mirror every Ltd 4320 entry into ApS 3320,
        #         then reclassify the same amount out of 3340 Trade receivables.
        #         Net effect on ApS assets = zero (reclassification only).
        if account == '4320 IC payables' and entity == 'Veloton Ltd':
            year = date[:4]
            dkk_amount = gbp_to_dkk(amount, year)
            out.append(make_row(date, '3320 IC receivables',  dkk_amount, 'Veloton ApS'))
            # Offset: remove the same amount from trade receivables
            dkk_float = float(dkk_amount.replace(',', '.'))
            offset = f'{-dkk_float:.2f}'.replace('.', ',')
            out.append(make_row(date, '3340 Trade receivables', offset, 'Veloton ApS'))

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.writelines(out)

print(f'Input:  {len(lines):,} lines')
print(f'Output: {len(out):,} lines  (+{len(out)-len(lines)} new rows)')
print(f'Done -> {OUTPUT}')
