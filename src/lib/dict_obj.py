
from collections.abc import Mapping

class DictObj(Mapping):

    def __init__(self, d):
        self.attrs = d.keys()

        for k, v in d.items():
            if isinstance(v, dict):
                v = DictObj(v)
            elif isinstance(v, (list, tuple)):
                v = [DictObj(x) for x in v]

            setattr(self, k, v)

    def __str__(self):
        results = list()
        for k in self.attrs:
            v = getattr(self, k)
            if isinstance(v, DictObj):
                results.append("{}:\n\t{}".format(k, str(v).replace("\n", "\n\t")))
            else:
                results.append("{}: {}".format(k, v))

        return "\n".join(results)

    def __len__(self):
        return len(self.attrs)

    def __getitem__(self, k):
        return getattr(self, k)

    def __iter__(self):
        return iter(self.attrs)
