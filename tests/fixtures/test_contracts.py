import unittest
from contracts import Inventory, api_to_ui, convert_string_id, import_rows


class DataContractTests(unittest.TestCase):
    def test_maps_valid_zero_and_ignores_unknown_fields(self):
        self.assertEqual(api_to_ui({'id': 0, 'quantity': 0, 'extra': 9}),
                         {'itemId': 0, 'quantity': 0})

    def test_required_fields_reject_missing_null_string_and_boolean(self):
        for field in ('id', 'quantity'):
            for invalid in (None, '', '0', False, -1, 0.0):
                with self.subTest(field=field, invalid=invalid):
                    row = {'id': 0, 'quantity': 0, field: invalid}
                    with self.assertRaisesRegex(ValueError, field):
                        api_to_ui(row)
            row = {'id': 0, 'quantity': 0}
            del row[field]
            with self.assertRaisesRegex(ValueError, 'missing'):
                api_to_ui(row)

    def test_import_reports_rows_and_preserves_original(self):
        rows = [{'id': 0, 'quantity': 0}, {'id': None, 'quantity': 0},
                {'quantity': 0}, {'id': '0', 'quantity': 0}]
        accepted, errors = import_rows(rows)
        self.assertEqual(accepted, [{'itemId': 0, 'quantity': 0}])
        self.assertEqual(errors, ['row 2: id: expected nonnegative integer',
                                 'row 3: id: required field missing',
                                 'row 4: id: expected nonnegative integer'])
        accepted, errors = import_rows([rows[3]], adapter=convert_string_id)
        self.assertEqual(accepted, [{'itemId': 0, 'quantity': 0}])
        self.assertEqual(errors, [])
        self.assertEqual(rows[3]['id'], '0')


class SupplierTests(unittest.TestCase):
    def test_update_reflected_in_all_references_without_duplicate_details(self):
        inventory = Inventory()
        source = {'id': 0, 'name': 'Old Supplier', 'email': 'old@example.invalid'}
        inventory.add_supplier(source)
        source['name'] = 'Accidental source mutation'
        for item_id in (0, 1):
            inventory.add_item({'id': item_id, 'quantity': 0, 'supplierId': 0,
                                'supplierName': 'Stale duplicated detail'})
        self.assertEqual(inventory.display_item(0)['supplier']['name'], 'Old Supplier')
        inventory.update_supplier(0, name='New Supplier', email='new@example.invalid')
        for item_id in (0, 1):
            self.assertEqual(set(inventory.items[item_id]), {'itemId', 'quantity', 'supplierId'})
            self.assertEqual(inventory.display_item(item_id)['supplier'],
                             {'id': 0, 'name': 'New Supplier', 'email': 'new@example.invalid'})
        snapshot = inventory.display_item(0)
        snapshot['supplier']['name'] = 'Display mutation'
        self.assertEqual(inventory.display_item(1)['supplier']['name'], 'New Supplier')

    def test_orphan_and_duplicate_references_rejected(self):
        inventory = Inventory()
        with self.assertRaisesRegex(ValueError, 'unknown supplier'):
            inventory.add_item({'id': 0, 'quantity': 0, 'supplierId': 99})
        inventory.add_supplier({'id': 0, 'name': 'Supplier'})
        with self.assertRaisesRegex(ValueError, 'duplicate supplier'):
            inventory.add_supplier({'id': 0, 'name': 'Other'})
        inventory.add_item({'id': 0, 'quantity': 0, 'supplierId': 0})
        with self.assertRaisesRegex(ValueError, 'duplicate item'):
            inventory.add_item({'id': 0, 'quantity': 0, 'supplierId': 0})


if __name__ == '__main__':
    unittest.main(verbosity=2)
