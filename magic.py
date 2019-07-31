import operator
from pythonds.basic.stack import Stack


class Magic:
    __functions = {
            "in": lambda n, attr: lambda x: getattr(x, attr) in n if attr and hasattr(x, attr) else x in n,
            "eq": lambda n, attr: lambda x: getattr(x, attr) == n if attr and hasattr(x, attr) else x == n,
            "lt": lambda n, attr: lambda x: getattr(x, attr) < n if attr and hasattr(x, attr) else x < n,
            "lte": lambda n, attr: lambda x: getattr(x, attr) <= n if attr and hasattr(x, attr) else x <= n,
            "gte": lambda n, attr: lambda x: getattr(x, attr) >= n if attr and hasattr(x, attr) else x >= n,
            "gt": lambda n, attr: lambda x: getattr(x, attr) > n if attr and hasattr(x, attr) else x > n,
            "ne": lambda n, attr: lambda x: getattr(x, attr) != n if attr and hasattr(x, attr) else x != n
    }

    def __init__(self, data=None):
        """Инициализация"""
        self.__data = data or []
        self.__filters = []

    def set_data(self, data):
        """Заполнение данных"""
        self.__data = data

    def __iter__(self):
        """Итератор"""
        for i in self.__data:
            try:
                if self.__check_item(i):
                    yield i
            except TypeError:
               pass

    def get_filter_data(self):
        """Получение отфильтрованного списка"""
        return [i for i in self]

    def __get_filters(self):
        """Получение фильтров"""
        return self.__filters

    def _merge_filters(self, oper):
        """Функция обработки фильтров для слияния"""
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
            functs.append(self.__functions[funct](value, attr))
        if functs:
            self.__filters.append({"filters": functs,
                                   "operator": oper})

    def filter(self, *args, **kwargs):
        """Цепочка фильтров работает как and"""
        self.__add_filters(args, kwargs, "AND")

        return self

    def _or(self, *args, **kwargs):
        """Цепочка фильтров работает как or (внутри как and)"""
        self.__add_filters(args, kwargs, "OR")

        return self

    def _not(self, *args, **kwargs):
        """Условие отрицания"""
        self.__add_filters(args, kwargs, "NOT")

        return self

    def __create_expr(self, item):
        """Создание выражения"""
        expr = []
        for i in self.__filters:
            expr.extend(["AND", not all([j(item) for j in i["filters"]])] if i["operator"] == "NOT" else
                        [i["operator"], all([j(item) for j in i["filters"]])])
        return expr[1:]

    @staticmethod
    def __infix_to_postfix(infix_expr):
        """Преобразование из инфиксной формы в постфиксную"""
        prec = {"AND": 2, "OR": 1} # приоритеты операций
        op_stack = Stack()
        post_fix_list = []
        token_list = infix_expr

        for token in token_list:
            if token not in ("AND", "OR"):
                post_fix_list.append(token)
            elif token == '(':
                op_stack.push(token)
            elif token == ')':
                top_token = op_stack.pop()
                while top_token != '(':
                    post_fix_list.append(top_token)
                    top_token = op_stack.pop()
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
        """Вычисление выражения"""
        operators = {'AND': operator.and_, 'OR': operator.or_}
        stack = [0]
        for token in expr:
            stack.append(operators[token](stack.pop(), stack.pop()) if token in operators else token)

        return stack.pop()

    def __check_item(self, item):
        """Фильтрация элемента"""
        expr = self.__create_expr(item)
        expr = self.__infix_to_postfix(expr)

        return self.__calc_expression(expr)




