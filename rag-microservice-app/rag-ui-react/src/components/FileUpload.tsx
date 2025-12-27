import { useState, useCallback } from "react";
import { Upload, FileText, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface FileUploadProps {
  onUploadSuccess?: (chunks: number) => void;
}

type UploadStatus = "idle" | "uploading" | "success" | "error";

export function FileUpload({ onUploadSuccess }: FileUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<UploadStatus>("idle");
  const [statusMessage, setStatusMessage] = useState("");
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile?.type === "application/pdf") {
      setFile(droppedFile);
      setStatus("idle");
      setStatusMessage("");
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setStatus("idle");
      setStatusMessage("");
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setStatus("uploading");
    setStatusMessage("Indexing document...");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("/api/ingest", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Upload failed");

      const data = await response.json();
      setStatus("success");
      setStatusMessage(`Document indexed successfully. Chunks created: ${data.chunks}`);
      onUploadSuccess?.(data.chunks);
    } catch {
      setStatus("error");
      setStatusMessage("Error indexing document. Please try again.");
    }
  };

  return (
    <div className="space-y-4">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={cn(
          "relative border-2 border-dashed rounded-xl p-8 transition-all duration-300 cursor-pointer",
          "hover:border-primary/50 hover:bg-primary/5",
          isDragging && "border-primary bg-primary/10 scale-[1.02]",
          file ? "border-success/50 bg-success/5" : "border-border"
        )}
      >
        <input
          type="file"
          accept="application/pdf"
          onChange={handleFileChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        
        <div className="flex flex-col items-center text-center space-y-3">
          {file ? (
            <>
              <div className="p-3 rounded-xl bg-success/10">
                <FileText className="w-8 h-8 text-success" />
              </div>
              <div>
                <p className="font-medium text-foreground">{file.name}</p>
                <p className="text-sm text-muted-foreground">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </>
          ) : (
            <>
              <div className="p-3 rounded-xl bg-primary/10">
                <Upload className="w-8 h-8 text-primary" />
              </div>
              <div>
                <p className="font-medium text-foreground">Drop your PDF here</p>
                <p className="text-sm text-muted-foreground">
                  or click to browse files
                </p>
              </div>
            </>
          )}
        </div>
      </div>

      {file && (
        <Button
          onClick={handleUpload}
          disabled={status === "uploading"}
          variant="gradient"
          className="w-full"
          size="lg"
        >
          {status === "uploading" ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Indexing...
            </>
          ) : (
            <>
              <Upload className="w-5 h-5" />
              Upload & Index
            </>
          )}
        </Button>
      )}

      {statusMessage && (
        <div
          className={cn(
            "flex items-center gap-2 p-3 rounded-lg text-sm animate-fade-in",
            status === "success" && "bg-success/10 text-success",
            status === "error" && "bg-destructive/10 text-destructive",
            status === "uploading" && "bg-primary/10 text-primary"
          )}
        >
          {status === "success" && <CheckCircle2 className="w-4 h-4" />}
          {status === "error" && <AlertCircle className="w-4 h-4" />}
          {status === "uploading" && <Loader2 className="w-4 h-4 animate-spin" />}
          {statusMessage}
        </div>
      )}
    </div>
  );
}
