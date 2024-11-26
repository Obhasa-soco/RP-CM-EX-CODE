import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore

# Locate the path to serviceAccountKey.json
base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
cred_path = os.path.join(base_dir, 'serviceAccountKey.json')

# Initialize Firebase with the credential path
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()


# Function to upload a single record to Firebase
def upload_manual_entry(voucher_code, total_quota, qr_code, collection_name):
    try:
        doc_ref = db.collection(collection_name).document(voucher_code)
        doc_ref.set({
            'voucher_code': voucher_code,
            'total_quota': total_quota,
            'qr_code': qr_code,
        })
        messagebox.showinfo("Success", "Manual entry uploaded to Firebase.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to upload data to Firebase: {e}")


# Function to upload CSV file to Firebase
def upload_csv_to_firebase(csv_file_path, collection_name):
    try:
        df = pd.read_csv(csv_file_path)
        required_columns = {'voucher_code', 'total_quota', 'qr_code'}
        if not required_columns.issubset(df.columns):
            messagebox.showerror("Error",
                                 "CSV file is missing required columns: 'voucher_code', 'total_quota', or 'qr_code'.")
            return

        for index, row in df.iterrows():
            doc_ref = db.collection(collection_name).document(row['voucher_code'])
            doc_ref.set({
                'voucher_code': row['voucher_code'],
                'total_quota': row['total_quota'],
                'qr_code': row['qr_code'],
            })
        messagebox.showinfo("Success", f"Uploaded {len(df)} records to Firebase.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to upload data to Firebase: {e}")


# Function to handle file selection
def select_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv")],
        title="Choose a CSV file"
    )
    if file_path:
        file_label.config(text=f"Selected File: {file_path}")
        global selected_file_path
        selected_file_path = file_path


# Function to trigger upload when "Send CSV" button is clicked
def send_csv_to_firebase():
    if selected_file_path:
        collection_name = 'voucher_data'  # Set your collection name
        upload_csv_to_firebase(selected_file_path, collection_name)
    else:
        messagebox.showerror("Error", "No file selected.")


# Function to trigger manual entry upload
def send_manual_entry_to_firebase():
    voucher_code = voucher_code_entry.get()
    total_quota = total_quota_entry.get()
    qr_code = qr_code_entry.get()
    if voucher_code and total_quota and qr_code:
        collection_name = 'voucher_data'  # Set your collection name
        upload_manual_entry(voucher_code, total_quota, qr_code, collection_name)
    else:
        messagebox.showerror("Error", "Please enter Voucher Code, Total Quota, and QR Code.")


# GUI Setup
app = tk.Tk()
app.title("CSV and Manual Entry to Firebase Uploader")
app.geometry("400x400")

# Label for file selection
file_label = tk.Label(app, text="No file selected.", fg="blue")
file_label.pack(pady=10)

# Button to browse files
browse_button = tk.Button(app, text="Upload CSV File", command=select_file)
browse_button.pack(pady=5)

# Button to send file to Firebase
send_csv_button = tk.Button(app, text="Send CSV to Firebase", command=send_csv_to_firebase)
send_csv_button.pack(pady=5)

# Manual Entry Section
manual_entry_label = tk.Label(app, text="Manual Entry:", font=("Helvetica", 12))
manual_entry_label.pack(pady=10)

# Voucher Code entry field
voucher_code_label = tk.Label(app, text="Voucher Code:")
voucher_code_label.pack()
voucher_code_entry = tk.Entry(app)
voucher_code_entry.pack()

# Total Quota entry field
total_quota_label = tk.Label(app, text="Total Quota:")
total_quota_label.pack()
total_quota_entry = tk.Entry(app)
total_quota_entry.pack()

# QR Code entry field
qr_code_label = tk.Label(app, text="QR Code:")
qr_code_label.pack()
qr_code_entry = tk.Entry(app)
qr_code_entry.pack()

# Button to send manual entry to Firebase
send_manual_button = tk.Button(app, text="Send Manual Entry to Firebase", command=send_manual_entry_to_firebase)
send_manual_button.pack(pady=10)

# Run the app
app.mainloop()
