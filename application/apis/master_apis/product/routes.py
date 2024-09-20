# application/apis/master_apis/routes.py
from flask import jsonify, request, make_response
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from .. import master_apis_blueprint
from .... import db
from ....models.master_models.models import Product

from flask_cors import cross_origin

import json
import random
import gc
import time

from ....utils import (
    AppMessageException,
    get_wib_date,
    set_attr,
    get_default_list_param,
    exception_handler,
    success_handler,
)

@master_apis_blueprint.route("/product", methods=["GET"])
@cross_origin()
def list_product():
    try:
        param = get_default_list_param(request.args, nullify_size=True)

        select_field = {
                "id": Product.id,
                "name": Product.name,
                "price": Product.price,
            }
        
        items = []                     
        data = (
            Product.query.filter(
                Product.rowstatus == 1,
            )
            .with_entities(*[select_field[n] for n in select_field.keys()])
            .order_by(db.asc(Product.id))
        )
        
        for row in data.paginate(param.get("page_index"), param.get("page_size"), False).items:
            obj = dict(zip(select_field.keys(), row))
            items.append(obj)

        results = {"data": items}
        return make_response(jsonify(success_handler(results)), 200)
    except Exception as e:
        return make_response(jsonify(exception_handler(e, default_data=[])), 500)


@master_apis_blueprint.route("/product", methods=["POST", "PUT"])
@cross_origin()
def saveupdate_product():
    try:
        # if not (current_user.is_authenticated):
        #     return make_response(jsonify(exception_handler("not logged in", 401)), 401)
        # if current_user.roles_id != 1:
        #     return make_response(jsonify(exception_handler('Forbidden access', 403)), 403)

        if not request.is_json:
            raise AppMessageException('please provide json data')

        data = request.get_json()

        name = data.get("name")
        price = data.get("price")

        if not name:
            raise AppMessageException("please provide name")
        if not price:
            raise AppMessageException("please provide price")


        product_id = data.get("id")
        
        # check if name is already available but rowstatus 0
        available_product = Product.query.filter_by(name=name,rowstatus=0).first()
        if available_product:
            known_product = available_product
            known_product.rowstatus = 1
            known_product.modified_by = "admin" if current_user.is_anonymous else current_user.username
            known_product.modified_date = get_wib_date()
            db.session.add(known_product)
            db.session.commit()
            
            results = {
                "name": known_product.name,
                "restored_data": True
            }
            
            return make_response(
            jsonify(success_handler({"data": results})), 200
        )
            
        known_product = Product.query.filter_by(id=product_id).first() if product_id else Product()
        if not known_product:
            raise AppMessageException("invalid Topic id: data not found")
               
        known_product.name = name
        known_product.price = price
        known_product.modified_by = "admin" if current_user.is_anonymous else current_user.username
        known_product.modified_date = get_wib_date()
        
        if not product_id:
            known_product.rowstatus = 1
            known_product.created_by = "admin" if current_user.is_anonymous else current_user.username
            known_product.created_date = get_wib_date()

        db.session.add(known_product)
        db.session.commit()
        
        results = {
                "name": known_product.name,
                "restored_data": False
            }
        
        return make_response(
            jsonify(success_handler({"data": results})), 200
        )
    except IntegrityError as e:
        duplicate_error = {
        'express21': {
            'status': {
                'message': "IntegrityError: Cannot add duplicated data",
                'status_code': 500
                },
                'results': {
                'data': {}
                }
            }
         }  
        return make_response(jsonify(duplicate_error), 500)
    except Exception as e:
        return make_response(jsonify(exception_handler(e)), 500)
    

@master_apis_blueprint.route("/product", methods=["DELETE"])
@cross_origin()
def delete_product():
    try:
        # if not (current_user.is_authenticated):
        #     return make_response(jsonify(exception_handler("not logged in", 401)), 401)
        # if current_user.roles_id != 1:
        #     return make_response(jsonify(exception_handler('Forbidden access', 403)), 403)
        
        id = request.args.get("id")
        if not id:
            raise AppMessageException("Please provide id to be deleted")

        
        known_product = Product.query.filter_by(id=id).first()
        if not known_product:
            raise AppMessageException('invalid topic id: data not found')
        if not known_product.rowstatus:
            raise AppMessageException('data with given id has been deleted')
        known_product.rowstatus = 0
        known_product.modified_by = "admin" if current_user.is_anonymous else current_user.username
        known_product.modified_date = get_wib_date()

        db.session.add(known_product)
        db.session.commit()

        
        return make_response(jsonify(success_handler({'data': {}})), 200)
    except Exception as e:
        return make_response(jsonify(exception_handler(e, default_data=[])), 500)
