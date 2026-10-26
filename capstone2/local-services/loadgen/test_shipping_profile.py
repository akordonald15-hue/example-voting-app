"""Dependency-free routing contract tests; no network or Locust process."""
import ast
from pathlib import Path
import unittest

source = ast.parse(Path(__file__).with_name('robot-shop.py').read_text())
function = next(node for node in source.body if isinstance(node, ast.FunctionDef) and node.name == 'shipping_destination')
scope = {'choice': lambda values: values[0]}
exec(compile(ast.Module(body=[function], type_ignores=[]), '<shipping-profile>', 'exec'), scope)
destination = scope['shipping_destination']

class Client:
    def __init__(self, code='us', cities=None):
        self.code, self.cities, self.paths = code, cities, []
    def get(self, path, headers):
        self.paths.append(path)
        data = [{'code':self.code, 'name':self.code}] if path.endswith('/codes') else self.cities
        return type('Response', (), {'json': lambda self: data})()

class ShippingProfileTests(unittest.TestCase):
    def test_default_upstream_route_unchanged(self):
        client=Client(cities=[{'uuid':1}])
        self.assertEqual(destination(client,{},'upstream')[1]['uuid'],1)
        self.assertEqual(client.paths[-1],'/api/shipping/cities/us')
    def test_browser_route_exercises_large_countries(self):
        for code,prefix in [('us','new'),('in','new'),('gb','lon')]:
            client=Client(code,[{'uuid':2}]);destination(client,{},'browser')
            self.assertEqual(client.paths[-1],f'/api/shipping/match/{code}/{prefix}')
            self.assertEqual(len(client.paths),2)
    def test_empty_unknown_or_invalid_profile_fails_without_retry(self):
        for code,cities,profile in [('us',[],'browser'),('zz',[],'browser'),('us',[],'invalid')]:
            client=Client(code,cities)
            with self.assertRaises(ValueError):destination(client,{},profile)
            self.assertLessEqual(len(client.paths),2)

if __name__ == '__main__': unittest.main()
