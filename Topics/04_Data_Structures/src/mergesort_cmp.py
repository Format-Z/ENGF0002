def test_simple_sort():
    compare = lambda x,y: x <= y
    assert mergesort([2, 3, 1, 4, 0], compare) == [0, 1, 2, 3, 4]

def test_simple_sort10(): # Test edge cases, for 1 or no elements.
    compare = lambda x,y: x <= y
    assert mergesort([190], compare) == [190]
    assert mergesort([], compare) == []

def test_simple_longlist():
    compare = lambda x,y: x <= y
    import random
    n = 1000
    lst = list(range(n))
    random.shuffle(lst) # Shuffle at random in-place
    sorted_lst = mergesort(lst, compare)
    assert sorted_lst == list(range(n))


def mergesort(lst, compare):
    if len(lst) <= 1:
        return lst.copy()
    pivot = len(lst) // 2
    lst1 = mergesort(lst[:pivot], compare)
    lst2 = mergesort(lst[pivot:], compare)
    return mergelists(lst1, lst2, compare)

def mergelists(lst1, lst2, compare):
    ''' Merge two sorted lists into a sorted list.'''
    merged_lst = []
    len1 = len(lst1)
    len2 = len(lst2)
    index1 = 0
    index2 = 0
    # while either list has any items left
    while index1 < len1 or index2 < len2:
        if (index2 == len2    #either we've used all of lst2
            or (index1 != len1     #or both lists have elements left
                and compare(lst1[index1], lst2[index2]))): 
            merged_lst.append(lst1[index1])
            index1 += 1    
        else:
            merged_lst.append(lst2[index2])
            index2 += 1
    return merged_lst

def test_order():
    items = ["A", "BB", "CCC", "DD", "E"]

    def compare_lex(l1, l2):
        return l1 <= l2
    assert mergesort(items, compare_lex) == items

    def compare_len(l1, l2):
        return len(l1) <= len(l2)
    assert mergesort(items, compare_len) \
        == ["A", "E", "BB", "DD", "CCC"]    

def test_order_lambda():
    items = ["A", "BB", "CCC", "DD", "E"]

    assert mergesort(items, lambda x,y: x <= y) == items
    assert mergesort(items, lambda x,y: len(x) <= len(y)) \
        == ["A", "E", "BB", "DD", "CCC"]    



if __name__ == "__main__":
    test_simple_longlist()
