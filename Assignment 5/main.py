from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel, Field
import math

app = FastAPI()

# ── MODELS ─────────────────────────────────────────

class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=100)
    delivery_address: str = Field(..., min_length=10)

class NewProduct(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    price: int = Field(..., gt=0)
    category: str = Field(..., min_length=2)
    in_stock: bool = True


# ── DATA ─────────────────────────────────────────

products = [
    {'id':1,'name':'Wireless Mouse','price':499,'category':'Electronics','in_stock':True},
    {'id':2,'name':'Notebook','price':99,'category':'Stationery','in_stock':True},
    {'id':3,'name':'USB Hub','price':799,'category':'Electronics','in_stock':False},
    {'id':4,'name':'Pen Set','price':49,'category':'Stationery','in_stock':True},
]

orders = []
order_counter = 1


# ── HELPER FUNCTIONS ─────────────────────────────────────────

def find_product(product_id:int):
    for p in products:
        if p['id'] == product_id:
            return p
    return None

def calculate_total(product, quantity):
    return product['price'] * quantity


# ── BASIC ENDPOINTS ─────────────────────────────────────────

@app.get("/")
def home():
    return {"message":"Welcome to our E-commerce API"}

@app.get("/products")
def get_all_products():
    return {"products":products,"total":len(products)}


# =====================================================
# Q1 SEARCH PRODUCTS
# =====================================================

@app.get("/products/search")
def search_products(keyword:str):

    result=[p for p in products if keyword.lower() in p["name"].lower()]

    if not result:
        return {"message":f"No products found for: {keyword}"}

    return {
        "keyword":keyword,
        "total_found":len(result),
        "products":result
    }


# =====================================================
# Q2 SORT PRODUCTS
# =====================================================

@app.get("/products/sort")
def sort_products(
    sort_by:str="price",
    order:str="asc"
):

    if sort_by not in ["price","name"]:
        return {"error":"sort_by must be 'price' or 'name'"}

    reverse=True if order=="desc" else False

    sorted_products=sorted(products,key=lambda x:x[sort_by],reverse=reverse)

    return {
        "sort_by":sort_by,
        "order":order,
        "products":sorted_products
    }


# =====================================================
# Q3 PAGINATION
# =====================================================

@app.get("/products/page")
def paginate_products(
    page:int=1,
    limit:int=2
):

    start=(page-1)*limit
    end=start+limit

    total_pages=math.ceil(len(products)/limit)

    return {
        "page":page,
        "limit":limit,
        "total_pages":total_pages,
        "products":products[start:end]
    }


# =====================================================
# Q5 SORT BY CATEGORY THEN PRICE
# =====================================================

@app.get("/products/sort-by-category")
def sort_by_category():

    sorted_products=sorted(products,key=lambda x:(x["category"],x["price"]))

    return {"products":sorted_products}


# =====================================================
# Q6 BROWSE (SEARCH + SORT + PAGINATE)
# =====================================================

@app.get("/products/browse")
def browse_products(
    keyword:str=None,
    sort_by:str="price",
    order:str="asc",
    page:int=1,
    limit:int=4
):

    result=products

    if keyword:
        result=[p for p in result if keyword.lower() in p["name"].lower()]

    reverse=True if order=="desc" else False
    result=sorted(result,key=lambda x:x[sort_by],reverse=reverse)

    total_found=len(result)
    total_pages=math.ceil(total_found/limit)

    start=(page-1)*limit
    end=start+limit

    paged=result[start:end]

    return {
        "keyword":keyword,
        "sort_by":sort_by,
        "order":order,
        "page":page,
        "limit":limit,
        "total_found":total_found,
        "total_pages":total_pages,
        "products":paged
    }


# =====================================================
# ORDER SEARCH (Q4)
# =====================================================

@app.get("/orders/search")
def search_orders(customer_name:str):

    result=[o for o in orders if customer_name.lower() in o["customer_name"].lower()]

    if not result:
        return {"message":f"No orders found for {customer_name}"}

    return {
        "customer_name":customer_name,
        "total_found":len(result),
        "orders":result
    }


# =====================================================
# BONUS ORDER PAGINATION
# =====================================================

@app.get("/orders/page")
def paginate_orders(page:int=1,limit:int=3):

    start=(page-1)*limit
    end=start+limit

    total_pages=math.ceil(len(orders)/limit)

    return {
        "page":page,
        "limit":limit,
        "total_pages":total_pages,
        "orders":orders[start:end]
    }


# ── ADD PRODUCT ─────────────────────────────────────────

@app.post("/products")
def add_product(new_product:NewProduct,response:Response):

    existing=[p['name'].lower() for p in products]

    if new_product.name.lower() in existing:
        response.status_code=status.HTTP_400_BAD_REQUEST
        return {"error":"Product with this name already exists"}

    next_id=max(p['id'] for p in products)+1

    product={
        "id":next_id,
        "name":new_product.name,
        "price":new_product.price,
        "category":new_product.category,
        "in_stock":new_product.in_stock
    }

    products.append(product)

    response.status_code=status.HTTP_201_CREATED

    return {"message":"Product added","product":product}


# ── UPDATE PRODUCT ─────────────────────────────────────────

@app.put("/products/{product_id}")
def update_product(product_id:int,response:Response,
                   in_stock:bool=Query(None),
                   price:int=Query(None)):

    product=find_product(product_id)

    if not product:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"error":"Product not found"}

    if in_stock is not None:
        product['in_stock']=in_stock

    if price is not None:
        product['price']=price

    return {"message":"Product updated","product":product}


# ── DELETE PRODUCT ─────────────────────────────────────────

@app.delete("/products/{product_id}")
def delete_product(product_id:int,response:Response):

    product=find_product(product_id)

    if not product:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"error":"Product not found"}

    products.remove(product)

    return {"message":f"Product '{product['name']}' deleted"}


# ── GET SINGLE PRODUCT ─────────────────────────────────────────

@app.get("/products/{product_id}")
def get_product(product_id:int):

    product=find_product(product_id)

    if not product:
        return {"error":"Product not found"}

    return {"product":product}


# ── ORDERS ─────────────────────────────────────────

@app.post("/orders")
def place_order(order_data:OrderRequest):

    global order_counter

    product=find_product(order_data.product_id)

    if not product:
        return {"error":"Product not found"}

    if not product['in_stock']:
        return {"error":f"{product['name']} is out of stock"}

    total=calculate_total(product,order_data.quantity)

    order={
        "order_id":order_counter,
        "customer_name":order_data.customer_name,
        "product":product['name'],
        "quantity":order_data.quantity,
        "delivery_address":order_data.delivery_address,
        "total_price":total,
        "status":"confirmed"
    }

    orders.append(order)
    order_counter+=1

    return {"message":"Order placed successfully","order":order}


@app.get("/orders")
def get_orders():
    return {"orders":orders,"total_orders":len(orders)}
