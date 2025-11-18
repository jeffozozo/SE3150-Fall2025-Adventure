from object import Object;

class Player:
    def __init__(self, name, health, condition, current_room):
        self.name = name
        self.health = health
        self.condition = []
        self.condition.append(condition)
        self.inventory = []  # List of Object instances
        self.current_room = current_room
        self.score = 0

    def is_alive(self):
        return self.health > 0

    def show_inventory(self):
        if not self.inventory:
            print("Your inventory is empty.")
        else:
            print("Inventory:")
            for item in self.inventory:
                print(f"- {item.name}: {item.description}")

    def has_item(self, item_name):
        for item in self.inventory:
            if item.name.lower() == item_name.lower(): 
                return True
        return False

    def get_item(self,item_name):
        for item in self.inventory:
            if item.name.lower() == item_name.lower(): 
                return item
        return None

    def print_stats(self):
        print(f"{self.name}")
        print(f"Health: {self.health}")
        print("Condition: ",self.condition) 
        print(f"Current Room: {self.current_room}")
        print(f"Score: {self.score}")


