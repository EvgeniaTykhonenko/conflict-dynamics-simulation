import pandas as pd

# ==========================================
# ЕТАП 1: ЗАВАНТАЖЕННЯ ТА ПЕРЕТВОРЕННЯ ДАТ
# ==========================================
df = pd.read_excel('CFD_oct_2022_id-1.xlsx')


def to_dt(row, yr_col, mo_col):
    """Конвертує окремі колонки року та місяця у формат Timestamp."""
    try:
        year = int(row[yr_col])
        month = int(row[mo_col])
        if year <= 0 or month <= 0:
            return pd.NaT
        return pd.Timestamp(year=year, month=month, day=1)
    except (ValueError, TypeError):
        return pd.NaT


# Створюємо дати початку, кінця та оголошення
df['start_date'] = df.apply(lambda r: to_dt(r, 'cf_effect_yr', 'cf_effect_month'), axis=1)
df['end_date'] = df.apply(lambda r: to_dt(r, 'end_yr', 'end_month'), axis=1)
df['dec_date'] = df.apply(lambda r: to_dt(r, 'cf_dec_yr', 'cf_dec_month'), axis=1)

# Видаляємо рядки без валідних дат
df = df.dropna(subset=['start_date', 'end_date'])

# ==========================================
# ЕТАП 2: РОЗГОРТАННЯ ЗА КОНФЛІКТАМИ (EXPANSION)
# ==========================================
final_results = []

for country_code, group in df.groupby('cc'):
    overall_start = group['start_date'].min()
    overall_end = group['end_date'].max()

    # Створюємо повну місячну сітку для конфлікту
    time_grid = pd.date_range(start=overall_start, end=overall_end, freq='MS')
    series = pd.DataFrame({'date': time_grid, 'cc': country_code})

    series['state'] = 1  # 1 = Конфлікт (за замовчуванням)
    series['announced'] = 0
    series['mediator_nego'] = 0.0
    series['enforcement'] = 0.0

    # "Фарбуємо" місяці миру та фіксуємо стратегії
    for _, row in group.iterrows():
        mask = (series['date'] >= row['start_date']) & (series['date'] <= row['end_date'])
        series.loc[mask, 'state'] = 0

        if pd.notnull(row['dec_date']):
            series.loc[series['date'] == row['dec_date'], 'announced'] = 1

        for col in ['mediator_nego', 'enforcement']:
            if col in row:
                series.loc[mask, col] = row[col]

    final_results.append(series)

processed_df = pd.concat(final_results).fillna(0)
processed_df = processed_df.sort_values(by=['cc', 'date'])

# ==========================================
# ЕТАП 3: ЗСУВ (SHIFT) ТА РОЗРАХУНОК МАТРИЦЬ МАРКОВА
# ==========================================
processed_df['state_prev'] = processed_df.groupby('cc')['state'].shift(1)
processed_df['mediator_prev'] = processed_df.groupby('cc')['mediator_nego'].shift(1)
processed_df['enf_prev'] = processed_df.groupby('cc')['enforcement'].shift(1)

# Видаляємо перший місяць кожної країни (немає t-1)
matrix_df = processed_df.dropna(subset=['state_prev', 'mediator_prev', 'enf_prev']).copy()


def get_markov_matrix(data, strategy_col, strategy_val, name="Matrix"):
    """Універсальна функція для розрахунку матриць P."""
    if strategy_val > 0:
        subset = data[data[strategy_col] >= strategy_val]
    else:
        subset = data[data[strategy_col] == 0.0]

    counts = subset.groupby(['state_prev', 'state']).size().unstack(fill_value=0)

    # Захист від відсутніх станів
    for i in [0.0, 1.0]:
        if i not in counts.columns: counts[i] = 0
        if i not in counts.index: counts.loc[i] = [0, 0]

    counts = counts.sort_index(axis=0).sort_index(axis=1)
    prob = counts.div(counts.sum(axis=1), axis=0).fillna(0)

    print(f"\n=== {name} ===")
    print("Ймовірності переходів:\n", prob.round(3))
    return prob


# Розраховуємо та виводимо матриці
P_0 = get_markov_matrix(matrix_df, strategy_col='mediator_prev', strategy_val=0.0, name="P_0 (БАЗОВА МАТРИЦЯ - u=0)")
P_dip = get_markov_matrix(matrix_df, strategy_col='mediator_prev', strategy_val=1.0, name="P_dip (ДИПЛОМАТІЯ - u=1)")
P_enf = get_markov_matrix(matrix_df, strategy_col='enf_prev', strategy_val=1.0, name="P_enf (ВІЙСЬКОВИЙ ПРИМУС - u=1)")


# ==========================================
# ЕТАП 4: ФОРМУВАННЯ ІНДЕКСУ СТІЙКОСТІ (ARIMA PREP)
# ==========================================
def calculate_resilience(series):
    """Накопичує кількість місяців безперервного миру."""
    resilience, current_res = [], 0
    for state in series:
        if state == 0.0:
            current_res += 1
        else:
            current_res = 0
        resilience.append(current_res)
    return resilience


processed_df['resilience_index'] = processed_df.groupby('cc')['state'].transform(calculate_resilience)

# Зберігаємо фінальний датасет (опціонально, як чекпоінт)
processed_df.to_csv('CFD_ready_for_Simulation.csv', index=False)
print("\nПрепроцесинг завершено. Дані збережено у CFD_ready_for_Simulation.csv")