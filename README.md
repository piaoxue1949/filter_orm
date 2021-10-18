# filter_orm
类似于django ORM的filter，可以对一个序列进行筛选。序列的成员可以是对象，也可以是字典。

```
a = MemFilter(range(100))
a.filter(__gt=3).filter(__lte=5).or(__lt=20, __gt=17).not(__eq=15)

b = MemFilter([{'name': 'aaa', 'value': 1}, {'name': 'bbb', 'value': 2},{'name': 'ccc', 'value': 3}])
b.filter(value__gte=0).filter(value__lte=5)._or(value__range=(1, 2), value__eq=3)._not(value__eq=15)

```

可以链式操作，只有当它最终执行时才会进行计算。

支持一下类orm的筛选方法：
"in"
"eq"
"lt"
"lte"
"gte"
"gt"
"ne"
"range"
"isnull"
"startswith"
"istartswith"
"endswith"
"iendswith"
"contains"
"icontains"
"regex"
"iregex"


启动测试
```
python -m unittest tests/tests.py
```
