
from src.excel_utils import compute_summary

def test_compute_summary_empty():
    rows = []
    res = compute_summary(rows, numeric_fields=['Quantity'])
    assert res['row_count'] == 0
    assert res['Quantity_total'] == 0
    assert res['Quantity_average'] == 0

def test_compute_summary_numbers():
    rows = [{'Quantity': 2}, {'Quantity': 3}, {'Quantity': 5}]
    res = compute_summary(rows, numeric_fields=['Quantity'])
    assert res['row_count'] == 3
    assert res['Quantity_total'] == 10
    assert res['Quantity_average'] == round(10/3,2)
