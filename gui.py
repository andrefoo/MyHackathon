import json
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import webbrowser

# Load JSON data
with open('./visual_matches.json', 'r') as file:
    data = json.load(file)

# Filter data to include only items that are in stock
in_stock_data = [item for item in data if item.get('in_stock', False)]

# Function to fetch image from URL
def fetch_image(url):
    response = requests.get(url)
    img_data = response.content
    img = Image.open(BytesIO(img_data))
    img.thumbnail((200, 200))
    return ImageTk.PhotoImage(img)

# Create the main window
root = tk.Tk()
root.title("JSON Data Viewer")

style = ttk.Style()
style.configure("Treeview", font=("Helvetica", 12))
style.configure("Treeview.Heading", font=("Helvetica", 14, "bold"))

# Add a header label
header = tk.Label(root, text="Product Listings", font=("Helvetica", 20, "bold"), bg="#f8f8f8", pady=10)
header.pack(fill=tk.X)

# Create a frame for the Treeview and scrollbar
tree_frame = ttk.Frame(root)
tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Add a scrollbar to the Treeview
scrollbar = ttk.Scrollbar(tree_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Create a Treeview to display the JSON data
tree = ttk.Treeview(tree_frame, columns=('Title', 'Source', 'Price', 'In Stock'), show='headings', yscrollcommand=scrollbar.set)
scrollbar.config(command=tree.yview)
tree.heading('Title', text='Title')
tree.heading('Source', text='Source')
tree.heading('Price', text='Price')
tree.heading('In Stock', text='In Stock')
tree.column('Title', anchor=tk.W, width=350)
tree.column('Source', anchor=tk.CENTER, width=150)
tree.column('Price', anchor=tk.CENTER, width=100)
tree.column('In Stock', anchor=tk.CENTER, width=100)
tree.pack(fill=tk.BOTH, expand=True)

# Populate the Treeview with filtered JSON data
for item in in_stock_data:
    price = item.get('price', {}).get('value', 'N/A')
    in_stock = 'Yes' if item.get('in_stock', False) else 'No'
    tree.insert('', tk.END, values=(
        item['title'],
        item['source'],
        price,
        in_stock
    ))

# Create a frame for displaying the details
details_frame = ttk.Frame(root, padding="10 10 10 10")
details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Function to open URL
def open_url(url):
    webbrowser.open_new(url)

# Function to display details of the selected item
def show_details(event):
    selected_item = tree.selection()[0]
    item_data = tree.item(selected_item, 'values')
    item = next((item for item in in_stock_data if item['title'] == item_data[0]), None)
    
    for widget in details_frame.winfo_children():
        widget.destroy()
    
    # Display title
    title_label = tk.Label(details_frame, text=f"Title: {item_data[0]}", font=("Helvetica", 16), bg="#f0f0f0", pady=5)
    title_label.grid(row=0, column=0, sticky='w')

    # Display source
    source_label = tk.Label(details_frame, text=f"Source: {item_data[1]}", font=("Helvetica", 12), pady=5)
    source_label.grid(row=1, column=0, sticky='w')

    # Display price
    price_label = tk.Label(details_frame, text=f"Price: {item_data[2]}", font=("Helvetica", 12), pady=5)
    price_label.grid(row=2, column=0, sticky='w')

    # Display in stock status
    stock_label = tk.Label(details_frame, text=f"In Stock: {item_data[3]}", font=("Helvetica", 12), pady=5)
    stock_label.grid(row=3, column=0, sticky='w')

    # Display URL
    url_label = tk.Label(details_frame, text="URL: Click here to view product", font=("Helvetica", 12), fg="blue", cursor="hand2")
    url_label.grid(row=4, column=0, pady=5)
    url_label.bind("<Button-1>", lambda e: open_url(item['link']))

    # Fetch and display thumbnail
    img = fetch_image(item['thumbnail'])
    img_label = tk.Label(details_frame, image=img)
    img_label.image = img
    img_label.grid(row=5, column=0, pady=10)

tree.bind('<<TreeviewSelect>>', show_details)

# Add a footer label
footer = tk.Label(root, text="End of Listings", font=("Helvetica", 12, "italic"), bg="#f8f8f8", pady=10)
footer.pack(fill=tk.X)

# Start the Tkinter event loop
root.mainloop()
