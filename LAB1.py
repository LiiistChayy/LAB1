
import pulp

def solve_steel_problem(a1_a, a1_b, a2_a, a2_b, cost_b_mod=0):
    prob = pulp.LpProblem("Steel_Optimization", pulp.LpMinimize)
    warehouses = [1, 2]; points = [1, 2]
    x = pulp.LpVariable.dicts("x", (warehouses, points, ['a', 'b']), lowBound=0)
    s = pulp.LpVariable.dicts("subst", (warehouses, points), lowBound=0)
    costs = {1: {1: 1.5, 2: 1.7}, 2: {1: 1.4, 2: 1.7}}

    prob += pulp.lpSum([
        x[i][j]['a'] * costs[i][j] + x[i][j]['b'] * (costs[i][j] + cost_b_mod)
        for i in warehouses for j in points
    ])


    prob += pulp.lpSum([x[1][j]['a'] for j in points]) <= a1_a
    prob += pulp.lpSum([x[1][j]['b'] for j in points]) <= a1_b
    prob += pulp.lpSum([x[2][j]['a'] for j in points]) <= a2_a
    prob += pulp.lpSum([x[2][j]['b'] for j in points]) <= a2_b


    prob += pulp.lpSum([x[i][1]['a'] - s[i][1] for i in warehouses]) >= 1100
    prob += pulp.lpSum([x[i][1]['b'] + 0.7 * s[i][1] for i in warehouses]) >= 4800
    prob += pulp.lpSum([x[i][1]['a'] + x[i][1]['b'] for i in warehouses]) == 6600

    prob += pulp.lpSum([x[i][2]['a'] - s[i][2] for i in warehouses]) >= 4500
    prob += pulp.lpSum([x[i][2]['b'] + 0.7 * s[i][2] for i in warehouses]) >= 2200
    prob += pulp.lpSum([x[i][2]['a'] + x[i][2]['b'] for i in warehouses]) == 7200

    for i in warehouses:
        for j in points:
            prob += s[i][j] <= x[i][j]['a']

    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    ts = sum(pulp.value(s[i][j]) for i in warehouses for j in points)
    return prob, ts

a1a, a1b, a2a, a2b = 3600, 5800, 5000, 2400
res, ts = solve_steel_problem(a1a, a1b, a2a, a2b)

print("--- Базовое решение ---")
print(f"Общая стоимость: {pulp.value(res.objective)} ДЕ")
print(f"Объем замены марки 'а' на 'б': {ts} тонн")

print("--- Исследование 1.1 ---")
while ts < 100:
    a1b -= 50; a2b -= 50
    a1a += 50; a2a += 50
    res, ts = solve_steel_problem(a1a, a1b, a2a, a2b)
    if a1b < 0 or a2b < 0: break

print(f"Результат: замена в {round(ts, 2)} т появилась при запасах 'б': А1={a1b}, А2={a2b}")

print("--- Исследование 2.1 ---")
a1a, a1b, a2a, a2b = 10000, 10000, 10000, 10000
mod = 0
res, ts = solve_steel_problem(a1a, a1b, a2a, a2b, cost_b_mod=mod)

while ts < 100:
    mod += 0.1
    res, ts = solve_steel_problem(a1a, a1b, a2a, a2b, cost_b_mod=mod)

print(f"Результат: замена в {round(ts, 2)} т появилась при наценке на марку 'б' = {round(mod, 2)} ДЕ")
