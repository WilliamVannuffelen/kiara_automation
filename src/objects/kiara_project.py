from src.objects.kiara_work_item import KiaraWorkItem
from src.objects.general_tasks import general_tasks


class KiaraProject:
    def __init__(self, name: str):
        self.name = name
        self.items = []

    @property
    def is_general_task(self) -> bool:
        return self.name in general_tasks

    def add_work_item(self, item: KiaraWorkItem):
        if item.project == self.name:
            self.items.append(item)
        else:
            raise ValueError(
                f"Item project '{item.project}' does not match group project '{self.name}'"
            )

    def __repr__(self):
        return f"KiaraWorkItemGroup(project={self.name}, items={self.items})"
