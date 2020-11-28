from telebot import types
from typing import Callable, List, Type, Dict
import re


class ArgumentError(TypeError):

    def __str__(self):
        return f"Does not convert the Argument {self.args[0]} to {self.args[1]}"


class UndefinedType(Exception):

    def __str__(self):
        return f"Do not support type {self.args[0]}"


class PayloadArgument:

    def __init__(self, name: str, argument_type: Type):
        self.name = name
        self.argument_type = argument_type

    def to_type(self, data: str):
        try:
            return self.argument_type(data)
        except TypeError:
            assert ArgumentError(data, self.argument_type)


class Route:

    def __init__(self, name: str, handler: Callable, arguments: List[PayloadArgument] = None, parsed: bool = True, middleware: List[Callable] = None):
        self.name = name
        self.handler = handler
        self.parsed = True if parsed or arguments else False
        self.middleware = middleware if middleware is not None else []
        self.arguments = arguments if arguments is not None else []

    def process_route(self, data: List[str]):
        for middleware in self.middleware:
            middleware()

        if not self.parsed:
            self.handler()
        else:
            arguments = self._get_arguments(data)
            self.handler(**arguments)

    def _get_arguments(self, data: List[str]) -> Dict:
        result = {}
        for i in range(len(self.arguments)):
            result[self.arguments[i].name] = self.arguments[i].argument_type(data[i])
        return result


class Router:

    def __init__(self):
        self._routes = []

    def add_route(self, data: str, handler: Callable, **kwargs):
        parsed = kwargs.get('parsed', False)
        middleware = kwargs.get('middleware', [])
        split_row = data.split("?")
        arguments = []
        if len(split_row) == 2:
            arguments = self.parse_route(split_row[1])
        self._routes.append(Route(split_row[0], handler, arguments, parsed, middleware))

    def add_route_multi(self, routes: List[Dict]):
        for route in routes:
            self.add_route(**route)

    @staticmethod
    def parse_route(data: str) -> List[PayloadArgument]:
        argument_templates = re.findall(r'<(.{3}:[^/]+)>', data)
        result = []
        argument_type = str
        for template in argument_templates:
            split_row = template.split(':')
            argument_name = split_row[1]
            if 'int' in split_row[0]:
                argument_type = int
            elif "str" in split_row[0]:
                argument_type = str
            else:
                assert UndefinedType(split_row[0])
            result.append(PayloadArgument(argument_name, argument_type))
        return result

    def find_route(self, data: str):
        try:
            string_to_find, arguments_data = data.split('?')
            if arguments_data[-1] == '/':
                arguments_data = arguments_data[:-1]
            arguments_data = arguments_data.split('/')
        except ValueError:
            string_to_find = data
            arguments_data = []

        for route in self._routes:
            if re.findall(string_to_find, route.name):
                route.process_route(arguments_data)
                break



