import { useState } from "react";
import { Send, Sparkles, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

export function QuerySection() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleAsk = async () => {
    if (!question.trim()) return;

    setIsLoading(true);
    setAnswer("");

    try {
      const response = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question.trim() }),
      });

      if (!response.ok) throw new Error("Query failed");

      const data = await response.json();
      setAnswer(data.answer);
    } catch {
      setAnswer("Error retrieving answer. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  };

  return (
    <div className="space-y-4">
      <div className="relative">
        <Textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask something about your uploaded document..."
          className="min-h-[120px] resize-none pr-14 bg-secondary/50 border-border focus:border-primary/50 focus:ring-primary/20 transition-all duration-300"
        />
        <Button
          onClick={handleAsk}
          disabled={!question.trim() || isLoading}
          size="icon"
          variant="gradient"
          className="absolute bottom-3 right-3"
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Send className="w-4 h-4" />
          )}
        </Button>
      </div>

      {(answer || isLoading) && (
        <div
          className={cn(
            "relative rounded-xl p-5 animate-slide-up overflow-hidden",
            "bg-gradient-to-br from-secondary/80 to-secondary/40",
            "border border-border"
          )}
        >
          {/* Decorative glow */}
          <div className="absolute -top-20 -right-20 w-40 h-40 bg-primary/10 rounded-full blur-3xl" />
          
          <div className="relative">
            <div className="flex items-center gap-2 mb-3 text-primary">
              <Sparkles className="w-4 h-4" />
              <span className="text-sm font-medium">AI Response</span>
            </div>
            
            {isLoading ? (
              <div className="space-y-2">
                <div className="h-4 w-3/4 rounded animate-shimmer" />
                <div className="h-4 w-1/2 rounded animate-shimmer" />
                <div className="h-4 w-5/6 rounded animate-shimmer" />
              </div>
            ) : (
              <p className="text-foreground whitespace-pre-wrap leading-relaxed">
                {answer}
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
