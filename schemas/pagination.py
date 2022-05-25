from extension import ma

from flask import request
from flask_sqlalchemy import Pagination
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from urllib.parse import urlencode



class PaginationSchema(ma.SQLAlchemySchema):
    class Meta:
        ordered = True
    links = fields.Method("get_pagination_links")
    page = fields.Integer(dump_only=True)
    pages = fields.Integer(dump_only=True)
    per_page = fields.Integer(dump_only=True)
    total = fields.Integer(dump_only=True)
    
    @staticmethod
    def get_url(page):
        query_args = request.args.to_dict()
        query_args['page'] = page
        return '{}?{}'.format(request.base_url, urlencode(query_args))
    
    def get_pagination_links(self, paginated_objects: Pagination):
        pagination_links = {
            'first': self.get_url(page=1),
            'last': self.get_url(page=paginated_objects.pages)
        }
        if paginated_objects.has_prev:
            pagination_links['prev'] = self.get_url(page=paginated_objects.prev_num)
        if paginated_objects.has_next:
            pagination_links['next'] = self.get_url(page=paginated_objects.next_num)
        return pagination_links
