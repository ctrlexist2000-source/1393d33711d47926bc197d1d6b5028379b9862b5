# 📦 Merch Splitter

Prosta aplikacja w Streamlit do dzielenia dużego pliku XLSX na mniejsze pliki i pobierania ich jako ZIP.

## Co robi aplikacja

Aplikacja przyjmuje plik `.xlsx` z kolumnami `product`, `quantity` (do 10 000 wierszy), a następnie umożliwia 2 tryby podziału:

1. **Maks. 100 wierszy na plik** (klasyczny split na równe paczki).
2. **Maks. suma quantity na plik** (split wg limitu ilości, np. 100 sztuk na plik).

Dla nazwy wejściowej `dubai 100.01.xlsx` numeracja jest kontynuowana:
- `dubai 100.01.xlsx`
- `dubai 100.02.xlsx`
- `dubai 100.03.xlsx`
- ...

## Jak uruchomić lokalnie

1. Zainstaluj zależności:

```bash
pip install -r requirements.txt
```

2. Uruchom aplikację:

```bash
streamlit run streamlit_app.py
```

## Jak udostępnić zespołowi (najszybciej)

Najprościej wrzucić repo na GitHub i podłączyć do **Streamlit Community Cloud**:

1. Push repo na GitHub.
2. Wejdź na https://share.streamlit.io
3. Wybierz repo i plik startowy `streamlit_app.py`.
4. Deploy.
5. Udostępnij link członkom zespołu.

Alternatywnie możesz wdrożyć aplikację wewnętrznie (np. Docker + reverse proxy).
