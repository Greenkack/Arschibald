"""
Preis-Modifikations-Engine für Multi-PDF Angebotserstellung

Diese Engine sorgt dafür, dass Multi-PDFs teurer sind als das Standard-Angebot
durch progressive Aufschläge basierend auf Firmen-Position.

Logik:
- Standard-Angebot bleibt unverändert (günstiger)
- Firma 1: Basis-Aufschlag (z.B. +15%)
- Firma 2: Basis + Progression (z.B. +20%)
- Firma 3: Basis + 2×Progression (z.B. +25%)
- usw.
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def calculate_base_price(
    products: Dict[str, dict],
    labor_costs: float = 0,
    additional_costs: float = 0,
    profit_margin: float = 0
) -> float:
    """
    Berechne Basis-Preis aus Produkten + Zusatzkosten
    
    Args:
        products: {category: product_dict} mit Produkten
        labor_costs: Arbeitskosten
        additional_costs: Zusätzliche Kosten
        profit_margin: Gewinnmarge in Prozent
    
    Returns:
        Basis-Preis in Euro
    """
    total = 0.0
    
    # Summiere Produktpreise
    for category, product in products.items():
        if product:
            # Preis kann verschiedene Keys haben
            price = (
                product.get('price') or 
                product.get('Preis') or 
                product.get('price_eur') or 
                product.get('Preis_EUR') or
                0
            )
            
            # Menge berücksichtigen (z.B. Anzahl Module)
            quantity = product.get('quantity') or product.get('Anzahl') or 1
            
            product_total = price * quantity
            total += product_total
            
            logger.info(f"{category}: {price}€ × {quantity} = {product_total}€")
    
    # Zusatzkosten
    total += labor_costs
    total += additional_costs
    
    logger.info(f"Basis-Preis vor Gewinnmarge: {total:.2f}€")
    
    # Gewinnmarge anwenden
    if profit_margin > 0:
        total = total * (1 + profit_margin / 100)
        logger.info(f"Basis-Preis nach Gewinnmarge ({profit_margin}%): {total:.2f}€")
    
    return total


def apply_modification(
    base_price: float,
    modifier_pct: float,
    firm_index: int = 0,
    progression_pct: float = 0
) -> float:
    """
    Wende Preis-Modifikation an mit progressivem Aufschlag
    
    Args:
        base_price: Basis-Preis ohne Modifikation
        modifier_pct: Basis-Aufschlag in Prozent (z.B. 15)
        firm_index: Index der Firma (0-basiert)
        progression_pct: Progressions-Aufschlag pro Firma in Prozent (z.B. 5)
    
    Returns:
        Modifizierter Preis in Euro
    
    Beispiel:
        base_price = 17000€
        modifier_pct = 15%
        progression_pct = 5%
        
        Firma 0 (Index 0): 17000 × 1.15 = 19.550€
        Firma 1 (Index 1): 17000 × 1.20 = 20.400€
        Firma 2 (Index 2): 17000 × 1.25 = 21.250€
    """
    # Berechne totalen Aufschlag
    total_modifier = modifier_pct + (progression_pct * firm_index)
    
    # Wende Modifikation an
    modified_price = base_price * (1 + total_modifier / 100)
    
    logger.info(
        f"Firma {firm_index + 1}: {base_price:.2f}€ × {1 + total_modifier/100:.3f} "
        f"(+{total_modifier:.1f}%) = {modified_price:.2f}€"
    )
    
    return modified_price


def get_progressive_modifier(
    base_modifier: float,
    firm_count: int,
    firm_index: int,
    progression_factor: float = 1.0
) -> float:
    """
    Berechne progressiven Aufschlag basierend auf Firmen-Position
    
    Args:
        base_modifier: Basis-Aufschlag in Prozent
        firm_count: Gesamtanzahl Firmen
        firm_index: Index der Firma (0-basiert)
        progression_factor: Faktor für Progression (1.0 = linear)
    
    Returns:
        Totaler Aufschlag in Prozent
    """
    # Linear: base + (index * progression)
    # Mit Faktor: base + (index * progression * factor)
    
    if firm_count <= 1:
        return base_modifier
    
    # Progression pro Firma
    progression_per_firm = (base_modifier / firm_count) * progression_factor
    
    total_modifier = base_modifier + (progression_per_firm * firm_index)
    
    logger.info(
        f"Progressive Modifikation Firma {firm_index + 1}/{firm_count}: "
        f"{base_modifier}% + ({progression_per_firm:.2f}% × {firm_index}) = {total_modifier:.2f}%"
    )
    
    return total_modifier


def calculate_price_with_products(
    products: Dict[str, dict],
    analysis_results: Optional[dict] = None,
    profit_margin: float = 0,
    modifier_pct: float = 0,
    firm_index: int = 0,
    progression_pct: float = 0
) -> Dict[str, float]:
    """
    Vollständige Preisberechnung mit Produkten, Analyse und Modifikation
    
    Args:
        products: Produkt-Dictionary
        analysis_results: Analyse-Resultate mit Kosten
        profit_margin: Gewinnmarge in Prozent
        modifier_pct: Basis-Aufschlag für Multi-PDF
        firm_index: Firmen-Index
        progression_pct: Progressive Aufschlag-Steigerung
    
    Returns:
        {
            'base_price': Basis-Preis,
            'modified_price': Modifizierter Preis,
            'modifier_applied': Angewandter Aufschlag in %
        }
    """
    logger.info(f"=== Preisberechnung Firma {firm_index + 1} ===")
    
    # Labor costs aus analysis_results
    labor_costs = 0
    additional_costs = 0
    
    if analysis_results:
        labor_costs = analysis_results.get('labor_costs', 0)
        additional_costs = analysis_results.get('additional_costs', 0)
    
    # Basis-Preis berechnen
    base_price = calculate_base_price(
        products=products,
        labor_costs=labor_costs,
        additional_costs=additional_costs,
        profit_margin=profit_margin
    )
    
    # Modifikation anwenden (nur für Multi-PDFs, nicht für Standard)
    if modifier_pct > 0:
        modified_price = apply_modification(
            base_price=base_price,
            modifier_pct=modifier_pct,
            firm_index=firm_index,
            progression_pct=progression_pct
        )
        
        total_modifier = modifier_pct + (progression_pct * firm_index)
    else:
        modified_price = base_price
        total_modifier = 0
    
    result = {
        'base_price': base_price,
        'modified_price': modified_price,
        'modifier_applied': total_modifier
    }
    
    logger.info(f"Resultat: Basis={base_price:.2f}€, Modifiziert={modified_price:.2f}€, Aufschlag={total_modifier:.1f}%")
    
    return result
