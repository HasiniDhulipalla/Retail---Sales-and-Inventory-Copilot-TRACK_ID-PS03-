from io import BytesIO
import pandas as pd

def csv_report(frame) -> bytes:
    return frame.to_csv(index=False).encode("utf-8")

def excel_report(frame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer: frame.to_excel(writer, index=False, sheet_name="Report")
    return output.getvalue()
