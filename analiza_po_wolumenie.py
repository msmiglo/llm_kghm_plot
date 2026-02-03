
from datetime import datetime
import json
import os
import requests

import matplotlib.pyplot as plt
import numpy as np


URL = "https://api.bankier.pl/quotes/public/company-profile-chart/PLKGHM000017/?intraday=true&range=1w"
FILENAME = "data.json"
FORCE_UPDATE = False


# get data
mod_time = os.path.getmtime(FILENAME)
mod_time = datetime.fromtimestamp(mod_time)
today_17_30 = datetime.now().replace(
    hour=17, minute=30, second=0, microsecond=0)

if mod_time > today_17_30 and not FORCE_UPDATE:
    print("data is up to date (was updated today after 17:30)")
else:
    print("updating data from net")
    with open(FILENAME, 'r') as f:
        local_data = json.load(f)

    response = requests.get(URL)
    response.raise_for_status()
    remote_data = response.json()

    # merge data
    for key in ['main', 'volume']:
        last_timestamp = local_data[key][-1][0]
        remote_timestamps = [elem[0] for elem in remote_data[key]]
        index = remote_timestamps.index(last_timestamp)
        local_data[key] += remote_data[key][index+1:]

    with open(FILENAME, 'w') as f:  # , encoding='utf-8'
        json.dump(local_data, f, indent=None)

# draw data
with open(FILENAME, 'r') as f:
    data = json.load(f)

t_x = [item[0] for item in data['main']]
x = [item[4] for item in data['main']]

t_w = [item[0] for item in data['volume']]
w = [item[1] for item in data['volume']]
cw = np.cumsum(w).tolist()

print(len(w), len(cw))

# Sprawdzenie czy etykiety czasowe są identyczne
identyczne = t_x == t_w
print(f"Czy etykiety czasowe są identyczne? {identyczne}")

fig, ax1 = plt.subplots()

# Seria x (Cena) - oś lewa
ax1.plot(t_x, x, color='blue')
ax1.set_ylabel('Cena (x)', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

# Seria w (Wolumen) - oś prawa
ax2 = ax1.twinx()
ax2.plot(t_x, w, color='green')
ax2.set_ylabel('Wolumen (w)', color='green')
ax2.tick_params(axis='y', labelcolor='green')

plt.tight_layout()
plt.show()

# Rysowanie głównej serii danych po wolumenie
days_t_i = [i for i in range(len(t_x) - 1) if t_x[i+1] - t_x[i] > 1000000]
main_t_i = days_t_i + [-1]
minor_t_i = [i+60*(j+1) for i in [0] + main_t_i for j in range(7)]

print(days_t_i)
print(main_t_i)
print(minor_t_i)
cw_big = [0] + [cw[i] for i in main_t_i]
x_big = [x[0]] + [x[i] for i in main_t_i]

cw_small = [cw[i] for i in minor_t_i if i < len(cw)]
x_small = [x[i] for i in minor_t_i if i < len(x)]

h1 = 60
h8 = 480
fig, ax1 = plt.subplots()

# Główna seria x-y (Oś X: cw, Oś Y: x)
ax1.plot(cw, x, color='blue', linewidth=1)

# Małe kropki (co 1h, średnica ~2px -> s=3)
ax1.scatter(cw_small, x_small, color='red', s=3, zorder=3)

# Duże kropki (co 8h, średnica ~5px -> s=25)
ax1.scatter(cw_big, x_big, color='red', s=25, zorder=4)

# Cieniutkie czerwone kreski od dużych kropek do dołu (oś X)
ax1.vlines(cw_big, ymin=min(x), ymax=x_big, color='red', linewidth=0.3, alpha=0.7)

# Formatowanie osi zgodnie z Twoimi wymaganiami
ax1.set_xlabel('Skumulowany Wolumen (cw)', color='green')
ax1.set_ylabel('Cena (x)', color='blue')

# Kolorowanie "ticków" (kresek i liczb na osiach)
ax1.tick_params(axis='x', colors='green')
ax1.tick_params(axis='y', colors='blue')

plt.tight_layout()
plt.show()
