#!/usr/bin/env python3
"""
multi_offer_generator_cli.py
Kommandozeilenschnittstelle für multi_offer_generator.py
Ermöglicht IPC-Integration mit Electron-App für Multi-PDF-Generierung
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def progress_callback(current, total, message="Processing"):
    """Progress callback that outputs JSON progress updates"""
    progress_data = {
        "current": current,
        "total": total,
        "percentage": round((current / total) * 100, 1) if total > 0 else 0,
        "message": message
    }
    print(f"PROGRESS:{json.dumps(progress_data)}", file=sys.stderr, flush=True)


def main():
    """Main entry point for CLI Multi-PDF generation"""
    parser = argparse.ArgumentParser(
        description='Generate Multi-PDFs using multi_offer_generator.py')
    parser.add_argument(
        '--config',
        required=True,
        help='JSON config file path')
    parser.add_argument(
        '--output-dir',
        help='Output directory for generated PDFs')
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output')

    args = parser.parse_args()

    try:
        # Load configuration
        with open(args.config, encoding='utf-8') as f:
            config = json.load(f)

        if args.debug:
            print(
                f"🔧 Loaded multi-PDF config: {json.dumps(config, indent=2)}", file=sys.stderr)

        # Import multi-offer generator
        from multi_offer_generator import generate_multi_offer_pdf

        # Extract configuration
        companies = config.get('companies', [])
        project_template = config.get('project_template', {})
        analysis_template = config.get('analysis_template', {})
        pdf_options = config.get('pdf_options', {})

        # Set default output directory
        if not args.output_dir:
            args.output_dir = config.get('output_directory', 'multi_output')
        os.makedirs(args.output_dir, exist_ok=True)

        if args.debug:
            print(
                f"🎯 Generating Multi-PDFs for {len(companies)} companies", file=sys.stderr)
            print(f"   Output Directory: {args.output_dir}", file=sys.stderr)

        # Initialize progress
        progress_callback(0, len(companies), "Starting multi-PDF generation")

        generated_files = []
        failed_companies = []

        for i, company in enumerate(companies):
            try:
                progress_callback(
                    i, len(companies), f"Processing {
                        company.get(
                            'name', 'Unknown Company')}")

                # Create company-specific project data
                project_data = project_template.copy()
                project_data.update({
                    'company_information': company,
                    'customer_name': f"Angebot für {company.get('name', 'Kunde')}"
                })

                # Generate output filename
                company_name = company.get(
                    'name',
                    'unknown').replace(
                    ' ',
                    '_').replace(
                    '/',
                    '_')
                output_filename = f"angebot_{company_name}_{i + 1:03d}.pdf"
                output_path = os.path.join(args.output_dir, output_filename)

                # Generate PDF for this company
                result_path = generate_multi_offer_pdf(
                    project_data=project_data,
                    analysis_results=analysis_template,
                    company_info=company,
                    output_path=output_path,
                    **pdf_options
                )

                generated_files.append({
                    "company": company.get('name', 'Unknown'),
                    "file_path": result_path,
                    "file_size": os.path.getsize(result_path) if os.path.exists(result_path) else 0,
                    "success": True
                })

            except Exception as e:
                if args.debug:
                    print(
                        f"❌ Error processing {
                            company.get(
                                'name',
                                'Unknown')}: {e}",
                        file=sys.stderr)

                failed_companies.append({
                    "company": company.get('name', 'Unknown'),
                    "error": str(e),
                    "success": False
                })

        # Final progress update
        progress_callback(
            len(companies),
            len(companies),
            "Multi-PDF generation completed")

        # Return comprehensive result as JSON
        result = {
            "success": True,
            "message": f"Multi-PDF generation completed: {
                len(generated_files)} successful, {
                len(failed_companies)} failed",
            "output_directory": args.output_dir,
            "generated_files": generated_files,
            "failed_companies": failed_companies,
            "total_companies": len(companies),
            "successful_count": len(generated_files),
            "failed_count": len(failed_companies)}

        print(json.dumps(result))

    except Exception as e:
        # Return error result as JSON
        error_result = {
            "success": False,
            "error": str(e),
            "message": f"Multi-PDF generation failed: {e}",
            "generated_files": [],
            "failed_companies": []
        }

        print(json.dumps(error_result))
        sys.exit(1)


if __name__ == "__main__":
    main()
