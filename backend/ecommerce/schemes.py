from typing import Any, Dict, List

import yaml
from rest_framework.schemas.openapi import AutoSchema

from service.views import ApiVersioning


class ApiVersioningSchema(AutoSchema):
    def get_path_parameters(self, path: str, method: str) -> List[Dict[str, Any]]:
        parameters = super().get_path_parameters(path, method)
        for parameter in parameters:
            if parameter['name'] == ApiVersioning.version_param and parameter['in'] == 'path':
                parameter['schema']['default'] = ApiVersioning.default_version

        return parameters


class CustomOrderSchema(ApiVersioningSchema):
    def get_operation(self, path: str, method: str) -> Dict[str, Any]:
        operation = super().get_operation(path, method)
        if method == 'POST' and path.endswith('register_order/'):
            operation['requestBody'] = yaml.safe_load('''
                required: true
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                products:
                                    type: array
                                    items:
                                        type: object
                                        properties:
                                            cuantity:
                                                type: integer
                                            product:
                                                type: string
                                        required:
                                            - cuantity
                                            - product
                            required:
                                - products
                ''')

        elif method == 'PUT' and path.endswith('update_order/'):
            operation['requestBody'] = yaml.safe_load('''
                required: true
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                products:
                                    type: array
                                    items:
                                        type: object
                                        properties:
                                            cuantity:
                                                type: integer
                                            product:
                                                type: string
                                        required:
                                            - cuantity
                                            - product
                            required:
                                - products
                ''')

        return operation
