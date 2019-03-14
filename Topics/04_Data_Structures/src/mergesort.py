def test_simple_sort():
    assert mergesort([2, 3, 1, 4, 0]) == [0, 1, 2, 3, 4]

def test_simple_sort10(): # Test edge cases, for 1 or no elements.
    assert mergesort([190]) == [190]
    assert mergesort([]) == []

def test_simple_longlist():
    import random
    n = 1000
    lst = list(range(n))
    random.shuffle(lst) # Shuffle at random in-place
    sorted_lst = mergesort(lst)
    assert sorted_lst == list(range(n))


def mergesort(lst):
    if len(lst) <= 1:
        return lst.copy()
    pivot = len(lst) // 2
    lst1 = mergesort(lst[:pivot])
    lst2 = mergesort(lst[pivot:])
    return mergelists(lst1, lst2)

def mergelists(lst1, lst2):
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
                and lst1[index1] <= lst2[index2])):  #and lst1 is smaller
            merged_lst.append(lst1[index1])
            index1 += 1    
        else:
            merged_lst.append(lst2[index2])
            index2 += 1
    return merged_lst

if __name__ == "__main__":
    test_simple_longlist()
