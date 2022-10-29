import json

import patterns.creational as M
from patterns.system_architecture import dm


def get_cart(user_pk: str):
    cart = dm.retrieve('carts', user_pk)
    if not cart:
        dm.cursor.execute("INSERT OR REPLACE INTO carts(rowid, cart) VALUES(?, '{}')", (user_pk,))
        dm.connect.commit()
        return {}
    try:
        return json.loads(json.loads(cart['cart']))
    except TypeError:
        return json.loads(cart['cart'])


def update_cart(user_pk: str, cart_items: dict = None) -> None:
    if cart_items is None:
        cart_items = {}
    cart_items = json.dumps(cart_items)
    new_cart = {"cart": f"'{json.dumps(cart_items)}'"}
    dm.update('carts', user_pk, new_cart)


def clear_cart(user_pk):
    cart_items = {}
    update_cart(user_pk, cart_items=cart_items)


def add_to_cart(user_pk: str, model_name: str, model_pk: str, quantity: int = 1) -> dict:
    cart = get_cart(user_pk)
    old_quantity = cart.setdefault(model_name, {}).setdefault(model_pk, 0)
    cart[model_name][model_pk] = old_quantity + quantity
    update_cart(user_pk=user_pk, cart_items=cart)
    return cart


def remove_from_cart(user_pk: str, model_name: str, model_pk: str, quantity: int = 0) -> dict:
    cart = get_cart(user_pk)
    if quantity == 0:
        del cart[model_name][model_pk]
        update_cart(user_pk, cart)
    else:
        try:
            old_quantity = cart[model_name][model_pk]
            new_quantity = old_quantity - quantity
            if new_quantity < 1:
                del cart[model_name][model_pk]
            else:
                cart[model_name][model_pk] = new_quantity
        except KeyError:
            pass

    update_cart(user_pk=user_pk, cart_items=cart)
    return cart


def get_detailed_cart(user_pk):
    cart = get_cart(user_pk)
    result = []
    total_quantity = 0
    full_cost = 0
    for model in cart:
        for pk in cart[model]:
            item = M.Model.retrieve(model_name=model, pk=str(pk))
            if item:
                item.quantity = cart[model][pk]
                total_quantity += item.quantity
                item.total_cost = int(item.price) * item.quantity
                full_cost += item.total_cost
                result.append(item)

    return total_quantity, result, full_cost

# dm.cursor.execute('CREATE TABLE IF NOT EXISTS carts (cart JSON)')
# dm.cursor.execute('INSERT OR REPLACE INTO carts(rowid, items_num, cart) VALUES(1, "{}") ')
# dm.connect.commit()

# update_cart('1', {
#     "Shoes": {
#         "1": 3,
#         "2": 2
#     }
# })

# add_to_cart(user_pk='1', model_name='Shoes', model_pk='2')
# remove_from_cart(user_pk='1', model_name='Shoes', model_pk='2', quantity=1)
# clear_cart("1")
# cart_ = get_detailed_cart('1')
# #
# print(cart_, type(cart_))
# cart_ = json.loads(cart_)
# print(cart_, type(cart_))
# cart_ = json.loads(cart_)
# print(cart_, type(cart_))
# print(get_detailed_cart(1))
