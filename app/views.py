import app.notifications as notifs
from app import cart
from my_framework.routes import route
from my_framework.templator import render
from patterns.creational import Model

cache = {}


@route('/')
def main(response):
    items = []
    items.append(Model.retrieve(model_name='Tshirts', pk='1'))
    items.append(Model.retrieve(model_name='Jackets', pk='2'))
    items.append(Model.retrieve(model_name='Shoes', pk='1'))
    items.append(Model.retrieve(model_name='Accessories', pk='1'))
    items.append(Model.retrieve(model_name='Accessories', pk='2'))
    items.append(Model.retrieve(model_name='Jackets', pk='1'))

    context = {
        "items": items
    }
    content = render(response.environ, "main.html", context=context)
    return response.ok_200(content=content)


@route('/cms/')
def cms(response):
    request = response.environ
    models = cache.get('cms_tree')
    if not models:
        models = Model.get_model_tree()
        cache['cms_tree'] = models
    context = {"models": models}

    def get_num_of_items_recursive(mdl: type):
        num_of_items = len(Model.list(model_name=mdl.__name__))
        num_of_items_in_subclasses = sum(get_num_of_items_recursive(subclass) for subclass in mdl.__subclasses__())
        return num_of_items + num_of_items_in_subclasses

    for model in context['models']:
        model['num_of_items'] = get_num_of_items_recursive(model['class'])
        subcategories = model['subcategories'][:]
        while subcategories:
            subcategory = subcategories.pop()
            subcategory['num_of_items'] = get_num_of_items_recursive(subcategory['class'])
            subcategories.extend(subcategory['subcategories'])

    if request['REQUEST_METHOD'] != 'GET':
        return response.method_not_allowed_405()

    query = request.get('query')
    if query:
        model_name = query['model']
        objects = Model.list(model_name=model_name)
        fields = Model.fields(model_name)
        context.update({
            "fields": fields,
            "objects": objects,
            "model_name": model_name
        })

    content = render(request, "cms.html", context)
    return response.ok_200(content)


@route('/cms/create/')
class CMSCreate:
    def __call__(self, response):
        context = {}
        model_name = ""
        request = response.environ
        query = request.get('query')
        if query:
            model_name = query['model']
            fields = Model.fields(model_name)
            fields = fields[1:]  # убираем pk
            context = {
                "fields": fields,
                "model_name": model_name
            }

        if request['REQUEST_METHOD'] == 'GET':
            content = render(request, "cms_create.html", context)
            return response.ok_200(content)

        if request['REQUEST_METHOD'] == 'POST':
            data = request['post-data']
            new_model = Model.create(model_name=model_name, data=data)

            # Уведомления
            if model_name != 'User':
                text = f"Добавлен новый товар {data['name']} в категорию {new_model.__class__.verbose_name}"
                notifs.notify_all_via_site(text)

            return response.redirect_303(f'/cms/?model={model_name}')


@route('/cms/copy/')
def cms_copy(response):
    request = response.environ
    query = request.get('query')
    if query:
        model_name = query['model']
        pk = int(query['pk'])
        object_list = Model.list(model_name=model_name)
        for obj in object_list:
            obj = obj.get_props()
            if obj['pk'] == pk:
                del obj['pk']
                Model.create(model_name=model_name, data=obj)
                return response.redirect_303(f'/cms/?model={model_name}')

        return response.bad_request_400()


@route('/cms/delete/')
def cms_delete(response):
    request = response.environ
    query = request.get('query')
    if query:
        model_name = query['model']
        pk = int(query['pk'])
        result = Model.delete(model_name=model_name, pk=pk)
        if result:
            return response.redirect_303(f'/cms/?model={model_name}')

    return response.bad_request_400()


@route('/notifications/')
def notifications(response):
    request = response.environ

    if request['USER'] == 'Anonymous':
        return response.bad_request_400()

    query = request.get('query')
    if query:
        read = query.get('read')
        if read:
            notifs.mark_as_read(read)
            return response.redirect_303('/notifications/')

        delete = query.get('delete')
        if delete:
            notifs.delete_one(delete)
            return response.redirect_303('/notifications/')

    context = {
        "notifications": notifs.retrieve(request["USER"].pk)
    }
    content = render(request, 'notifications.html', context=context)

    return response.ok_200(content)


@route('/catalogue/')
def catalogue(response):
    request = response.environ
    query = request.get('query')
    category = query.get('category') if query else 'Products'
    models = cache.get('catalogue_tree')
    if not models:
        products = Model.get_model_by_name('Products')
        models = Model.get_model_tree(products)
        cache['catalogue_tree'] = models

    products = Model.get_model_by_name(category)
    if products.__subclasses__():
        is_category = True
        products = products.__subclasses__()
    else:
        is_category = False
        products = Model.list(model_name=products.__name__)

    context = {
        "models": models,
        "category": category,
        "products": products,
        "products_are_categories": is_category
    }
    return response.ok_200(render(response.environ, 'catalogue.html', context))


@route('/product/')
def catalogue(response):
    request = response.environ
    product = None
    try:
        query = request.get('query')
        category = query.get('category')
        pk = query.get('pk')
        product = Model.retrieve(model_name=category, pk=pk)
    except AttributeError:
        return response.bad_request_400()

    context = {
        "product": product
    }
    return response.ok_200(render(response.environ, 'product.html', context))


@route('/cart/')
def cart_show(response):
    request = response.environ
    try:
        user = request['USER']
    except (KeyError, TypeError):
        return response.bad_request_400()

    # print(user.cart_items_num)
    content = render(request, 'cart.html')
    return response.ok_200(content=content)


@route('/cart/add/')
def cart_add(response):
    request = response.environ

    try:
        user_pk = str(request['USER'].pk)
        query = request['query']
        model_name = query['category']
        item_pk = query['pk']
        quantity = int(query.get('quantity', 1))
    except (KeyError, TypeError):
        return response.bad_request_400()

    cart.add_to_cart(user_pk, model_name, item_pk, quantity)
    return response.redirect_303('/cart/')


@route('/cart/delete/')
def cart_add(response):
    request = response.environ

    try:
        user_pk = str(request['USER'].pk)
        query = request['query']
        model_name = query['category']
        item_pk = query['pk']
        quantity = int(query.get('quantity', 1))
    except (KeyError, TypeError):
        return response.bad_request_400()

    cart.remove_from_cart(user_pk, model_name, item_pk, quantity)
    return response.redirect_303('/cart/')


@route('/cart/set/')
def cart_add(response):
    request = response.environ

    try:
        user_pk = str(request['USER'].pk)
        query = request['query']
        model_name = query['category']
        item_pk = query['pk']
        quantity = int(query.get('quantity', 0))
    except (KeyError, TypeError):
        return response.bad_request_400()

    user_cart = cart.get_cart(user_pk)
    user_cart.update({
        model_name: {
            item_pk: quantity
        }
    })
    cart.update_cart(user_pk, user_cart)

    return response.redirect_303('/cart/')


@route('/cart/clear/')
def cart_add(response):
    request = response.environ

    try:
        user_pk = str(request['USER'].pk)
    except (KeyError, TypeError):
        return response.bad_request_400()

    cart.clear_cart(user_pk)
    return response.redirect_303('/cart/')


def test_redirect(response):
    # notifs.notify_all_via_site('hi!')
    return response.ok_200(render(response.environ, 'catalogue.html'))
