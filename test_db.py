from product_db import list_products
import time

start = time.time()
products = list_products()
end = time.time()

print(f"Loaded {len(products)} products in {end - start:.4f} seconds")

start = time.time()
products2 = list_products()
end = time.time()

print(f"Loaded {len(products2)} products in {end - start:.4f} seconds (second time)")
