import json
import os

from patterns.system_architecture import dm


class Database:

    def create(self, model: str, new_data: dict) -> dict:
        new_data = dm.create(model, new_data)
        return new_data

    def list(self, model: str) -> list:
        return dm.list(model)

    def retrieve(self, model: str, pk: str) -> dict | None:
        return dm.retrieve(model, pk)

    def update(self, model: str, pk: str, new_data: dict) -> dict | None:
        return dm.update(model, pk, new_data)

    def delete(self, model, pk: str) -> bool:
        return dm.delete(model, str(pk))


db = Database()
