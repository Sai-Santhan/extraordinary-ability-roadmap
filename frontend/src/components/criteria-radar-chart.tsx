"use client";

import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
} from "recharts";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";

interface CriterionData {
  criterion: string;
  score: number;
  fullMark: number;
}

const chartConfig = {
  score: {
    label: "Confidence",
    color: "var(--chart-1)",
  },
} satisfies ChartConfig;

export function CriteriaRadarChart({ data }: { data: CriterionData[] }) {
  return (
    <ChartContainer
      config={chartConfig}
      className="mx-auto aspect-square max-h-[350px] w-full [&_.recharts-polar-grid-concentric-polygon]:fill-muted/30 [&_.recharts-polar-grid-concentric-polygon:last-child]:fill-background [&_.recharts-polar-grid_[stroke='#ccc']]:stroke-border"
    >
      <RadarChart accessibilityLayer data={data} cx="50%" cy="50%" outerRadius="70%">
        <PolarGrid gridType="polygon" />
        <PolarAngleAxis
          dataKey="criterion"
          tick={({ x, y, payload, textAnchor }) => (
            <text
              x={x}
              y={y}
              textAnchor={textAnchor}
              dominantBaseline="central"
              className="fill-foreground text-[11px] font-medium"
            >
              {payload.value}
            </text>
          )}
        />
        <ChartTooltip
          cursor={false}
          content={
            <ChartTooltipContent
              hideLabel
              formatter={(value) => (
                <span className="font-medium">{value}% confidence</span>
              )}
            />
          }
        />
        <Radar
          name="score"
          dataKey="score"
          stroke="hsl(var(--chart-1))"
          fill="hsl(var(--chart-1))"
          fillOpacity={0.15}
          strokeWidth={2}
          dot={{
            r: 4,
            fill: "hsl(var(--chart-2))",
            stroke: "hsl(var(--background))",
            strokeWidth: 2,
          }}
          activeDot={{
            r: 6,
            fill: "hsl(var(--chart-2))",
            stroke: "hsl(var(--background))",
            strokeWidth: 2,
          }}
        />
      </RadarChart>
    </ChartContainer>
  );
}
