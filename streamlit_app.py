import io
import math
import zipfile
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Merch Splitter",
    page_icon="📦",
    layout="centered",
)

MAX_ROWS_PER_FILE = 100
MAX_INPUT_ROWS = 10_000
REQUIRED_COLUMNS = ["product", "quantity"]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize incoming column names to simplify validation."""
    normalized = df.copy()
    normalized.columns = [str(column).strip().lower() for column in normalized.columns]
    return normalized


def validate_base_input(df: pd.DataFrame) -> tuple[bool, str]:
    """Validate required columns and row constraints."""
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        return False, f"Brakuje wymaganych kolumn: {', '.join(missing_columns)}"

    if len(df) == 0:
        return False, "Plik nie zawiera żadnych wierszy do podziału."

    if len(df) > MAX_INPUT_ROWS:
        return False, f"Plik ma więcej niż {MAX_INPUT_ROWS:,} wierszy. Podziel dane i spróbuj ponownie.".replace(",", " ")

    return True, ""


def validate_quantity_column(df: pd.DataFrame) -> tuple[bool, str]:
    """Validate quantity column for split-by-quantity mode."""
    quantity = pd.to_numeric(df["quantity"], errors="coerce")

    if quantity.isna().any():
        return False, "Kolumna `quantity` musi zawierać wyłącznie liczby."

    if (quantity < 0).any():
        return False, "Kolumna `quantity` nie może zawierać wartości ujemnych."

    return True, ""


def build_output_name(prefix: str, index: int) -> str:
    return f"{prefix}.{index:02d}.xlsx"


def parse_name_pattern(filename: str) -> tuple[str, int]:
    stem = Path(filename).stem.strip()
    if not stem:
        return "merch", 1

    if "." in stem:
        maybe_prefix, maybe_number = stem.rsplit(".", 1)
        if maybe_number.isdigit() and len(maybe_number) == 2 and maybe_prefix.strip():
            return maybe_prefix.strip(), int(maybe_number)

    return stem, 1


def build_chunks_by_row_count(df: pd.DataFrame, rows_per_file: int = MAX_ROWS_PER_FILE) -> list[pd.DataFrame]:
    """Split dataframe into equal row chunks."""
    chunk_count = math.ceil(len(df) / rows_per_file)
    return [df.iloc[index * rows_per_file:(index + 1) * rows_per_file] for index in range(chunk_count)]


def build_chunks_by_quantity_sum(df: pd.DataFrame, max_quantity_sum: float) -> list[pd.DataFrame]:
    """Split dataframe so that each file has quantity sum <= max_quantity_sum."""
    chunks: list[pd.DataFrame] = []
    current_rows: list[dict] = []
    current_sum = 0.0

    numeric_quantity = pd.to_numeric(df["quantity"], errors="coerce")

    for idx, (_, row) in enumerate(df.iterrows()):
        qty = float(numeric_quantity.iloc[idx])

        if qty > max_quantity_sum:
            if current_rows:
                chunks.append(pd.DataFrame(current_rows))
                current_rows = []
                current_sum = 0.0
            chunks.append(pd.DataFrame([row.to_dict()]))
            continue

        if current_rows and current_sum + qty > max_quantity_sum:
            chunks.append(pd.DataFrame(current_rows))
            current_rows = []
            current_sum = 0.0

        current_rows.append(row.to_dict())
        current_sum += qty

    if current_rows:
        chunks.append(pd.DataFrame(current_rows))

    return chunks


def chunks_to_zip_bytes(chunks: list[pd.DataFrame], prefix: str, start_index: int = 1) -> bytes:
    """Write chunks as XLSX files into ZIP and return bytes."""
    output = io.BytesIO()

    with zipfile.ZipFile(output, mode="w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        for index, chunk in enumerate(chunks, start=start_index):
            chunk_stream = io.BytesIO()
            chunk.to_excel(chunk_stream, index=False)
            chunk_stream.seek(0)

            file_name = build_output_name(prefix, index)
            zip_file.writestr(file_name, chunk_stream.read())

    output.seek(0)
    return output.getvalue()


st.title("📦 Merch Splitter")
st.markdown(
    "Wgraj plik XLSX z kolumnami **product** i **quantity**. "
    "Możesz dzielić plik na:")
st.markdown("- paczki po maks. 100 wierszy, **albo**")
st.markdown("- paczki po maks. sumie `quantity` w każdym pliku.")

split_mode = st.radio(
    "Tryb podziału",
    options=["Maks. 100 wierszy na plik", "Maks. suma quantity na plik"],
    index=0,
)

quantity_limit = None
if split_mode == "Maks. suma quantity na plik":
    quantity_limit = st.number_input(
        "Maksymalna suma quantity w jednym pliku",
        min_value=1.0,
        value=100.0,
        step=1.0,
    )

uploaded_file = st.file_uploader("Wybierz plik wejściowy (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        raw_df = pd.read_excel(uploaded_file)
    except Exception as error:  # noqa: BLE001
        st.error(f"Nie udało się odczytać pliku XLSX: {error}")
    else:
        data = normalize_columns(raw_df)
        valid, message = validate_base_input(data)

        if not valid:
            st.error(message)
        else:
            if split_mode == "Maks. suma quantity na plik":
                qty_valid, qty_message = validate_quantity_column(data)
                if not qty_valid:
                    st.error(qty_message)
                    st.stop()

            source_prefix, start_number = parse_name_pattern(uploaded_file.name)

            if split_mode == "Maks. 100 wierszy na plik":
                chunks = build_chunks_by_row_count(data, rows_per_file=MAX_ROWS_PER_FILE)
                rule_description = f"po maks. {MAX_ROWS_PER_FILE} wierszy"
            else:
                chunks = build_chunks_by_quantity_sum(data, max_quantity_sum=float(quantity_limit))
                rule_description = f"po maks. sumie quantity = {quantity_limit:g}"

            st.success("Plik wygląda poprawnie ✅")
            st.caption(
                f"Wierszy: **{len(data)}** • Plików wyjściowych: **{len(chunks)}** "
                f"({rule_description})"
            )

            st.dataframe(data.head(10), use_container_width=True)

            try:
                zip_bytes = chunks_to_zip_bytes(chunks, source_prefix, start_index=start_number)
            except Exception as error:  # noqa: BLE001
                st.error(
                    "Nie udało się zapisać plików XLSX. Upewnij się, że zależność `openpyxl` jest "
                    f"dostępna. Szczegóły: {error}"
                )
            else:
                st.download_button(
                    label="⬇️ Pobierz ZIP z podzielonymi plikami",
                    data=zip_bytes,
                    file_name=f"{source_prefix}.zip",
                    mime="application/zip",
                    type="primary",
                )
else:
    st.info("Przykład: `dubai 100.01.xlsx` → ZIP z `dubai 100.01.xlsx`, `dubai 100.02.xlsx`, itd.")
