import csv
import json
import os
from tkinter import filedialog, messagebox

def export_to_csv(data, filename=None):
    if not filename:
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not filename:
        return
    try:
        # Предполагаем, что data - словарь с ключами
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for key, rows in data.items():
                writer.writerow([key])
                if rows:
                    writer.writerow(rows[0].keys() if rows else [])
                    for row in rows:
                        writer.writerow(row.values())
        messagebox.showinfo("Успех", f"Экспортировано в {filename}")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def export_to_json(data, filename=None):
    if not filename:
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if not filename:
        return
    try:
        # Преобразуем rows в список dict
        out = {}
        for key, rows in data.items():
            out[key] = [dict(row) for row in rows]
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Успех", f"Экспортировано в {filename}")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))