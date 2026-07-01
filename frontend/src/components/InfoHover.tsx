import { Info } from "lucide-react";
import { HoverCard, HoverCardTrigger, HoverCardContent } from "@/components/ui/hover-card";

export function InfoHover({ text }: { text: string }) {
  return (
    <HoverCard openDelay={100}>
      <HoverCardTrigger asChild>
        <span className="cursor-help text-muted-foreground">
          <Info size={16} />
        </span>
      </HoverCardTrigger>
      <HoverCardContent>
        <span dangerouslySetInnerHTML={{ __html: text }} />
      </HoverCardContent>
    </HoverCard>
  );
}
