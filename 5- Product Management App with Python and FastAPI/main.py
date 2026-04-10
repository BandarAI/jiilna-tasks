from fastapi import FastAPI
from pydantic import BaseModel
import sys
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QListWidget, QMessageBox
from threading import Thread
import uvicorn
import time

# product class
class Product:
    def __init__(self, name, amount, price):
        self.name = name
        self.amount = amount
        self.price = price

    @property
    def total(self):
        return self.amount * self.price

    def __str__(self):
        return f"{self.name} | Amount: {self.amount} | Price: {self.price:.2f} | Total: {self.total:.2f}"

# fastapi config
app = FastAPI()
products = []

class ProductModel(BaseModel):
    name: str
    amount: int
    price: float

@app.get("/products")
def get_products():
    return [str(p) for p in products]

@app.post("/products")
def add_product(product: ProductModel):
    p = Product(product.name, product.amount, product.price)
    products.append(p)
    return {"message": "Product added", "product": str(p)}

# pyqt interface
API_URL = "http://127.0.0.1:8000"

class ProductGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Product Manager")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Product Name")
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount")
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Price")
        self.add_button = QPushButton("Add Product")
        self.list_widget = QListWidget()

        self.layout.addWidget(self.name_input)
        self.layout.addWidget(self.amount_input)
        self.layout.addWidget(self.price_input)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(QLabel("Products List:"))
        self.layout.addWidget(self.list_widget)

        self.add_button.clicked.connect(self.add_product)

        self.name_input.returnPressed.connect(self.add_product)
        self.amount_input.returnPressed.connect(self.add_product)
        self.price_input.returnPressed.connect(self.add_product)

        self.fetch_list()

    def add_product(self):
        try:
            name = self.name_input.text()
            amount = int(self.amount_input.text())
            price = float(self.price_input.text())
        except ValueError:
            QMessageBox.warning(self, "error", "enter valid amount and price")
            return

        # post to api
        try:
            response = requests.post(f"{API_URL}/products", json={
                "name": name,
                "amount": amount,
                "price": price
            })
            if response.status_code == 200:
                # add product to list and clean the inputs
                self.fetch_list()
                self.name_input.clear()
                self.amount_input.clear()
                self.price_input.clear()
            else:
                QMessageBox.warning(self, "error", f"failed to add product: {response.text}")
        except Exception as e:
            QMessageBox.critical(self, "error", f"cant reach API: {e}")

    def fetch_list(self):
        self.list_widget.clear()
        try:
            response = requests.get(f"{API_URL}/products")
            if response.status_code == 200:
                for item in response.json():
                    self.list_widget.addItem(item)
            else:
                QMessageBox.warning(self, "error", f"failed to fetch products: {response.text}")
        except Exception as e:
            QMessageBox.critical(self, "error", f"cant reach API: {e}")

# run fastapi
def run_api():
    uvicorn.run(app, host="127.0.0.1", port=8000)

# call pyqt
def run_gui():
    app = QApplication(sys.argv)
    gui = ProductGUI()
    gui.show()
    sys.exit(app.exec())




if __name__ == "__main__":
    api_thread = Thread(target=run_api, daemon=True)
    api_thread.start()
    time.sleep(1) 
    run_gui()
