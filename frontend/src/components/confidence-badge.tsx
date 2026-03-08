import { Badge } from "@/components/ui/badge";

export function ConfidenceBadge({ confidence }: { confidence: number }) {
  const variant = confidence > 70 ? "default" : confidence > 40 ? "secondary" : "destructive";
  return <Badge variant={variant}>{confidence}% confident</Badge>;
}
