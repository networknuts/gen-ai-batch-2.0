import { FileText, Zap, Database } from "lucide-react";
import { FileUpload } from "@/components/FileUpload";
import { QuerySection } from "@/components/QuerySection";
import { GlassCard } from "@/components/GlassCard";

const Index = () => {
  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_hsl(217_91%_60%_/_0.1)_0%,_transparent_50%)]" />
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/5 rounded-full blur-3xl" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-accent/5 rounded-full blur-3xl" />
      
      {/* Grid pattern overlay */}
      <div 
        className="absolute inset-0 opacity-[0.02]"
        style={{
          backgroundImage: `linear-gradient(hsl(var(--foreground)) 1px, transparent 1px),
                           linear-gradient(90deg, hsl(var(--foreground)) 1px, transparent 1px)`,
          backgroundSize: '60px 60px'
        }}
      />

      <div className="relative max-w-4xl mx-auto px-6 py-12 md:py-20">
        {/* Header */}
        <header className="text-center mb-12 md:mb-16 animate-fade-in">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-6">
            <Zap className="w-4 h-4 text-primary" />
            <span className="text-sm font-medium text-primary">RAG-Powered Intelligence</span>
          </div>
          
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-4">
            <span className="text-foreground">Document </span>
            <span className="gradient-text">Intelligence</span>
          </h1>
          
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Upload your PDF documents and ask questions. Our AI-powered RAG system 
            will provide accurate, contextual answers in seconds.
          </p>
        </header>

        {/* Feature badges */}
        <div className="flex flex-wrap justify-center gap-4 mb-12 animate-slide-up" style={{ animationDelay: '0.1s' }}>
          {[
            { icon: FileText, label: "PDF Support" },
            { icon: Database, label: "Vector Search" },
            { icon: Zap, label: "Fast Retrieval" },
          ].map(({ icon: Icon, label }) => (
            <div
              key={label}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-secondary/50 border border-border/50"
            >
              <Icon className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">{label}</span>
            </div>
          ))}
        </div>

        {/* Main content */}
        <div className="space-y-6">
          <div className="animate-slide-up" style={{ animationDelay: '0.2s' }}>
            <GlassCard title="Upload Document" step={1}>
              <FileUpload />
            </GlassCard>
          </div>

          <div className="animate-slide-up" style={{ animationDelay: '0.3s' }}>
            <GlassCard title="Ask a Question" step={2}>
              <QuerySection />
            </GlassCard>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-16 text-center animate-fade-in" style={{ animationDelay: '0.4s' }}>
          <p className="text-sm text-muted-foreground">
            RAG Microservices • Powered by Vector Search & AI
          </p>
        </footer>
      </div>
    </div>
  );
};

export default Index;
