import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# КАЛІБРОВАНІ МАТРИЦІ (отримані з preprocessing.py)
# ==========================================
P_BASE = {'p00': 0.866, 'p01': 0.134, 'p10': 0.067, 'p11': 0.933}
P_DIP = {'p00': 0.931, 'p01': 0.069, 'p10': 0.067, 'p11': 0.933}
P_ENF = {'p00': 0.967, 'p01': 0.033, 'p10': 0.067, 'p11': 0.933}


# ==========================================
# ЯДРО СИМУЛЯЦІЇ (ГІБРИДНА МОДЕЛЬ)
# ==========================================
def simulate_conflict(months, strategy='base', arima_weight=0.01):
    """
    Симулює одну траєкторію конфлікту на задану кількість місяців.
    Використовує базові марковські ймовірності + Індекс стійкості (ARIMA) + шоки.
    """
    if strategy == 'base':
        P = P_BASE
    elif strategy == 'dip':
        P = P_DIP
    elif strategy == 'enf':
        P = P_ENF

    current_state = 1  # Починаємо зі стану конфлікту
    resilience = 0
    history = []

    for t in range(months):
        history.append(current_state)

        # Шок "announced" - випадково виникає з ймовірністю 5%
        shock = 0.05 if np.random.rand() < 0.05 else 0

        if current_state == 0:  # Стан МИРУ
            resilience += 1
            # Динамічна корекція: База + Пам'ять + Шок
            adjusted_p00 = min(0.999, P['p00'] + (resilience * arima_weight) + shock)
            current_state = 0 if np.random.rand() < adjusted_p00 else 1
        else:  # Стан КОНФЛІКТУ
            resilience = 0
            # Динамічна корекція: База + Шок
            adjusted_p10 = min(0.95, P['p10'] + shock)
            current_state = 0 if np.random.rand() < adjusted_p10 else 1

    return history


# ==========================================
# ЦИКЛ МОНТЕ-КАРЛО ТА ВІЗУАЛІЗАЦІЯ
# ==========================================
def run_monte_carlo_experiments(n_iterations=1000, months=60):
    print(f"Запуск симуляції: {n_iterations} ітерацій на {months} місяців.")

    base_peace_durations, dip_peace_durations, enf_peace_durations = [], [], []

    # Прогони симулятора для кожного сценарію
    for i in range(n_iterations):
        base_sim = simulate_conflict(months, strategy='base')
        base_peace_durations.append(base_sim.count(0))

        dip_sim = simulate_conflict(months, strategy='dip')
        dip_peace_durations.append(dip_sim.count(0))

        enf_sim = simulate_conflict(months, strategy='enf')
        enf_peace_durations.append(enf_sim.count(0))

    # Статистичні оцінки
    mean_base = np.mean(base_peace_durations)
    mean_dip = np.mean(dip_peace_durations)
    mean_enf = np.mean(enf_peace_durations)

    print("\n--- РЕЗУЛЬТАТИ СИМУЛЯЦІЇ ---")
    print(f"Середній час миру (Базовий): {mean_base:.1f} міс.")
    print(f"Середній час миру (Дипломатія): {mean_dip:.1f} міс. (+{((mean_dip - mean_base) / mean_base) * 100:.1f}%)")
    print(f"Середній час миру (Примус): {mean_enf:.1f} міс. (+{((mean_enf - mean_base) / mean_base) * 100:.1f}%)")

    # Побудова графіка
    plt.figure(figsize=(10, 6))

    plt.hist(base_peace_durations, bins=20, alpha=0.6, color='red', label='Базовий сценарій (без втручань)')
    plt.hist(dip_peace_durations, bins=20, alpha=0.6, color='green', label='Дипломатія / Медіатор')
    plt.hist(enf_peace_durations, bins=20, alpha=0.6, color='blue', label='Військовий примус')

    # Лінії середніх значень
    plt.axvline(mean_base, color='darkred', linestyle='dashed', linewidth=2)
    plt.axvline(mean_dip, color='darkgreen', linestyle='dashed', linewidth=2)
    plt.axvline(mean_enf, color='darkblue', linestyle='dashed', linewidth=2)

    # Оформлення
    plt.title('Розподіл тривалості миру (Результати 1000 Монте-Карло симуляцій)', fontsize=14)
    plt.xlabel('Загальна кількість місяців миру за 5 років', fontsize=12)
    plt.ylabel('Кількість симуляцій (частота)', fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(axis='y', alpha=0.3)

    # Збереження
    plt.savefig('monte_carlo_results.png', dpi=300, bbox_inches='tight')
    print("\nГрафік успішно збережено")
    plt.show()


if __name__ == "__main__":
    # Запуск головного циклу при виконанні скрипта
    run_monte_carlo_experiments(n_iterations=1000, months=60)