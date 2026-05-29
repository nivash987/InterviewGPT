"use client";

import { useCallback, useRef, useState } from "react";
import { FileText, UploadCloud } from "lucide-react";

import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

const ACCEPTED_TYPES = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
];
const MAX_SIZE_MB = 5;

interface ResumeUploadZoneProps {
  onUpload: (file: File, onProgress: (percent: number) => void) => Promise<void>;
  disabled?: boolean;
  label?: string;
}

export function ResumeUploadZone({ onUpload, disabled = false, label }: ResumeUploadZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const validateFile = (file: File): string | null => {
    const ext = file.name.split(".").pop()?.toLowerCase();
    if (ext !== "pdf" && ext !== "docx") {
      return "Only PDF and DOCX files are supported.";
    }
    if (!ACCEPTED_TYPES.includes(file.type) && ext !== "pdf" && ext !== "docx") {
      return "Invalid file type.";
    }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      return `File must be ${MAX_SIZE_MB} MB or smaller.`;
    }
    return null;
  };

  const handleFile = useCallback(
    async (file: File) => {
      setError(null);
      const validationError = validateFile(file);
      if (validationError) {
        setError(validationError);
        return;
      }

      setUploading(true);
      setProgress(0);
      try {
        await onUpload(file, setProgress);
        setProgress(100);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Upload failed");
      } finally {
        setUploading(false);
        if (inputRef.current) {
          inputRef.current.value = "";
        }
      }
    },
    [onUpload],
  );

  const onDrop = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      setIsDragging(false);
      if (disabled || uploading) return;
      const file = event.dataTransfer.files[0];
      if (file) void handleFile(file);
    },
    [disabled, uploading, handleFile],
  );

  return (
    <div className="space-y-3">
      {label && <p className="text-sm font-medium">{label}</p>}
      <div
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
        }}
        onDragOver={(e) => {
          e.preventDefault();
          if (!disabled && !uploading) setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
        onClick={() => !disabled && !uploading && inputRef.current?.click()}
        className={cn(
          "flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed px-6 py-10 transition-colors",
          isDragging ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-primary/50",
          (disabled || uploading) && "pointer-events-none opacity-60",
        )}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          className="hidden"
          disabled={disabled || uploading}
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) void handleFile(file);
          }}
        />
        {uploading ? (
          <UploadCloud className="mb-3 h-10 w-10 text-primary animate-pulse" />
        ) : (
          <FileText className="mb-3 h-10 w-10 text-muted-foreground" />
        )}
        <p className="text-sm font-medium">
          {uploading ? "Uploading…" : "Drag and drop your resume here"}
        </p>
        <p className="mt-1 text-xs text-muted-foreground">
          PDF or DOCX, up to {MAX_SIZE_MB} MB
        </p>
      </div>

      {uploading && (
        <div className="space-y-1">
          <Progress value={progress} />
          <p className="text-xs text-muted-foreground text-right">{progress}%</p>
        </div>
      )}

      {error && <p className="text-sm text-destructive">{error}</p>}
    </div>
  );
}
