import sqlite3
from datetime import datetime

from crm import create_tables_crm, save_customer, save_project
from database import get_db_connection


def main():
    conn = get_db_connection()
    assert conn is not None, 'No DB connection'
    conn.row_factory = sqlite3.Row
    create_tables_crm(conn)

    cust = {
        'salutation': 'Herr',
        'title': '',
        'first_name': 'Streamlit',
        'last_name': 'Tester',
        'company_name': '',
        'address': 'Musterstr.',
        'house_number': '1',
        'zip_code': '12345',
        'city': 'Musterstadt',
        'state': '',
        'region': '',
        'email': 'streamlit.tester@example.com',
        'phone_landline': '',
        'phone_mobile': '',
        'income_tax_rate_percent': 0.0,
        'creation_date': datetime.now().isoformat(),
    }
    cid = save_customer(conn, cust)
    print('saved customer id:', cid)
    cur = conn.cursor()
    cur.execute(
        'SELECT id, first_name, last_name, email FROM customers WHERE id = ?', (cid,))
    print('db row:', dict(cur.fetchone()))

    proj = {
        'customer_id': cid,
        'project_name': 'PV Angebot Test',
        'project_status': 'Angebot',
        'creation_date': datetime.now().isoformat(),
    }
    pid = save_project(conn, proj)
    print('saved project id:', pid)
    cur.execute(
        'SELECT id, customer_id, project_name FROM projects WHERE id = ?', (pid,))
    print('proj row:', dict(cur.fetchone()))
    conn.close()


if __name__ == '__main__':
    main()
