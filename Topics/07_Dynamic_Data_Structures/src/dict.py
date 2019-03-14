def test_dict():
    dict = {'Name': 'Mark', 'Age': 157, 'Course': 'ENGF0002'}
    print("dict['Name']: ", dict['Name'])
    print("dict['Age']: ", dict['Age'])

    dict['Age'] = 158; # update existing entry
    dict['Office'] = "MPEB 6.21"; # Add new entry
    print("dict['Name']: ", dict['Name'])
    print("dict['Age']: ", dict['Age'])

    del dict['Name'] # remove entry with key 'Name'
    dict.clear()     # remove all entries in dict
    del dict         # delete entire dictionary

