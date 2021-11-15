class A:
    cls_str: str = 'A'
    def __init__(self):
        self.a = 1
    def func_a(self):
        print('a')

class B(A):
    cls_str: str = 'B'
    def __init__(self):
        self.b = 2

    def func_b(self):
        print('b')
    
    @classmethod
    def cast(cls, some_a: A):
        """Cast an A into a B."""
        assert isinstance(some_a, A)
        some_a.__class__ = cls  # now mymethod() is available
        assert isinstance(some_a, B)
        return some_a

class C(B):
    cls_str: str = 'C'
    def __init__(self):
        self.c = 3
    def func_c(self):
        print('c')

a = A()
print(type(a))
print("str: {}".format(a.cls_str))

a = B.cast(a)
print(type(a))
a.func_b()
print("str: {}".format(a.cls_str))

a = C.cast(a)
print(type(a))
a.func_c()
print("str: {}".format(a.cls_str))

def sqlalchemy_to_pydantic(
    db_model: Type, *, exclude: Container[str] = []
) -> Type[BaseModel]:
    """
    Mostly copied from https://github.com/tiangolo/pydantic-sqlalchemy
    """
    mapper = inspect(db_model)
    fields = {}
    for attr in mapper.attrs:
        if isinstance(attr, ColumnProperty):
            if attr.columns:
                column = attr.columns[0]
                python_type = column.type.python_type
                name = attr.key
                if name in exclude:
                    continue
                default = None
                if column.default is None and not column.nullable:
                    default = ...
                fields[name] = (python_type, default)
    pydantic_model = create_model(
        db_model.__name__, **fields  # type: ignore
    )
    return pydantic_model 