from app.svc.Services import Services as svc
from app.models.ModelNode import PrsModelNodeAttrs, PrsModelNodeCreate, PrsModelNodeEntry

class PrsDataStorageCreateAttrs(PrsModelNodeAttrs):
    """Attributes for request for /dataStorages/ POST"""
    
class PrsDataStorageCreate(PrsModelNodeCreate):
    """Request /tags/ POST"""
    attributes: PrsDataStorageCreateAttrs = PrsDataStorageCreateAttrs()

class PrsDataStorageEntry(PrsModelNodeEntry):
    objectClass: str = 'prsDataStorage'

    def __init__(self, data: PrsDataStorageCreate):
        
        super().__init__(data)
        

    