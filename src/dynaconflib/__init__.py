from vcsettings import Repository


def getitem(self, key):
    print("intercepted")
    return self[key]


class BaseDict(dict):
    def __getitem__(self, k):
        print("intercepted")
        return super().__getitem__(k)


class Dynaconf:
    def __init__(self, data: dict | None = None):
        self.repo = Repository()
        self.repo.work_tree = BaseDict()
        if data:
            sha = self.repo.commit(data)
            self.checkout(sha)

    def get_settings(self):
        return self.repo.work_tree


if __name__ == "__main__":
    dynaconf = Dynaconf()
    settings = dynaconf.get_settings()
    print(settings)
