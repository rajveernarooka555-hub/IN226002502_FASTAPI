from fastapi import FastAPI,Response, status, Query, HTTPException
from pydantic import BaseModel, Field


app = FastAPI()

# Data 


products = [

    {'id': 1, 'name': 'Wireless Mouse', 'price': 499, 'category': 'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook',       'price':  99, 'category': 'Stationery',  'in_stock': True},
    {'id': 3, 'name': 'USB Hub',        'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set',        'price':  49, 'category': 'Stationery',  'in_stock': True},

]



class NewProduct(BaseModel):                           
    name: str  = Field(..., min_length=2, max_length=100)
    price:int  = Field(..., gt=0)
    category: str  = Field(..., min_length=2)
    in_stock: bool = True

@app.get('/products')

def get_all_products():

    return {'products': products, 'total': len(products)}

 

@app.get('/products/filter')

def filter_products(
    category:  str  = Query(None, description='Electronics or Stationery'),
    min_price: int  = Query(None, description='Minimum price'),
    max_price: int  = Query(None, description='Maximum price'),
    in_stock:  bool = Query(None, description='True = in stock only'),

):

    result = filter_products(category, min_price, max_price, in_stock)
    return {'filtered_products': result, 'count': len(result)}


def find_product(product_id: int):
    """Search products list by ID. Returns product dict or None."""
    for p in products:
        if p['id'] == product_id:
            return p
    return None

@app.put("products/discount")
def apply_discount(category: str=Query(...), discount_percent: int=Query(...)):
    return{
        "category": category,
        "discount_percent": discount_percent
    }

@app.post('/products')

def add_product(new_product: NewProduct, response: Response):

    # Check for duplicate name (case-insensitive)

    existing_names = [p['name'].lower() for p in products]
    if new_product.name.lower() in existing_names:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Product with this name already exists'}

    # Auto-generate next ID

    next_id = max(p['id'] for p in products) + 1
    product = {
        'id':       next_id,
        'name':     new_product.name,
        'price':    new_product.price,
        'category': new_product.category,
        'in_stock': new_product.in_stock,

    }
    products.append(product)
    response.status_code = status.HTTP_201_CREATED
    return {'message': 'Product added', 'product': product}







#Question : 5
@app.get("/products/audit")
def products_audit():
    total_products = len(products)

    in_stock_products = [p for p in products if p["in_stock"]]
    in_stock_count = len(in_stock_products)

    out_of_stock_names = [p["name"] for p in products if not p["in_stock"]]

    total_stock_value = sum(p["price"] * 10 for p in in_stock_products)

    most_expensive = max(products, key=lambda x: x["price"])

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_names": out_of_stock_names,
        "total_stock_value": total_stock_value,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        }
    }


#Bonus
@app.put("/products/discount")

def apply_discount(category: str, discount_percent: int):
    
    found = False
    
    for product in products:
        if product["category"] == category:
            discount = product["price"] * discount_percent / 100
            product["price"] = product["price"] - discount
            found = True

    if not found:
        raise HTTPException(status_code=404, detail="Category not found")

    return {"message": f"{discount_percent}% discount applied to {category} products"}

#Question : 3
@app.delete('/products/{product_id}')
def delete_product(product_id: int, response: Response):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Product not found'}

    products.remove(product)
    return {'message': f"Product '{product['name']}' deleted"}

#Question : 2

@app.put('/products/{product_id}')
def update_product(
    product_id: int,
    response:   Response,
    in_stock:   bool = Query(None, description='Update stock status'),
    price:      int  = Query(None, description='Update price'),

):

    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Product not found'}

    if in_stock is not None:     # must use 'is not None' — False is a valid value
        product['in_stock'] = in_stock

    if price is not None:
        product['price'] = price

    return {'message': 'Product updated', 'product': product}