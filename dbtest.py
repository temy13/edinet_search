from backend.db import insert_item


code = "aa"
filename = "bb"
key = "123"
value = "1255"
ishtml = "True"
insert_item(code, filename, key, value, ishtml)
key = u"ご主人様"
print(type(key))
insert_item(code, filename, key, value, ishtml)
