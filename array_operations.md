# Bezpieczne operacje na rastrach NumPy

Operacje na rastrach wymagają rozróżnienia **braku danych**, **wyniku nieokreślonego** i **wartości spoza zakresu typu danych**. Dobór metody zależy od tego, czy problem dotyczy wejścia do obliczeń, samego działania, czy wykorzystania wyniku.

## Podstawowe mechanizmy

| Mechanizm | Zastosowanie |
|---|---|
| `np.ma` | Raster z maską; zachowanie informacji o pomijanych pikselach w kolejnych obliczeniach. |
| `np.isfinite()` | Wykrywanie wartości skończonych; nie rozpoznaje umownych kodów NoData. |
| `np.divide(..., out=..., where=...)` | Kontrola miejsc, w których wykonywane jest dzielenie zwykłych tablic. |
| `np.errstate()` | Kontrola ostrzeżeń o błędach arytmetyki zmiennoprzecinkowej; nie zmienia wyników. |
| `np.nanmean()` i podobne | Statystyki zwykłych tablic z `NaN`; nie pomijają automatycznie `inf` ani kodów NoData. |
| `np.nan_to_num()` | Zamiana `NaN` i `inf` na wskazane liczby, gdy wymaga tego dalsze przetwarzanie. |
| `astype()` | Zmiana typu danych, np. przed odejmowaniem rastrów `uint8`. |

```python
import numpy as np
import matplotlib.pyplot as plt
```

## 1. Brak danych i maski

### `NoData`, `NaN`, `inf`

| Wartość | Znaczenie |
|---|---|
| `NoData` (np. `-9999`) | Kod braku pomiaru określony w danych lub metadanych; dla NumPy to zwykła liczba. |
| `np.nan` | Wynik nieokreślony lub znacznik braku wartości w tablicy zmiennoprzecinkowej. |
| `np.inf`, `-np.inf` | Nieskończoności, np. po dzieleniu niezerowej wartości przez zero. |

```python
a = np.array([1., -9999., np.nan, np.inf, 5.])

np.isnan(a)      # tylko NaN
np.isinf(a)      # inf i -inf
np.isfinite(a)   # liczby skończone, w tym -9999
```

**Ważne:** `NoData` należy odczytać z metadanych rastra. Własny kod `-9999` jest tu tylko przykładem.

### `np.ma` – tablica danych i maska

`np.ma.MaskedArray` przechowuje wartości oraz maskę logiczną o tym samym układzie przestrzennym. W masce `True` oznacza piksel **pomijany w analizie**; nie oznacza usunięcia go z tablicy.

```python
ar = np.array([[10., -9999.],
               [20., 30.]])

m = np.ma.masked_equal(ar, -9999)

m                       # [[10.0, --], [20.0, 30.0]]
m.mean()                # 20.0
np.ma.getmaskarray(m)   # [[False, True], [False, False]]
```

Inne sposoby tworzenia i rozszerzania maski:

```python
m = np.ma.masked_invalid(m)           # dodatkowo maskuje NaN i inf
cloud = np.array([[False, False],
                  [True, False]])
m = np.ma.masked_where(cloud, m)      # dodaje maskę chmur
valid = ~np.ma.getmaskarray(m)        # True = piksel dopuszczony do analizy
```

Nowa maska obejmuje piksele wykluczone wcześniej **lub** wskazane przez `cloud`. Można w ten sposób łączyć NoData, chmury, cienie i błędy obliczeń.

### Działania na tablicach maskowanych

`MaskedArray` obsługuje typowe działania NumPy bez rozdzielania danych i masek: `+`, `-`, `*`, `/`, porównania oraz wiele funkcji (`np.sqrt`, `np.log` itp.). W działaniach na dwóch rastrach wynik jest maskowany tam, gdzie zamaskowany jest **którykolwiek operand**. Funkcje uwzględniają również niedozwolone wartości argumentów, np. zerowy mianownik.

```python
ma1 = np.ma.array([[10., 20.],
                   [30., 40.]],
                  mask=[[False, True],
                        [False, False]])

ma2 = np.ma.array([[2., 5.],
                   [0., 4.]],
                  mask=[[False, False],
                        [False, True]])

result = ma1 / ma2
# [[5.0, --],
#  [ --, --]]

result.mean()                # 5.0
np.ma.getmaskarray(result)   # maska wyniku
ma1 + 2                     # działanie ze skalarem; maska pozostaje
ma1[0, :]                   # wycinek także zachowuje maskę
```

**Nie trzeba** robić `ma1.data / ma2.data` ani ręcznie scalać masek. Spowodowałoby to utratę ochrony zapewnianej przez `np.ma`. Działa również mieszana arytmetyka `MaskedArray` z odpowiednio ułożoną zwykłą `ndarray`.

Dla rastrów operacje piksel po pikselu mają sens tylko przy zgodnej siatce (rozmiar, rozdzielczość, położenie pikseli i układ współrzędnych). NumPy nie sprawdza georeferencji.

## 2. Arytmetyka rastrów

### Typ danych i przepełnienie

Arytmetyka na typach całkowitoliczbowych może przekroczyć ich zakres. Przykład dla `uint8` (`0–255`):

```python
a = np.array([250], dtype=np.uint8)
b = np.array([10], dtype=np.uint8)

a + b                          # [4] — przepełnienie

a.astype(np.float32) + b       # [260.]
b.astype(np.float32) - a       # [-240.]
```

Przy odejmowaniu kanałów i obliczaniu indeksów zwykle przechodzimy na typ zmiennoprzecinkowy **przed** działaniem.

### Dzielenie zwykłych tablic: `np.divide()`

`np.divide()` z `where=` nie wykonuje działania tam, gdzie warunek jest fałszywy. `out=` wskazuje tablicę wynikową; dla pominiętych pikseli pozostaje jej wartość początkowa.

```python
a = np.array([1., 0., 5., 8.])
b = np.array([2., 0., 0., 4.])

out = np.full(a.shape, np.nan)
valid = np.isfinite(a) & np.isfinite(b) & (b != 0)
np.divide(a, b, out=out, where=valid)

# [0.5, nan, nan, 2.0]
```

Dla mianownika bliskiego zeru wynik może być niestabilny; jeśli uzasadniają to właściwości danych, stosuje się próg, np. `np.abs(b) > 1e-6` zamiast `b != 0`.

**Wybór:** dla dwóch `MaskedArray` zwykle wystarczy `ma1 / ma2`; `np.divide(..., where=...)` jest przydatne przy zwykłych `ndarray`, gdy chcemy jawnie sterować zakresem obliczeń.

### Pierwiastek, logarytm, zakres wartości

Pierwiastek rzeczywisty wymaga argumentu nieujemnego, logarytm — dodatniego. `np.ma` może maskować wyniki poza dziedziną funkcji:

```python
x = np.ma.array([-4., 0., 1., 9.])

np.ma.sqrt(x)       # [--, 0.0, 1.0, 3.0]
np.ma.log(x)        # [--, --, 0.0, 2.197...]
```

`np.clip(a, min, max)` to inna operacja: **ogranicza wartości**, nie oznacza ich jako brak danych. Użyteczna m.in. do przygotowania RGB do wyświetlania.

### Ostrzeżenia NumPy: `np.errstate()`

NumPy zgłasza ostrzeżenia (`RuntimeWarning`) m.in. dla `1/0` (`divide`) i `0/0` (`invalid`). `np.errstate()` ustawia sposób ich obsługi **tylko wewnątrz bloku `with`**.

```python
a = np.array([1., 0.])
b = np.array([0., 0.])

with np.errstate(divide='ignore', invalid='ignore'):
    result = a / b

# [inf, nan] — wyniki pozostają bez zmian
```

`ignore` oznacza **niezgłaszanie wskazanych ostrzeżeń**, a nie naprawę operacji. Ma sens tylko wtedy, gdy takie przypadki są oczekiwane i wynik zostanie następnie sprawdzony lub zamaskowany. Przy diagnozowaniu błędów ostrzeżeń nie należy ukrywać. Nie jest to mechanizm obsługi wszystkich ostrzeżeń Pythona.

## 3. Kiedy używać `.mask`, `.data`, `.compressed()` i `.filled()`?

Na `MaskedArray` wykonujemy zwykłe obliczenia **dopóki kolejny etap obsługuje maskę**. Konwersja jest potrzebna np. przy tworzeniu histogramu, przekazywaniu danych do funkcji wymagającej zwykłej `ndarray` lub zapisie rastra z kodem NoData.

| Element | Wynik | Zastosowanie / ograniczenie |
|---|---|---|
| `m.mean()`, `m.min()`, `m.sum()` | Statystyka bez zamaskowanych pikseli | Bezpośrednio na `MaskedArray`. |
| `np.ma.getmaskarray(m)` | Maska `bool` o wymiarach rastra | Do łączenia masek, kontroli jakości, indeksowania. |
| `m.mask` | Maska lub pojedyncze `False` | Nie zawsze jest tablicą; bezpieczniej użyć `getmaskarray()`. |
| `m.compressed()` | Zwykła `ndarray` **1D** | Histogram, lista poprawnych pomiarów; **traci układ 2D**. |
| `m.filled(wartość)` | Zwykła `ndarray` o pierwotnym kształcie | Eksport lub funkcje bez obsługi masek; maskowane piksele zastępuje wskazaną wartością. |
| `m.data` | Same dane, bez uwzględnienia maski | Dostęp techniczny; wartości w zamaskowanych pikselach mogą być nieprzydatne. |

```python
m = np.ma.array([[1., 2.],
                 [3., 4.]],
                mask=[[False, True],
                      [False, False]])

m.mean()                         # 2.666...
m.compressed()                   # [1., 3., 4.]       — 1D
m.filled(np.nan)                 # [[1., nan], [3., 4.]] — 2D
m.data                           # [[1., 2.], [3., 4.]] — tylko dane
```

Przy danych całkowitoliczbowych przed wypełnieniem `NaN` należy zmienić typ: `m.astype(float).filled(np.nan)`. `np.asarray(m)` również nie zachowuje maski. Przy funkcjach, które wymagają zwykłej `ndarray` lub nie obsługują `MaskedArray`, trzeba świadomie wybrać `compressed()` albo `filled()`; `compressed()` nie nadaje się do zapisu rastra 2D.

### Statystyki i wyświetlanie

Dla zwykłej `ndarray` zawierającej `NaN` można użyć `np.nanmean()`, `np.nanmin()` itp. Funkcje te **nie eliminują** `inf` ani umownego NoData.

```python
a = np.array([1., 2., np.nan, 5.])
np.nanmean(a)                    # 2.666...
```

`imshow()` obsługuje maskowane piksele. Do `hist()` przekazujemy wartości z `compressed()`:

```python
fig, axs = plt.subplots(1, 2, figsize=(8, 3))
im = axs[0].imshow(m, cmap='gray')
fig.colorbar(im, ax=axs[0])
axs[1].hist(m.compressed(), bins=10)
plt.show()
```

Jeżeli odbiorca wymaga zwykłej tablicy bez `NaN` i `inf`, dostępne jest `np.nan_to_num()`. Zastąpienie braków np. zerami zmienia znaczenie pomiarów i nie powinno być domyślnym etapem przetwarzania:

```python
a = np.array([1., np.nan, np.inf])
np.nan_to_num(a, nan=0., posinf=0.)    # [1., 0., 0.]
```

## 4. Przykład: NDVI z maskowaniem

Przykład obejmuje umowny NoData (`-9999`) i zerowy mianownik. Maski obu kanałów są uwzględniane w działaniach automatycznie.

```python
nir = np.array([[0.6, 0.0],
                [0.4, -9999.]])
red = np.array([[0.2, 0.0],
                [0.1, 0.2]])

nir = np.ma.masked_invalid(np.ma.masked_equal(nir, -9999))
red = np.ma.masked_invalid(np.ma.masked_equal(red, -9999))

ndvi = (nir - red) / (nir + red)
# [[0.5, --],
#  [0.6, --]]

ndvi.mean()                 # 0.55
ndvi.compressed()           # [0.5, 0.6]
ndvi.filled(np.nan)         # ndarray 2D do dalszego użycia
```

Maska chmur lub jakości może być dodana do `nir` i `red` przed obliczeniem indeksu albo do `ndvi` po obliczeniu, zależnie od przyjętej procedury. Skalowanie danych satelitarnych do reflektancji i interpretacja znaczników jakości są odrębnymi etapami.
