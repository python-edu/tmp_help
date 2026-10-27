# Matplotlib – obraz zamiast wykresu


## Podstawowe ustawienia

| Ustawienie | Działanie |
|---|---|
| `ax.axis("off")` | Wyłącza osie, podziałki, etykiety i ramkę |
| `ax.set_xticks([])` | Ukrywa podziałkę X |
| `ax.set_yticks([])` | Ukrywa podziałkę Y |
| `ax.grid(False)` | Wyłącza siatkę |
| `ax.set_aspect("equal")` | Zachowuje proporcje pikseli |
| `interpolation="nearest"` | Wyłącza wygładzanie pikseli |
| `cmap="gray"` | Obraz w skali szarości |
| `vmin=0, vmax=255` | Stała skala jasności dla danych 8-bitowych |
| `layout="constrained"` | Automatyczne rozmieszczenie wykresów |
| `ax.set_box_aspect(1)` | Kwadratowy obszar osi |

### Minimalny kod do wyświetlania obrazu

```python
fig, ax = plt.subplots(figsize=(6, 6))

ax.imshow(
    img,
    cmap="gray",
    vmin=0,
    vmax=255,
    interpolation="nearest"
)

ax.axis("off")
plt.show()
```

### Bez marginesów – sam obraz

```python
fig, ax = plt.subplots(figsize=(6, 6))

ax.imshow(img, cmap="gray", interpolation="nearest")
ax.axis("off")

fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
plt.show()
```

### Rozmiar i proporcje

- `figsize=(width, height)` – rozmiar figury w calach, nie rozdzielczość obrazu.
- `dpi` – rozdzielczość figury przy renderowaniu lub zapisie.
- `aspect="equal"` – zachowuje proporcje obrazu.
- `aspect="auto"` – wypełnia dostępne pole, ale może zniekształcać obraz.
- `ax.set_box_aspect(1)` – wymusza kwadratowy obszar osi.

### Zapis obrazu bez dodatkowych marginesów

```python
plt.savefig("image.png", bbox_inches="tight", pad_inches=0)
```



# Automatyczne obliczanie siatki wykresów
A. Trzy kolumny – dowolna liczba obrazów
- Liczba kolumn: ncols = 3
- Liczba wierszy: nrows = ceil(n / ncols)
- Rozmiar całej figury: figsize=(szerokość, wysokość) w calach.
- Rozmiar figury rośnie proporcjonalnie do liczby kolumn i wierszy.

```python
from math import ceil

n = len(images)
ncols = 3
nrows = ceil(n / ncols)

fig, axs = plt.subplots(
    nrows, ncols,
    figsize=(4 * ncols, 4 * nrows),
    layout="constrained",
    squeeze=False
)

for ax, img in zip(axs.flat, images):
    ax.imshow(img, cmap="gray")
    ax.axis("off")

# Ukrycie niewykorzystanych pól
for ax in axs.flat[n:]:
    ax.axis("off")

plt.show()
```

---

# Dwie pary obraz + histogram w każdym wierszu
Układ czterech kolumn:
>- Obraz 1 : Histogram 1 | Obraz 2 : Histogram 2
>- Obraz 2 : Histogram 2 | Obraz 3 : Histogram 3



- ncols = 4
- nrows = ceil(n / 2) – dwa obrazy na wiersz.
- set_box_aspect(1) – jednakowy, kwadratowy obszar każdego wykresu.


```python
from math import ceil

n = len(images)
nrows = ceil(n / 2)

fig, axs = plt.subplots(
    nrows, 4,
    figsize=(16, 4 * nrows),
    layout="constrained",
    squeeze=False
)

for i, img in enumerate(images):
    row = i // 2
    col = (i % 2) * 2

    ax_img = axs[row, col]
    ax_hist = axs[row, col + 1]

    ax_img.imshow(img, cmap="gray")
    ax_img.axis("off")

    ax_hist.hist(img.ravel(), bins=256)
    ax_hist.set_box_aspect(1)

# Ukrycie niewykorzystanych pól
for ax in axs.flat:
    if not ax.has_data():
        ax.axis("off")

plt.show()
```
