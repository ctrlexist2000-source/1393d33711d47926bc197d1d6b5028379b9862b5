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
REQUIRED_COLUMNS = ["product", "quantity"]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize incoming column names to simplify validation."""
    normalized = df.copy()
    normalized.columns = [str(column).strip().lower() for column in normalized.columns]
    return normalized


def validate_input(df: pd.DataFrame) -> tuple[bool, str]:
    """Validate required columns and row constraints."""
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        return False, f"Brakuje wymaganych kolumn: {', '.join(missing_columns)}"

    if len(df) == 0:
        return False, "Plik nie zawiera żadnych wierszy do podziału."

    if len(df) > 10_000:
        return False, "Plik ma więcej niż 10 000 wierszy. Podziel dane i spróbuj ponownie."

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


def split_into_zip(
    df: pd.DataFrame,
    prefix: str,
    start_index: int = 1,
    rows_per_file: int = MAX_ROWS_PER_FILE,
) -> bytes:
    """Split DataFrame into chunks and return ZIP bytes with XLSX files."""
    output = io.BytesIO()

    chunk_count = math.ceil(len(df) / rows_per_file)

    with zipfile.ZipFile(output, mode="w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        for index in range(chunk_count):
            chunk_start = index * rows_per_file
            chunk_end = chunk_start + rows_per_file
            chunk = df.iloc[chunk_start:chunk_end]

            chunk_stream = io.BytesIO()
            chunk.to_excel(chunk_stream, index=False)
            chunk_stream.seek(0)

            file_name = build_output_name(prefix, start_index + index)
            zip_file.writestr(file_name, chunk_stream.read())

    output.seek(0)
    return output.getvalue()


st.title("📦 Merch Splitter")
st.write(
    "Wgraj plik XLSX z kolumnami `product` i `quantity`, a aplikacja podzieli go "
    "na pliki po maks. 100 wierszy i przygotuje ZIP do pobrania."
)

uploaded_file = st.file_uploader("Wybierz plik wejściowy (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        raw_df = pd.read_excel(uploaded_file)
    except Exception as error:  # noqa: BLE001
        st.error(f"Nie udało się odczytać pliku XLSX: {error}")
    else:
        data = normalize_columns(raw_df)
        valid, message = validate_input(data)

        if not valid:
            st.error(message)
        else:
            total_rows = len(data)
            total_files = math.ceil(total_rows / MAX_ROWS_PER_FILE)
            source_prefix, start_number = parse_name_pattern(uploaded_file.name)

            st.success("Plik wygląda poprawnie ✅")
            st.caption(
                f"Wierszy: **{total_rows}** • Plików wyjściowych: **{total_files}** "
                f"(po maks. {MAX_ROWS_PER_FILE} wierszy)"
            )

            preview = data.head(10)
            st.dataframe(preview, use_container_width=True)

            zip_bytes = split_into_zip(
                data,
                source_prefix,
                start_index=start_number,
                rows_per_file=MAX_ROWS_PER_FILE,
            )

            st.download_button(
                label="⬇️ Pobierz ZIP z podzielonymi plikami",
                data=zip_bytes,
                file_name=f"{source_prefix}.zip",
                mime="application/zip",
                type="primary",
            )
else:
    st.info("Przykład nazwy pliku: `dubai 100.01.xlsx` → ZIP z `dubai 100.01.xlsx`, `dubai 100.02.xlsx`, itd.")
