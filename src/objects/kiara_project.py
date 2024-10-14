from src.objects.kiara_work_item import KiaraWorkItem


class KiaraProject:
    def __init__(self, name: str):
        self.name = name
        self.items = []

    def add_work_item(self, item: KiaraWorkItem):
        if item.project == self.name:
            self.items.append(item)
        else:
            raise ValueError(
                f"Item project '{item.project}' does not match group project '{self.name}'"
            )

    def __repr__(self):
        return f"KiaraWorkItemGroup(project={self.name}, items={self.items})"
