from linked_lst import Node

n1 = Node(1)
n2 = Node(2)
n3 = Node(3)
n1.next = n2
n2.next = n3


print(n1.value)
print(n1.next.value)
print(n2.next.value)

n1.print_lst()
