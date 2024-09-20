# application/models/master_models/models.py
from ... import db
from datetime import datetime
import uuid

import os
from ...utils import get_wib_date, map_attr


class Product(db.Model):
    __tablename__ = "master_product"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    price = db.Column(db.Integer, default=0)

    rowstatus = db.Column(db.Integer, default=1)
    created_by = db.Column(db.String(100), nullable=True)
    created_date = db.Column(db.DateTime, default=get_wib_date)
    modified_by = db.Column(db.String(100), nullable=True)
    modified_date = db.Column(db.DateTime, onupdate=get_wib_date)

    def to_json(self, attr=[]):
        if attr:
            return map_attr(self, attr)

        return {
            "name": self.name,
        }