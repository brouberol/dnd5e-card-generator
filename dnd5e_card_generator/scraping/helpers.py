from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag


class StrictTag(Tag):
    def find(self, *args, **kwargs) -> "StrictTag":
        tag = super().find(*args, **kwargs)
        if not tag:
            raise ValueError("Tag not found")
        return tag

    def find_all(self, *args, **kwargs) -> ResultSet["StrictTag"]:
        rs = super().find(*args, **kwargs)
        if not rs:
            raise ValueError("Tag not found")
        return rs


class StrictBeautifulSoup(BeautifulSoup):
    def find(self, *args, **kwargs) -> StrictTag:
        tag = super().find(*args, **kwargs)
        if not tag:
            raise ValueError("Tag not found")
        return tag
