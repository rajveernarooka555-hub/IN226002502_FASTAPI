from fastapi import FastAPI

app = FastAPI()

# The full list of 7 products
products = [
     {"id": 1, "name": "Wireless Mouse", "price": 799, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
    {"id": 4, "name": "USB Cable", "price": 199, "category": "Electronics", "in_stock": False},

    # Q1 - Added products
    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "in_stock": False},
]

@app.get("/products")
async def get_all_products():
    # This structure matches the "Expected Output" precisely
    return {
        "products": products,
        "total": len(products)
    }

# Q2. Add a category filter endpoint
# Task: New endpoint to filter by category
@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):
    result = [p for p in products if p["category"] == category_name]
    if not result:
        return {"error": "No products found in this category"}
    return {
        "category": category_name,
        "products": result,
        "total": len(result)
    }
# Q3. Show only in-stock products
@app.get("/products/instock")
async def get_instock_products():
    # Filter only products where in_stock is True
    available_items = [p for p in products if p["in_stock"] is True]
    
    # Return the specific keys requested: "in_stock_products" and "count"
    return {
        "in_stock_products": available_items,
        "count": len(available_items)
    }
# Q4. Build a store info endpoint
@app.get("/store/summary")
async def get_store_summary():
    # Calculate stock counts
    in_stock_count = len([p for p in products if p["in_stock"]])
    out_of_stock_count = len([p for p in products if not p["in_stock"]])
    
    # Get unique categories using a set
    unique_categories = list(set(p["category"] for p in products))
    
    return {
        "store_name": "My E-commerce Store",
        "total_products": len(products),
        "in_stock": in_stock_count,
        "out_of_stock": out_of_stock_count,
        "categories": unique_categories
    }

#Q5. Search product by name
@app.get("/products/search/{keyword}")
async def search_products(keyword: str):
    # Search logic: check if keyword exists within the product name (case-insensitive)
    query = keyword.lower()
    results = [p for p in products if query in p["name"].lower()]
    
    # Check if any matches were found
    if not results:
        return {"message": "No products matched your search"}
    
    # Return the matches and the count
    return {
        "results": results,
        "total_matches": len(results)
    }

# Q.Bonus: Cheapest & most expensive product
@app.get("/products/deals")
async def get_product_deals():
    # If the list is empty, handle it gracefully
    if not products:
        return {"error": "No products available in the store"}

    # Find the cheapest product
    best_deal = min(products, key=lambda p: p["price"])
    
    # Find the most expensive product
    premium_pick = max(products, key=lambda p: p["price"])
    
    return {
        "best_deal": best_deal,
        "premium_pick": premium_pick
    }
