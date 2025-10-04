from api.extensions import db
from api.lib.database import CRUDModel, SurrogatePK


class DcimRackLayout(CRUDModel, SurrogatePK):
    __tablename__ = 'dcim_rack_layouts'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    layout_name = db.Column(db.String(100), nullable=False)
    layout_data = db.Column(db.JSON, nullable=False)
