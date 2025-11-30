/**
 * Comparison View Component (Modern - shadcn/ui)
 * 
 * Side-by-side comparison of different system configurations
 */

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { ArrowRight, Check } from 'lucide-react';

interface ComparisonViewProps {
  combined: any;
  solarOnly: any;
  heatPumpOnly: any;
}

export const ComparisonView: React.FC<ComparisonViewProps> = ({
  combined,
  solarOnly,
  heatPumpOnly,
}) => {
  const formatCurrency = (value: number) => {
    return `${value.toLocaleString('de-DE', { minimumFractionDigits: 0 })} €`;
  };

  const comparisonData = [
    {
      label: 'Investitionskosten',
      combined: formatCurrency(combined?.totalInvestment || 45000),
      solar: formatCurrency(solarOnly?.totalInvestment || 22000),
      heatPump: formatCurrency(heatPumpOnly?.totalInvestment || 28000),
    },
    {
      label: 'Jährliche Ersparnis',
      combined: formatCurrency(combined?.annualSavings || 3200),
      solar: formatCurrency(solarOnly?.annualSavings || 1400),
      heatPump: formatCurrency(heatPumpOnly?.annualSavings || 1600),
    },
    {
      label: 'Amortisationszeit',
      combined: `${combined?.paybackPeriod || 14} Jahre`,
      solar: `${solarOnly?.paybackPeriod || 16} Jahre`,
      heatPump: `${heatPumpOnly?.paybackPeriod || 17} Jahre`,
    },
    {
      label: 'ROI (25 Jahre)',
      combined: `${combined?.roi || 156}%`,
      solar: `${solarOnly?.roi || 142}%`,
      heatPump: `${heatPumpOnly?.roi || 138}%`,
    },
    {
      label: 'CO₂-Einsparung/Jahr',
      combined: `${(combined?.co2Reduction || 4800).toLocaleString('de-DE')} kg`,
      solar: `${(solarOnly?.co2Reduction || 2100).toLocaleString('de-DE')} kg`,
      heatPump: `${(heatPumpOnly?.co2Reduction || 2500).toLocaleString('de-DE')} kg`,
    },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ArrowRight className="h-5 w-5" />
          System-Vergleich
        </CardTitle>
        <CardDescription>
          Vergleich verschiedener Systemkonfigurationen
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[200px]">Kriterium</TableHead>
              <TableHead className="text-center">
                <Badge variant="default">Kombiniert</Badge>
              </TableHead>
              <TableHead className="text-center">
                <Badge variant="outline">Nur PV</Badge>
              </TableHead>
              <TableHead className="text-center">
                <Badge variant="outline">Nur Wärmepumpe</Badge>
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {comparisonData.map((row, index) => (
              <TableRow key={index}>
                <TableCell className="font-medium">{row.label}</TableCell>
                <TableCell className="text-center font-semibold text-primary">
                  {row.combined}
                </TableCell>
                <TableCell className="text-center">{row.solar}</TableCell>
                <TableCell className="text-center">{row.heatPump}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-green-50 dark:bg-green-950 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Check className="h-5 w-5 text-green-600" />
              <span className="font-semibold">Bester ROI</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Kombiniertes System bietet höchste Rendite
            </p>
          </div>

          <div className="p-4 bg-blue-50 dark:bg-blue-950 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Check className="h-5 w-5 text-blue-600" />
              <span className="font-semibold">Schnellste Amortisation</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Kürzeste Amortisationszeit durch Synergien
            </p>
          </div>

          <div className="p-4 bg-orange-50 dark:bg-orange-950 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Check className="h-5 w-5 text-orange-600" />
              <span className="font-semibold">Höchste CO₂-Reduktion</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Maximaler Umweltbeitrag durch Kombination
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
