import unittest
from magic import Magic


class TestMagicFilter(unittest.TestCase):
    def setUp(self):
        self.m = Magic()

    def test_filter_and_or(self):
        self.m.set_data([0, 1, 2, 3, 5, 7])
        self.m.filter(__lt=5, __gt=2)._or(__eq=1)

        self.assertEqual(self.m.get_filter_data(), [1, 3])

    def test_filter_with_object(self):
        m1 = Magic()
        m1.filter(__lt=5, __gt=2)._or(__eq=1)

        self.m.set_data([0, 1, 2, 3, 5, 7])
        self.m.filter(m1)

        self.assertEqual(self.m.get_filter_data(), [1, 3])

    def test_filter_with_objects(self):
        m1 = Magic()
        m1.filter(__lt=5, __gt=2)

        m2 = Magic()
        m2.filter(__in=[3])

        self.m.set_data([0, 1, 2, 3, 4, 5, 7])
        self.m.filter(m1)._not(m2)

        self.assertEqual(self.m.get_filter_data(), [4])

    def test_filter_and_not(self):
        self.m.set_data(range(15))
        self.m.filter(__gt=5)._not(__gte=7, __lte=11)

        self.assertEqual(self.m.get_filter_data(), [6, 12, 13, 14])

    def test_filter_and_or_not(self):
        self.m.set_data(range(100))
        self.m.filter(__gt=3).filter(__lte=5)._or(__lt=20, __gt=14)._not(__eq=15)

        self.assertEqual(self.m.get_filter_data(), [4, 5, 16, 17, 18, 19])

    def test_filter_object_and_gt(self):
        class Square:
            def __init__(self, a, b):
                self.a = a
                self.b = b
        data = []
        for i in range(10):
            data.append(Square(i, i**2))

        self.m.set_data(data)
        self.m.filter(a__gt=5)

        self.assertEqual(len(self.m.get_filter_data()), 4)

    def test_filter_object_and_gt_lte_same_attr(self):
        class Square:
            def __init__(self, a, b):
                self.a = a
                self.b = b
        data = []
        for i in range(10):
            data.append(Square(i, i**2))

        self.m.set_data(data)
        self.m.filter(a__gt=5, a__lte=8)

        self.assertEqual(len(self.m.get_filter_data()), 3)

    def test_filter_object_and_gt_lte_diff_attr(self):
        class Square:
            def __init__(self, a, b):
                self.a = a
                self.b = b
        data = []
        for i in range(10):
            data.append(Square(i, i**2))

        self.m.set_data(data)
        self.m.filter(a__gt=5, b__gte=49)

        self.assertEqual(len(self.m.get_filter_data()), 3)

    def test_filter_object_and_not_gt_lte_diff_attr(self):
        class Square:
            def __init__(self, a, b):
                self.a = a
                self.b = b
        data = []
        for i in range(10):
            data.append(Square(i, i**2))

        self.m.set_data(data)
        self.m.filter(a__gt=5, b__gte=49)._not(a__eq=7)

        self.assertEqual(len(self.m.get_filter_data()), 2)

    def test_filter_object_error_attr(self):
        class Square:
            def __init__(self, a, b):
                self.a = a
                self.b = b
        data = []
        for i in range(10):
            data.append(Square(i, i**2))

        self.m.set_data(data)
        self.m.filter(a__gt=5, b__gte=49).filter(c__eq=7)

        self.assertEqual(len(self.m.get_filter_data()), 0)
