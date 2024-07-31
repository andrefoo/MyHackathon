import json
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import webbrowser
import sys

def load_json(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

def fetch_image(url):
    response = requests.get(url)
    img_data = response.content
    img = Image.open(BytesIO(img_data))
    img.thumbnail((200, 200))
    return ImageTk.PhotoImage(img)

def open_url(url):
    webbrowser.open_new(url)

def show_details(event, tree, data, details_frame):
    selected_item = tree.selection()[0]
    item_data = tree.item(selected_item, 'values')
    item = next((item for item in data if item['title'] == item_data[0]), None)
    
    for widget in details_frame.winfo_children():
        widget.destroy()
    
    title_label = tk.Label(details_frame, text=f"Title: {item_data[0]}", font=("Helvetica", 16), bg="#f0f0f0", pady=5)
    title_label.grid(row=0, column=0, sticky='w')

    source_label = tk.Label(details_frame, text=f"Source: {item_data[1]}", font=("Helvetica", 12), pady=5)
    source_label.grid(row=1, column=0, sticky='w')

    if 'price' in item:
        price_label = tk.Label(details_frame, text=f"Price: {item_data[2]}", font=("Helvetica", 12), pady=5)
        price_label.grid(row=2, column=0, sticky='w')
        
        stock_label = tk.Label(details_frame, text=f"In Stock: {item_data[3]}", font=("Helvetica", 12), pady=5)
        stock_label.grid(row=3, column=0, sticky='w')
    
    url_label = tk.Label(details_frame, text="URL: Click here to view product", font=("Helvetica", 12), fg="blue", cursor="hand2")
    url_label.grid(row=4, column=0, pady=5)
    url_label.bind("<Button-1>", lambda e: open_url(item['link']))

    img = fetch_image(item['thumbnail'])
    img_label = tk.Label(details_frame, image=img)
    img_label.image = img
    img_label.grid(row=5, column=0, pady=10)

def main(filepath):
    data = load_json(filepath)
    shopping_data = [item for item in data if 'price' in item]
    other_data = [item for item in data if 'price' not in item]

    root = tk.Tk()
    root.title("JSON Data Viewer")

    style = ttk.Style()
    style.configure("Treeview", font=("Helvetica", 12))
    style.configure("Treeview.Heading", font=("Helvetica", 14, "bold"))

    header = tk.Label(root, text="Product Listings", font=("Helvetica", 20, "bold"), bg="#f8f8f8", pady=10)
    header.pack(fill=tk.X)

    tree_frame = ttk.Frame(root)
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    scrollbar = ttk.Scrollbar(tree_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    shopping_tree = ttk.Treeview(tree_frame, columns=('Title', 'Source', 'Price', 'In Stock'), show='headings', yscrollcommand=scrollbar.set)
    other_tree = ttk.Treeview(tree_frame, columns=('Title', 'Source'), show='headings', yscrollcommand=scrollbar.set)
    scrollbar.config(command=lambda *args: (shopping_tree.yview(*args), other_tree.yview(*args)))
    
    for tree in [shopping_tree, other_tree]:
        tree.heading('Title', text='Title')
        tree.heading('Source', text='Source')
        tree.column('Title', anchor=tk.W, width=350)
        tree.column('Source', anchor=tk.CENTER, width=150)
        tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

    shopping_tree.heading('Price', text='Price')
    shopping_tree.heading('In Stock', text='In Stock')
    shopping_tree.column('Price', anchor=tk.CENTER, width=100)
    shopping_tree.column('In Stock', anchor=tk.CENTER, width=100)

    for item in shopping_data:
        price = item.get('price', {}).get('value', 'N/A')
        in_stock = 'Yes' if item.get('in_stock', False) else 'No'
        shopping_tree.insert('', tk.END, values=(
            item['title'],
            item['source'],
            price,
            in_stock
        ))

    for item in other_data:
        other_tree.insert('', tk.END, values=(
            item['title'],
            item['source']
        ))

    details_frame = ttk.Frame(root, padding="10 10 10 10")
    details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    shopping_tree.bind('<<TreeviewSelect>>', lambda event: show_details(event, shopping_tree, shopping_data, details_frame))
    other_tree.bind('<<TreeviewSelect>>', lambda event: show_details(event, other_tree, other_data, details_frame))

    footer = tk.Label(root, text="End of Listings", font=("Helvetica", 12, "italic"), bg="#f8f8f8", pady=10)
    footer.pack(fill=tk.X)

    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <filepath>")
    else:
        main(sys.argv[1])
