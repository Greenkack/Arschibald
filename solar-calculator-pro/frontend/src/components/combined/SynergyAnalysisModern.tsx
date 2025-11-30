/**
 * Synergy Analysis Component (Modern - shadcn/ui)
 * 
 * Analyzes synergy effects between PV and heat pump
 */

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Lightbulb, Zap, TrendingUp } from 'lucide-react';

interface SynergyAnalysisProps {
  solarData: any;
  heatPumpData: any;
}

export const SynergyAnalysis: React.FC<SynergyAnalysisProps> = ({ solarData, heatPumpData }) => {
  const synergyEffects = [
    {
      title: 'Eigenverbrauchsoptimierung',
      description: 'Direkte Nutzung von PV-Strom für Wärmepumpe',
      benefit: 35,
      icon: Zap,
    },
    {
      title: 'Netzentlastung',
      description: 'Reduzierung des Strombezugs aus dem Netz',
      benefit: 45,
      icon: TrendingUp,
    },
    {
      title: 'Kostensynergie',
      description: 'Optimierte Gesamtinvestition durch kombinierte Planung',
      benefit: 28,
      icon: Lightbulb,
    },
  ];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5" />
            Synergie-Effekte
          </CardTitle>
          <CardDescription>
            Vorteile der kombinierten Installation von PV-Anlage und Wärmepumpe
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {synergyEffects.map((effect, index) => {
            const Icon = effect.icon;
            return (
              <div key={index} className="space-y-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-primary/10 rounded-lg">
                      <Icon className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <h4 className="font-semibold">{effect.title}</h4>
                      <p className="text-sm text-muted-foreground">{effect.description}</p>
                    </div>
                  </div>
                  <Badge variant="secondary">{effect.benefit}%</Badge>
                </div>
                <Progress value={effect.benefit} className="h-2" />
              </div>
            );
          })}

          <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-950 rounded-lg">
            <h4 className="font-semibold mb-2">Gesamtsynergie</h4>
            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
              {Math.round((synergyEffects.reduce((sum, e) => sum + e.benefit, 0) / synergyEffects.length))}%
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              Durchschnittlicher Synergie-Vorteil gegenüber Einzellösungen
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
