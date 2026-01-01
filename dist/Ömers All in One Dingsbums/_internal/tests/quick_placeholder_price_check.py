from pdf_template_engine import placeholders

pd = {'project_details': {}}
ci = {'name': 'X'}

cases = [{'name': 'Case A',
          'ar': {'total_investment_brutto': 10000.0,
                  'total_investment_netto': 8403.36}},
         {'name': 'Case B',
          'ar': {'total_investment_brutto': 12000.0,
                  'total_investment_netto': 10084.03}},
         ]

for c in cases:
    res = placeholders.build_dynamic_data(pd, c['ar'], ci)
    print(c['name'])
    print('  final_end_preis_formatted =',
          res.get('final_end_preis_formatted'))
    print('  preis_mit_mwst_formatted  =', res.get('preis_mit_mwst_formatted'))
