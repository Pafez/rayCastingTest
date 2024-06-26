class TapeList:
    
    def __init__(self, starter_length):
        self.length = starter_length
        self.values = []
        for i in range(starter_length):
            self.values.append(None)

    def enter(self, value):
        self.values.insert(0, value)
        if len(self.values) > self.length:
            self.values.pop()

    def get_list(self):
        return self.values
        
    def get_value(self, index):
        return self.values[index]

    def get_oldest_value(self):
        return self.values[self.length - 1]

    def enlarge(self, number_of_slots):
        self.length += number_of_slots
        return number_of_slots