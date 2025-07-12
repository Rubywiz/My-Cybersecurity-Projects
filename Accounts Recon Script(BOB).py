import pandas as pd
from tabulate import tabulate
from fpdf import FPDF
import os
from PyPDF2 import PdfReader

# Supported file formats
SUPPORTED_EXTENSIONS = ['.xlsx', '.csv', '.txt', '.pdf']

# List to hold failed transactions
failed_transactions = pd.DataFrame()

# Define columns to extract
TARGET_COLUMNS = ['Account Number', 'Date', 'Amount', 'Transaction ID', 'Status']

def extract_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    # Assume tabular text has comma or tab separators
    try:
        df = pd.read_csv(pd.compat.StringIO(text), sep="\t|,", engine='python')
        return df
    except:
        print(f"⚠️ Could not parse table from {file_path}")
        return pd.DataFrame()

def process_file(file_path):
    ext = os.path.splitext(file_path)[-1].lower()

    try:
        if ext == '.xlsx':
            df = pd.read_excel(file_path)
        elif ext == '.csv':
            df = pd.read_csv(file_path)
        elif ext == '.txt':
            df = pd.read_csv(file_path, delimiter='\t')
        elif ext == '.pdf':
            df = extract_from_pdf(file_path)
        else:
            print(f"Unsupported file type: {file_path}")
            return pd.DataFrame()
    except Exception as e:
        print(f"Failed to read {file_path}: {e}")
        return pd.DataFrame()

    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]
    if 'status' in df.columns:
        return df[df['status'].str.lower().str.contains("fail")]
    else:
        print(f"No status column in {file_path}")
        return pd.DataFrame()

def export_to_pdf(df, output_file):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Add header
    col_names = list(df.columns)
    col_width = 190 / len(col_names)
    pdf.set_fill_color(200, 220, 255)
    for col in col_names:
        pdf.cell(col_width, 10, col, border=1, fill=True)
    pdf.ln()

    # Add rows
    for index, row in df.iterrows():
        for item in row:
            pdf.cell(col_width, 10, str(item), border=1)
        pdf.ln()

    pdf.output(output_file)
    print(f"✅ PDF exported: {output_file}")

# Main
if __name__ == "__main__":
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(title="Select transaction files", filetypes=[("All Files", "*.*")])

    for file in file_paths:
        print(f"📂 Processing: {file}")
        df = process_file(file)
        if not df.empty:
            failed_transactions = pd.concat([failed_transactions, df], ignore_index=True)

    if failed_transactions.empty:
        print("✅ No failed transactions found.")
    else:
        print("\n📉 Failed Transactions:")
        print(tabulate(failed_transactions[TARGET_COLUMNS], headers="keys", tablefmt="fancy_grid"))
        export_to_pdf(failed_transactions[TARGET_COLUMNS], "Failed_Transactions_Report.pdf")
