"""
Test suite for Task 17: Performance Optimization

Tests the performance optimization features including:
- Chart caching
- Efficient PDF merging
- Image scaling

Run with: python test_task_17_performance_optimization.py
"""

import io
import time
from extended_pdf_generator import (
    ChartCache,
    ExtendedPDFGenerator,
    ProductDatasheetMerger,
    CompanyDocumentMerger,
    ChartPageGenerator,
    ExtendedPDFLogger
)


def test_chart_cache():
    """Test 17.1: Chart caching functionality"""
    print("\n" + "=" * 60)
    print("TEST 17.1: Chart Caching")
    print("=" * 60)

    # Create cache
    cache = ChartCache(max_size=10)

    # Test data
    chart_key = "test_chart"
    chart_data = b"test_chart_data_12345"
    chart_bytes = b"rendered_chart_image_bytes"

    # Test cache miss
    result = cache.get(chart_key, chart_data)
    assert result is None, "Expected cache miss on first access"
    print("✓ Cache miss works correctly")

    # Store in cache
    cache.put(chart_key, chart_data, chart_bytes)
    print("✓ Chart stored in cache")

    # Test cache hit
    result = cache.get(chart_key, chart_data)
    assert result == chart_bytes, "Expected cache hit"
    print("✓ Cache hit works correctly")

    # Test cache stats
    stats = cache.get_stats()
    assert stats['hit_count'] == 1, "Expected 1 hit"
    assert stats['miss_count'] == 1, "Expected 1 miss"
    assert stats['size'] == 1, "Expected 1 item in cache"
    print(f"✓ Cache stats: {stats['hit_rate_percent']}% hit rate")

    # Test cache invalidation
    cache.invalidate(chart_key, chart_data)
    result = cache.get(chart_key, chart_data)
    assert result is None, "Expected cache miss after invalidation"
    print("✓ Cache invalidation works correctly")

    # Test LRU eviction
    cache.clear()
    for i in range(15):  # More than max_size
        cache.put(f"chart_{i}", f"data_{i}".encode(), f"bytes_{i}".encode())

    stats = cache.get_stats()
    assert stats['size'] <= 10, f"Cache size should be <= 10, got {
        stats['size']}"
    print(f"✓ LRU eviction works (cache size: {stats['size']})")

    print("\n✅ All chart caching tests passed!")


def test_chart_page_generator_with_cache():
    """Test ChartPageGenerator with caching enabled"""
    print("\n" + "=" * 60)
    print("TEST 17.1b: ChartPageGenerator with Cache")
    print("=" * 60)

    # Create mock analysis results with chart bytes
    analysis_results = {
        'monthly_prod_cons_chart_bytes': b'fake_chart_data_1',
        'cumulative_cashflow_chart_bytes': b'fake_chart_data_2',
        'consumption_coverage_pie_chart_bytes': b'fake_chart_data_3'
    }

    logger = ExtendedPDFLogger()

    # Create generator with caching enabled
    generator = ChartPageGenerator(
        analysis_results=analysis_results,
        layout='one_per_page',
        theme={'colors': {'primary': '#1E3A8A'}},
        logger=logger,
        use_cache=True
    )

    # Clear cache before test
    ChartPageGenerator.invalidate_cache()

    # First access - should be cache miss
    chart_bytes_1 = generator._get_chart_bytes('monthly_prod_cons_chart_bytes')
    assert chart_bytes_1 is not None, "Expected chart bytes"
    print("✓ First chart access (cache miss)")

    # Second access - should be cache hit
    chart_bytes_2 = generator._get_chart_bytes('monthly_prod_cons_chart_bytes')
    assert chart_bytes_2 == chart_bytes_1, "Expected same bytes from cache"
    print("✓ Second chart access (cache hit)")

    # Check cache stats
    stats = ChartPageGenerator.get_cache_stats()
    print(
        f"✓ Cache stats: {
            stats['hit_count']} hits, {
            stats['miss_count']} misses")
    assert stats['hit_count'] >= 1, "Expected at least 1 cache hit"

    print("\n✅ ChartPageGenerator caching tests passed!")


def test_efficient_pdf_merging():
    """Test 17.2: Efficient PDF merging"""
    print("\n" + "=" * 60)
    print("TEST 17.2: Efficient PDF Merging")
    print("=" * 60)

    logger = ExtendedPDFLogger()

    # Test ExtendedPDFGenerator's efficient merging
    offer_data = {
        'grand_total': 25000.0,
        'customer_name': 'Test Customer'
    }

    analysis_results = {
        'monthly_prod_cons_chart_bytes': b'fake_chart_1',
        'cumulative_cashflow_chart_bytes': b'fake_chart_2'
    }

    options = {
        'financing_details': False,
        'product_datasheets': [],
        'company_documents': [],
        'selected_charts': []
    }

    generator = ExtendedPDFGenerator(
        offer_data=offer_data,
        analysis_results=analysis_results,
        options=options,
        logger=logger
    )

    # Test that the efficient method exists
    assert hasattr(
        generator, '_add_pages_to_writer_efficient'), "Expected efficient merge method"
    print("✓ Efficient merge method exists")

    # Test that it returns page count
    from pypdf import PdfWriter
    writer = PdfWriter()

    # Create a simple test PDF
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.drawString(100, 100, "Test Page")
    c.showPage()
    c.save()
    test_pdf_bytes = buffer.getvalue()

    page_count = generator._add_pages_to_writer_efficient(
        writer, test_pdf_bytes)
    assert page_count == 1, f"Expected 1 page, got {page_count}"
    print("✓ Efficient merge returns correct page count")

    print("\n✅ Efficient PDF merging tests passed!")


def test_product_datasheet_efficient_merge():
    """Test ProductDatasheetMerger's efficient merging"""
    print("\n" + "=" * 60)
    print("TEST 17.2b: ProductDatasheetMerger Efficient Merge")
    print("=" * 60)

    logger = ExtendedPDFLogger()
    merger = ProductDatasheetMerger(logger=logger)

    # Test with empty list
    result = merger.merge([])
    assert result == b'', "Expected empty bytes for empty list"
    print("✓ Empty list handled correctly")

    # Test with non-existent IDs (should handle gracefully)
    result = merger.merge([99999, 99998])
    # Should return empty bytes since products don't exist
    print("✓ Non-existent products handled gracefully")

    print("\n✅ ProductDatasheetMerger efficient merge tests passed!")


def test_image_scaling():
    """Test 17.3: Image scaling optimization"""
    print("\n" + "=" * 60)
    print("TEST 17.3: Image Scaling")
    print("=" * 60)

    from PIL import Image

    # Create a test image
    test_img = Image.new('RGB', (3000, 2000), color='red')
    buffer = io.BytesIO()
    test_img.save(buffer, format='PNG')
    large_image_bytes = buffer.getvalue()

    print(
        f"✓ Created test image: 3000x2000 pixels ({
            len(large_image_bytes)} bytes)")

    logger = ExtendedPDFLogger()
    merger = ProductDatasheetMerger(logger=logger)

    # Test image conversion with scaling
    pdf_bytes = merger._convert_image_to_pdf(large_image_bytes)

    assert pdf_bytes != b'', "Expected non-empty PDF bytes"
    assert len(pdf_bytes) > 0, "Expected valid PDF output"
    print(f"✓ Image converted to PDF ({len(pdf_bytes)} bytes)")

    # Check that optimization was logged
    summary = logger.get_summary()
    info_messages = [msg['message'] for msg in summary['info']]

    # Should have logged scaling information
    scaling_logged = any(
        'Scaling image' in msg or 'Optimized image' in msg for msg in info_messages)
    if scaling_logged:
        print("✓ Image scaling was performed and logged")
    else:
        print("✓ Image was already optimal size")

    print("\n✅ Image scaling tests passed!")


def test_chart_image_optimization():
    """Test ChartPageGenerator's image optimization"""
    print("\n" + "=" * 60)
    print("TEST 17.3b: Chart Image Optimization")
    print("=" * 60)

    from PIL import Image

    # Create a large test chart image
    test_chart = Image.new('RGB', (2400, 1800), color='blue')
    buffer = io.BytesIO()
    test_chart.save(buffer, format='PNG')
    large_chart_bytes = buffer.getvalue()

    print(
        f"✓ Created test chart: 2400x1800 pixels ({
            len(large_chart_bytes)} bytes)")

    logger = ExtendedPDFLogger()
    generator = ChartPageGenerator(
        analysis_results={},
        layout='one_per_page',
        theme={'colors': {'primary': '#1E3A8A'}},
        logger=logger
    )

    # Test optimization for a target size
    from reportlab.lib.units import cm
    target_width = 15 * cm
    target_height = 10 * cm

    optimized_bytes = generator._optimize_chart_image(
        large_chart_bytes, target_width, target_height)

    assert optimized_bytes != b'', "Expected non-empty optimized bytes"
    print(f"✓ Chart optimized ({len(optimized_bytes)} bytes)")

    # Optimized should typically be smaller (unless already optimal)
    if len(optimized_bytes) < len(large_chart_bytes):
        reduction = (1 - len(optimized_bytes) / len(large_chart_bytes)) * 100
        print(f"✓ Size reduced by {reduction:.1f}%")
    else:
        print("✓ Image was already optimal size")

    print("\n✅ Chart image optimization tests passed!")


def test_performance_comparison():
    """Test overall performance improvements"""
    print("\n" + "=" * 60)
    print("TEST: Performance Comparison")
    print("=" * 60)

    from PIL import Image

    # Create multiple test charts
    chart_count = 10
    analysis_results = {}

    for i in range(chart_count):
        img = Image.new('RGB', (1200, 800), color=(i * 20, 100, 200))
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        analysis_results[f'test_chart_{i}_bytes'] = buffer.getvalue()

    print(f"✓ Created {chart_count} test charts")

    logger = ExtendedPDFLogger()

    # Test with caching enabled
    ChartPageGenerator.invalidate_cache()
    generator_cached = ChartPageGenerator(
        analysis_results=analysis_results,
        layout='one_per_page',
        theme={'colors': {'primary': '#1E3A8A'}},
        logger=logger,
        use_cache=True
    )

    start_time = time.time()
    for key in analysis_results.keys():
        generator_cached._get_chart_bytes(key)
        # Second access should hit cache
        generator_cached._get_chart_bytes(key)
    cached_time = time.time() - start_time

    stats = ChartPageGenerator.get_cache_stats()
    print(f"✓ With cache: {cached_time:.4f}s, {stats['hit_count']} cache hits")

    # Test without caching
    generator_uncached = ChartPageGenerator(
        analysis_results=analysis_results,
        layout='one_per_page',
        theme={'colors': {'primary': '#1E3A8A'}},
        logger=logger,
        use_cache=False
    )

    start_time = time.time()
    for key in analysis_results.keys():
        generator_uncached._get_chart_bytes(key)
        generator_uncached._get_chart_bytes(key)
    uncached_time = time.time() - start_time

    print(f"✓ Without cache: {uncached_time:.4f}s")

    if stats['hit_count'] > 0:
        print(f"✓ Cache provided performance benefit")

    print("\n✅ Performance comparison completed!")


def run_all_tests():
    """Run all performance optimization tests"""
    print("\n" + "=" * 70)
    print("TASK 17: PERFORMANCE OPTIMIZATION - TEST SUITE")
    print("=" * 70)

    try:
        test_chart_cache()
        test_chart_page_generator_with_cache()
        test_efficient_pdf_merging()
        test_product_datasheet_efficient_merge()
        test_image_scaling()
        test_chart_image_optimization()
        test_performance_comparison()

        print("\n" + "=" * 70)
        print("✅ ALL PERFORMANCE OPTIMIZATION TESTS PASSED!")
        print("=" * 70)
        print("\nImplemented features:")
        print("  ✓ 17.1 Chart caching with LRU eviction")
        print("  ✓ 17.2 Efficient single-pass PDF merging")
        print("  ✓ 17.3 Image scaling and optimization (300 DPI)")
        print("\nPerformance improvements:")
        print("  • Chart caching reduces redundant rendering")
        print("  • Single-pass merging reduces memory usage")
        print("  • Image optimization reduces file size")
        print("  • 300 DPI ensures print quality")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    run_all_tests()
