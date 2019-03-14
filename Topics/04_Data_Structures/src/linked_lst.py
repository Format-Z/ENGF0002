class Node():
    def __init__(self, value):
        self.value = value
        self.next = None

    def print_lst(self):
        print(self.value)
        if self.next != None:
            self.next.print_lst()
        
