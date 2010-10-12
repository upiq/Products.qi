

class MockRows:
    def __init__(self):
        self.rows=[]
    def add(row):
        self.rows.append(row)
    def get(self,**kw):
        for x in self.rows:
            found=True
            for y in kw:
                if not getattr(x, y)==kw[y]:
                    found=False
                    break;
            if found:
                return row
        return None
    def filter(self,**kw):
        #we intend rows to be returned always for tests
        #we're not testing django
        return self
    def order_by(self, *args):
        #ordering is too hard for tests
        return self
    def __len__(self):
        return len(self.rows)
        
            
                
        
class MockDjangoObject:
    pass

class MockTable:
    def __init__(self):
        self.objects=MockRows()
    def __call__(self):
        return MockObject()

class MockDB:
    def __init__(self):
        pass