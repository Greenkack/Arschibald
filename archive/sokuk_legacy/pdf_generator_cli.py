#!/usr/bin/env python3
"""
pdf_generator_cli.py
Kommandozeilenschnittstelle für pdf_generator.py
Ermöglicht IPC-Integration mit Electron-App
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    """Main entry point for CLI PDF generation"""
    parser = argparse.ArgumentParser(
        description='Generate PDF using pdf_generator.py')
    parser.add_argument(
        '--config',
        required=True,
        help='JSON config file path')
    parser.add_argument('--output', help='Output PDF file path')
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
                f"🔧 Loaded config: {
                    json.dumps(
                        config,
                        indent=2)}",
                file=sys.stderr)

        # Import and use pdf_generator
        from pdf_generator import generate_offer_pdf_with_main_templates

        # Extract configuration
        project_data = config.get('project_data', {})
        analysis_results = config.get('analysis_results', {})
        company_info = config.get('company_info', {})
        pdf_options = config.get('pdf_options', {})

        # Set default output path if not provided
        if not args.output:
            output_dir = config.get('output_directory', 'output')
            os.makedirs(output_dir, exist_ok=True)
            args.output = os.path.join(
                output_dir, f"angebot_{
                    project_data.get(
                        'customer_name', 'kunde')}.pdf")

        # Generate PDF
        if args.debug:
            print("🎯 Generating PDF with template engine", file=sys.stderr)
            print(
                f"   Project Data: {
                    project_data.get(
                        'customer_name',
                        'Unknown')}",
                file=sys.stderr)
            print(f"   Output: {args.output}", file=sys.stderr)

        result_path = generate_offer_pdf_with_main_templates(
            project_data=project_data,
            analysis_results=analysis_results,
            company_info=company_info,
            output_path=args.output,
            **pdf_options
        )

        # Return success result as JSON
        result = {
            "success": True,
            "message": "PDF generated successfully",
            "output_path": result_path,
            "file_size": os.path.getsize(result_path) if os.path.exists(result_path) else 0
        }

        print(json.dumps(result))

    except Exception as e:
        # Return error result as JSON
        error_result = {
            "success": False,
            "error": str(e),
            "message": f"PDF generation failed: {e}"
        }

        print(json.dumps(error_result))
        sys.exit(1)


if __name__ == "__main__":
    main()
