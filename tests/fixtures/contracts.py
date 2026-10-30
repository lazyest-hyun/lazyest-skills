"""Synthetic contract: nonnegative integer IDs/quantities; extra fields ignored.

String IDs require an explicit adapter. Supplier details live only in suppliers.
"""

def required_integer(row, field):
    if field not in row:
        raise ValueError(f'{field}: required field missing')
    value = row[field]
    if type(value) is not int or value < 0:
        raise ValueError(f'{field}: expected nonnegative integer')
    return value


def api_to_ui(row):
    return {'itemId': required_integer(row, 'id'),
            'quantity': required_integer(row, 'quantity')}


def convert_string_id(row):
    """Explicit import-only conversion, never applied by api_to_ui itself."""
    converted = dict(row)
    value = converted.get('id')
    if isinstance(value, str) and value.isascii() and value.isdecimal():
        converted['id'] = int(value)
    return converted


def import_rows(rows, adapter=None):
    accepted, errors = [], []
    for number, original in enumerate(rows, 1):
        try:
            candidate = adapter(original) if adapter else original
            accepted.append(api_to_ui(candidate))
        except ValueError as error:
            errors.append(f'row {number}: {error}')
    return accepted, errors


class Inventory:
    def __init__(self):
        self.suppliers = {}
        self.items = {}

    def add_supplier(self, record):
        supplier_id = required_integer(record, 'id')
        if supplier_id in self.suppliers:
            raise ValueError('duplicate supplier ID')
        self.suppliers[supplier_id] = dict(record)

    def add_item(self, record):
        item = api_to_ui(record)
        supplier_id = required_integer(record, 'supplierId')
        if supplier_id not in self.suppliers:
            raise ValueError('supplierId: unknown supplier')
        if item['itemId'] in self.items:
            raise ValueError('duplicate item ID')
        self.items[item['itemId']] = {**item, 'supplierId': supplier_id}

    def update_supplier(self, supplier_id, *, name, email):
        self.suppliers[supplier_id].update(name=name, email=email)

    def display_item(self, item_id):
        item = self.items[item_id]
        return {**item, 'supplier': dict(self.suppliers[item['supplierId']])}
