#!/usr/bin/env python3
"""
Test script for admin panel functionality
"""

import traceback

import streamlit as st


def main():
    st.title("Admin Panel Test")

    try:
        # Test imports
        st.subheader("Import Tests")

        import database
        st.success("✅ Database module imported")

        import product_db
        st.success("✅ Product DB module imported")

        import admin_panel
        st.success("✅ Admin panel module imported")

        from matrix_loader import MatrixLoader
        st.success("✅ MatrixLoader imported")

        # Test MatrixLoader instantiation
        loader = MatrixLoader()
        st.success("✅ MatrixLoader instantiated")

        # Test admin panel function availability
        st.subheader("Function Availability Tests")

        if hasattr(admin_panel, 'render_admin_panel'):
            st.success("✅ render_admin_panel function available")
        else:
            st.error("❌ render_admin_panel function not available")

        if hasattr(admin_panel, 'render_price_matrix'):
            st.success("✅ render_price_matrix function available")
        else:
            st.error("❌ render_price_matrix function not available")

        # Test database functions
        st.subheader("Database Function Tests")

        db_functions = [
            'get_db_connection', 'save_admin_setting', 'load_admin_setting',
            'list_companies', 'add_company', 'get_company', 'update_company',
            'delete_company', 'set_default_company'
        ]

        for func_name in db_functions:
            if hasattr(database, func_name):
                st.success(f"✅ database.{func_name}")
            else:
                st.error(f"❌ database.{func_name}")

        # Test product database functions
        st.subheader("Product Database Function Tests")

        product_functions = [
            'list_products',
            'add_product',
            'update_product',
            'delete_product',
            'get_product_by_id',
            'get_product_by_model_name',
            'list_product_categories']

        for func_name in product_functions:
            if hasattr(product_db, func_name):
                st.success(f"✅ product_db.{func_name}")
            else:
                st.error(f"❌ product_db.{func_name}")

        st.subheader("Matrix Loader Test")

        # Test basic matrix operations
        try:
            # Test with empty data
            matrix = loader.load_matrix()
            if matrix is None:
                st.info("✅ MatrixLoader correctly returns None for empty data")
            else:
                st.warning("⚠️ MatrixLoader returned non-None for empty data")

            st.success("✅ MatrixLoader basic functionality works")

        except Exception as e:
            st.error(f"❌ MatrixLoader error: {e}")
            st.code(traceback.format_exc())

    except Exception as e:
        st.error(f"❌ Test failed: {e}")
        st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
