from __future__ import annotations
from vcsettings import Repository
from contextlib import contextmanager


def main():
    initial_data = {
        "a": 1,
        "b": 2,
    }
    dynaconf = Dynaconf(data=initial_data)
    settings = dynaconf.get_settings()
    print(settings)
    settings["a"]

    # setting
    print("== Restore ==")
    settings["c"] = [1, 2, 3]
    print(settings)
    settings.d.restore()
    print(settings)

    print("== Save ==")
    settings["c"] = [1, 2, 3]
    print(settings)
    settings.d.save()
    print(settings)

    print("== Context Manager ==")
    print(settings)
    with settings.d():
        settings["d"] = True
        settings["e"] = False
        print(settings)
    print(settings)

    print("== Context Manager - rollback ==")
    print(settings)
    with settings.d():
        settings["f"] = {"foo": "bar", "spam": "eggs"}
        print(settings)
        raise TypeError()
    print(settings)


def getitem(self, key):
    print("intercepted")
    return self[key]


class BaseDict(dict):
    d: Dynaconf = None

    def __getitem__(self, k):
        print("intercepted", self.d.repo)
        return super().__getitem__(k)

    def __str__(self):
        # print(self.d.repo.refs)
        return super().__str__()


class LoadingSystem:
    def __init__(self, repo: Repository):
        self.repo = repo

    def load(self, load_request: str): ...

    def load_direct(self, data: dict): ...


class Dynaconf:
    def __init__(self, data: dict | None = None):
        self.repo = Repository()
        self.repo.work_tree = BaseDict()
        self.repo.work_tree.d = self
        if data:
            sha = self.repo.commit(data)
            self.repo.checkout(sha)

    def get_settings(self):
        return self.repo.work_tree

    def save(self):
        self.repo.commit(self.repo.work_tree)

    def restore(self):
        self.repo.checkout(self.repo.head)

    @contextmanager
    def __call__(self, msg: str = ""):
        try:
            print("enter context")
            yield
        except Exception:
            self.restore()
        else:
            self.save()
        print("exit context")


if __name__ == "__main__":
    exit(main())
