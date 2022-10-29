import abc
import inspect

from my_framework.database import Database


class Prototype:
    pass


model_dict = {}


class ModelList(abc.ABCMeta):
    def __init__(cls, name, bases, clsdict):
        type.__init__(cls, name, bases, clsdict)
        if not any(base in [abc.ABC, Prototype] for base in cls.__bases__):
            model_dict[cls.__name__] = cls


class Model(abc.ABC, metaclass=ModelList):
    verbose_name = "Abstract Model"

    def __init__(self, pk):
        self.pk = pk

    def get_props(self) -> dict:
        return self.__dict__

    @classmethod
    def get_models(cls) -> dict:
        return model_dict

    @classmethod
    def get_model_by_name(cls, model_name):
        return model_dict.get(model_name)

    @classmethod
    @abc.abstractmethod
    def list(cls, *, model_name) -> list:
        models = cls.get_models()
        model = models[model_name]
        return model.list(model_name)

    @classmethod
    @abc.abstractmethod
    def retrieve(cls, *, model_name, pk):
        model = cls.get_model_by_name(model_name)
        return model.retrieve(model_name, pk)

    @classmethod
    @abc.abstractmethod
    def create(cls, *, model_name, data: dict):
        models = cls.get_models()
        model = models[model_name]
        return model.create(model_name, data)

    @classmethod
    @abc.abstractmethod
    def update(cls, *, model_name, pk: int, data: dict):
        models = cls.get_models()
        model = models[model_name]
        return model.update(model_name, pk, data)

    @classmethod
    @abc.abstractmethod
    def delete(cls, *, model_name, pk: int):
        models = cls.get_models()
        model = models[model_name]
        return model.delete(model_name, pk)

    @classmethod
    @abc.abstractmethod
    def fields(cls, model_name):
        models = cls.get_models()
        model = models[model_name]
        return model.fields()
        # return list(inspect.signature(model).parameters)

    @classmethod
    def get_model_tree(cls, model=None, result_list=None):
        if model is None:
            model = cls

        if result_list is None:
            result_list = []

        for subclass in model.__subclasses__():
            if Prototype not in subclass.__bases__:
                subclass_dict = {
                    "name": subclass.__name__,
                    "verbose_name": subclass.verbose_name,
                    "subcategories": subclass.get_model_tree(),
                    "class": subclass
                }
                result_list.append(subclass_dict)
            else:
                subclass.get_model_tree(result_list=result_list)

        return result_list


class ModelPrototype(Model, Prototype):
    db = Database()
    verbose_name = 'Model Prototype'

    def __init__(self, *, pk, **kwargs):
        super(ModelPrototype, self).__init__(pk)
        for key, value in kwargs.items():
            self.__dict__[key] = value

    @classmethod
    def list(cls, model_name):
        result = []
        objects = cls.db.list(model_name)
        for obj in objects:
            new_obj = cls(**obj)
            result.append(new_obj)
        return result

    @classmethod
    def retrieve(cls, model_name, pk):
        obj = cls.db.retrieve(model_name, pk)
        return cls(**obj)

    @classmethod
    def create(cls, model_name, data):
        params = cls.db.create(model_name, data)
        return cls(**params)

    @classmethod
    def update(cls, model_name, pk: str, data: dict):
        params = cls.db.update(model_name, pk, data)
        return cls(**params)

    @classmethod
    def delete(cls, model_name, pk: str) -> bool:
        result = cls.db.delete(model_name, pk)
        return result

    @classmethod
    def fields(cls, model_name=None):
        return list(inspect.signature(cls).parameters)[:-1]


class User(ModelPrototype):
    verbose_name = 'Пользователи'

    def __init__(self, pk, username, password, email, **kwargs):
        super(User, self).__init__(pk=pk)
        self.username = username
        self.password = password
        self.email = email


class Products(ModelPrototype):
    verbose_name = "Товары"
    img = "https://vashifinancy.ru/upload/medialibrary/1fd/1fdaed8c7a70b8224c04f4420009643e.jpg"
    description = "Товары отличного качества!"

    def __init__(self, pk, name, img, description, price, **kwargs):
        super(Products, self).__init__(pk=pk, name=name, img=img, description=description, price=price, **kwargs)


class Clothes(Products):
    verbose_name = "Одежда"
    img = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTrcAoKFbAx7jUtLxP9T00-nOug7HAbab5ZTA&usqp=CAU"
    description = "Идолы и  ложные понятия уже  пленили  человеческий  разум  и глубоко  в нем укрепились."


class UpperClothes(Clothes):
    verbose_name = "Верхняя Одежда"
    img = "https://assets.gq.ru/photos/61937162229593646945c836/4:3/w_3411,h_2558,c_limit/GettyImages-1349115323.jpg"
    description = "Построение  понятий и аксиом  через истинную индукцию есть, несомненно, подлинное средство для того, чтобы подавить и изгнать  идолы."


class Jackets(UpperClothes):
    verbose_name = "Куртки"
    img = "https://ae04.alicdn.com/kf/Hbbefb889432742fb8609942d968e55e1E.jpg"
    description = "Идолы рода находят основание в  самой природе человека, в  племени  или самом  роде  людей."


class Tshirts(UpperClothes):
    verbose_name = "Футболки"
    img = "https://incity.ru/upload/resize_cache/iblock/9fc/600_800_1/qml457bhmsjek8o23tb1r0p2vc8xfkwb.jpg"
    description = "У каждого  помимо ошибок,  свойственных роду человеческому, есть  своя  особая пещера, которая ослабляет  и искажает свет  природы."


class Shoes(Clothes):
    verbose_name = "Обувь"
    img = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR_7IYgyZNo7Su4CoHHnZBcjYSzY98LJhSUXg&usqp=CAU"
    description = "Учение об идолах представляет собой то же для истолкования природы, что и учение об опровержении софизмов - для общепринятой диалектики"


class Accessories(Products):
    verbose_name = "Аксессуары"
    img = "https://static.mvideo.ru/media/Promotions/Promo_Page/2021/July/obzor-10-aksessuarov-dlya-smartfona/obzor-10-aksessuarov-dlya-smartfona-top1-m.png"
    description = "Назовем  первый  вид  идолами рода, второй -- идолами пещеры, третий -- идолами площади."


class Categories(ModelPrototype):
    verbose_name = "Категории"

    def __init__(self, pk, name, description=None, **kwargs):
        super(Categories, self).__init__(pk=pk, name=name, description=description, **kwargs)
