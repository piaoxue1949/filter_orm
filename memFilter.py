""""
https://github.com/etipsin/filter_orm
"""
import re
import operator
from pythonds.basic.stack import Stack


class MemFilter:

    @staticmethod
    def is_null(left_value, value: bool):
        if value:
            return left_value is None
        return left_value is not None

    @staticmethod
    def is_blank(left_value, value: bool):
        if value:
            return left_value == ""
        return left_value != ""

    @staticmethod
    def is_range(left_value, value, l_close=True, r_close=False):
        try:
            min_value, max_value = value[0], value[1]
            flag = True
            if min_value is not None:
                flag &= (left_value >= min_value)
            if max_value is not None:
                flag &= (left_value <= max_value)
            if not l_close:
                flag &= (min_value != left_value)
            if not r_close:
                flag &= (left_value != max_value)
            return flag
        except Exception:
            pass
        return False

    @staticmethod
    def is_startswith(left_value, value, ignore_case=False):
        try:
            if ignore_case:
                return left_value.lower().startswith(value.lower())
            return left_value.startswith(value)
        except Exception:
            pass
        return False

    @staticmethod
    def is_endswith(left_value, value, ignore_case=False):
        try:
            if ignore_case:
                return left_value.lower().endswith(value.lower())
            return left_value.endswith(value)
        except Exception:
            pass
        return False

    @staticmethod
    def is_contains(left_value, value, ignore_case=False):
        try:
            if ignore_case:
                return left_value.lower().find(value.lower()) >= 0
            return left_value.find(value) >= 0
        except Exception:
            pass
        return False

    @staticmethod
    def is_regex_match(left_value, value, ignore_case=False):
        if ignore_case:
            match = re.match(value, left_value, re.I)
        else:
            match = re.match(value, left_value)
        return match is not None

    @classmethod
    def get_functions(cls, op, value, attr):
        def get_left_value(item):
            l_v = item
            if attr:
                if isinstance(item, dict):
                    l_v = item.get(attr)
                elif hasattr(item, attr):
                    l_v = getattr(item, attr)
            return l_v

        __functions = {
            "in": lambda x: get_left_value(x) in value,
            "eq": lambda x: get_left_value(x) == value,
            "lt": lambda x: get_left_value(x) < value,
            "lte": lambda x: get_left_value(x) <= value,
            "gte": lambda x: get_left_value(x) >= value,
            "gt": lambda x: get_left_value(x) > value,
            "ne": lambda x: get_left_value(x) != value,
            "range": lambda x: cls.is_range(get_left_value(x), value),
            "range00": lambda x: cls.is_range(get_left_value(x), value, False, False),
            "range01": lambda x: cls.is_range(get_left_value(x), value, False, True),
            "range10": lambda x: cls.is_range(get_left_value(x), value, True, False),
            "range11": lambda x: cls.is_range(get_left_value(x), value, True, True),
            "isnull": lambda x: cls.is_null(get_left_value(x), value),
            "isblank": lambda x: cls.is_blank(get_left_value(x), value),
            "startswith": lambda x: cls.is_startswith(get_left_value(x), value),
            "istartswith": lambda x: cls.is_startswith(get_left_value(x), value, ignore_case=True),
            "endswith": lambda x: cls.is_endswith(get_left_value(x), value),
            "iendswith": lambda x: cls.is_endswith(get_left_value(x), value, ignore_case=True),
            "contains": lambda x: cls.is_contains(get_left_value(x), value),
            "icontains": lambda x: cls.is_contains(get_left_value(x), value, ignore_case=True),
            "regex": lambda x: cls.is_regex_match(get_left_value(x), value),
            "iregex": lambda x: cls.is_regex_match(get_left_value(x), value, ignore_case=True),
        }
        return __functions[op]

    def __init__(self, data=None):
        """初始化"""
        self.__data = data or []
        self.__filters = []

    def set_data(self, data):
        """填充数据"""
        self.__data = data

    def __iter__(self):
        """迭代"""
        for i in self.__data:
            try:
                if self.__check_item(i):
                    yield i
            except TypeError:
               pass

    def datas(self):
        """获取筛选的列表"""
        return [i for i in self]

    def first(self):
        first = None
        for i in self:
            first = i
            break
        return first

    def __get_filters(self):
        """获取筛选器"""
        return self.__filters

    def _merge_filters(self, oper):
        """合并的筛选器处理功能"""
        filters = self.__get_filters()
        if filters:
            filters[0]["operator"] = oper

        return filters

    def __add_filters(self, ar_filters, kw_filters, oper):
        for arg in ar_filters:
            self.__filters.extend(arg._merge_filters(oper))

        functs = []
        for key, value in kw_filters.items():
            attr, funct = key.split("__", maxsplit=1)
            functs.append(self.get_functions(funct, value, attr))
        if functs:
            self.__filters.append({"filters": functs,
                                   "operator": oper})

    def filter(self, *args, **kwargs):
        """筛选器链的工作方式--and"""
        self.__add_filters(args, kwargs, "AND")

        return self

    def _or(self, *args, **kwargs):
        """筛选器链的工作方式为 or（内部为 and）"""
        self.__add_filters(args, kwargs, "OR")

        return self

    def _not(self, *args, **kwargs):
        """否定条件"""
        self.__add_filters(args, kwargs, "NOT")

        return self

    def __create_expr(self, item):
        """创建表达式"""
        expr = []
        for i in self.__filters:
            expr.extend(["AND", not all([j(item) for j in i["filters"]])] if i["operator"] == "NOT" else
                        [i["operator"], all([j(item) for j in i["filters"]])])
        return expr[1:]

    @staticmethod
    def __infix_to_postfix(infix_expr):
        """从后缀窗体转换为后缀窗体"""
        prec = {"AND": 2, "OR": 1} # 操作优先级
        op_stack = Stack()
        post_fix_list = []
        token_list = infix_expr

        for token in token_list:
            if token not in ("AND", "OR"):
                post_fix_list.append(token)
            else:
                while (not op_stack.isEmpty()) and \
                        (prec[op_stack.peek()] >= prec[token]):
                    post_fix_list.append(op_stack.pop())
                op_stack.push(token)

        while not op_stack.isEmpty():
            post_fix_list.append(op_stack.pop())

        return post_fix_list

    @staticmethod
    def __calc_expression(expr):
        """表达式计算"""
        operators = {'AND': operator.and_, 'OR': operator.or_}
        stack = [0]
        for token in expr:
            stack.append(operators[token](stack.pop(), stack.pop()) if token in operators else token)

        return stack.pop()

    def __check_item(self, item):
        """项目筛选"""
        expr = self.__create_expr(item)
        expr = self.__infix_to_postfix(expr)

        return self.__calc_expression(expr)




