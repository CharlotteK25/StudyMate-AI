import { useState, useRef, useCallback } from "react";
import {
  Upload,
  FileText,
  File,
  Sparkles,
  CheckCircle2,
  X,
  Loader2,
  Download,
  Trash2,
  Eye,
} from "lucide-react";

interface UploadedFile {
  id: string;
  name: string;
  format: "PDF" | "DOCX" | "TXT" | "PPTX";
  size: string;
  date: string;
  status: "ready" | "processing" | "done";
}

const MOCK_FILES: UploadedFile[] = [
  { id: "1", name: "Biology_Lecture_3", format: "PDF", size: "2.4 MB", date: "Jun 5, 2026", status: "ready" },
  { id: "2", name: "Calc_Notes_Week7", format: "DOCX", size: "1.1 MB", date: "Jun 4, 2026", status: "done" },
  { id: "3", name: "Chemistry_Formulas", format: "PDF", size: "3.8 MB", date: "Jun 3, 2026", status: "ready" },
  { id: "4", name: "History_Essay_Draft", format: "DOCX", size: "890 KB", date: "Jun 2, 2026", status: "done" },
  { id: "5", name: "Physics_Lab_Report", format: "PDF", size: "5.2 MB", date: "Jun 1, 2026", status: "ready" },
];

const FORMAT_STYLES: Record<string, { bg: string; text: string }> = {
  PDF:  { bg: "#fef2f2", text: "#dc2626" },
  DOCX: { bg: "#eff6ff", text: "#2563eb" },
  TXT:  { bg: "#f0fdf4", text: "#16a34a" },
  PPTX: { bg: "#fff7ed", text: "#ea580c" },
};

function FormatBadge({ format }: { format: string }) {
  const s = FORMAT_STYLES[format] ?? { bg: "#f3f4f6", text: "#374151" };
  return (
    <span
      className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-semibold tracking-wide"
      style={{ backgroundColor: s.bg, color: s.text }}
    >
      {format}
    </span>
  );
}

function FileIcon({ format }: { format: string }) {
  const s = FORMAT_STYLES[format] ?? { bg: "#f3f4f6", text: "#374151" };
  return (
    <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: s.bg }}>
      <FileText size={15} style={{ color: s.text }} />
    </div>
  );
}

export function UploadNotes() {
  const [isDragging, setIsDragging] = useState(false);
  const [files, setFiles] = useState<UploadedFile[]>(MOCK_FILES);
  const [processingIds, setProcessingIds] = useState<Set<string>>(new Set());
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    if (!e.currentTarget.contains(e.relatedTarget as Node)) {
      setIsDragging(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const dropped = Array.from(e.dataTransfer.files);
    addFiles(dropped);
  }, []);

  const addFiles = (rawFiles: File[]) => {
    const newEntries: UploadedFile[] = rawFiles.map((f) => {
      const ext = f.name.split(".").pop()?.toUpperCase() ?? "TXT";
      const format = (["PDF", "DOCX", "TXT", "PPTX"].includes(ext) ? ext : "TXT") as UploadedFile["format"];
      const kb = f.size / 1024;
      const size = kb >= 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${kb.toFixed(0)} KB`;
      return {
        id: crypto.randomUUID(),
        name: f.name.replace(/\.[^/.]+$/, ""),
        format,
        size,
        date: "Jun 5, 2026",
        status: "ready",
      };
    });
    setFiles((prev) => [...newEntries, ...prev]);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) addFiles(Array.from(e.target.files));
  };

  const generateSummary = (id: string) => {
    setProcessingIds((prev) => new Set(prev).add(id));
    setTimeout(() => {
      setFiles((prev) => prev.map((f) => f.id === id ? { ...f, status: "done" } : f));
      setProcessingIds((prev) => { const s = new Set(prev); s.delete(id); return s; });
    }, 2000);
  };

  const removeFile = (id: string) => setFiles((prev) => prev.filter((f) => f.id !== id));

  return (
    <div className="flex flex-col gap-6">
      {/* Page header */}
      <div>
        <h1 className="text-gray-900">Upload Notes</h1>
        <p className="text-sm text-gray-400 mt-0.5">Upload your study files and generate AI-powered summaries instantly</p>
      </div>

      {/* Drop zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`relative rounded-2xl border-2 border-dashed cursor-pointer transition-all duration-200 select-none
          ${isDragging
            ? "border-[#4ade80] bg-[#f0fdf4] scale-[1.01] shadow-lg shadow-[#4ade8020]"
            : "border-gray-200 bg-white hover:border-[#86efac] hover:bg-[#f0fdf4]/50"
          }`}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.txt,.pptx"
          className="hidden"
          onChange={handleInputChange}
        />
        <div className="flex flex-col items-center justify-center gap-4 py-14 px-6">
          <div className={`w-16 h-16 rounded-2xl flex items-center justify-center transition-all duration-200
            ${isDragging ? "bg-[#4ade80] scale-110" : "bg-[#f0fdf4]"}`}>
            <Upload size={28} className={isDragging ? "text-white" : "text-[#4ade80]"} />
          </div>
          <div className="text-center">
            <p className={`font-medium transition-colors ${isDragging ? "text-[#16a34a]" : "text-gray-700"}`}>
              {isDragging ? "Drop files to upload" : "Drag-and-drop or select your notes"}
            </p>
            <p className="text-sm text-gray-400 mt-1">
              Supports PDF, DOCX, TXT, PPTX · Max 50 MB per file
            </p>
          </div>
          <button
            type="button"
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all duration-150
              ${isDragging
                ? "bg-[#4ade80] text-white shadow-md"
                : "bg-[#f0fdf4] text-[#16a34a] border border-[#86efac] hover:bg-[#dcfce7] hover:shadow-sm"
              }`}
            onClick={(e) => { e.stopPropagation(); inputRef.current?.click(); }}
          >
            <Upload size={15} />
            Upload File
          </button>
        </div>

        {isDragging && (
          <div className="absolute inset-0 rounded-2xl border-2 border-[#4ade80] pointer-events-none animate-pulse" />
        )}
      </div>

      {/* Recent Uploads table */}
      <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.07)] shadow-sm overflow-hidden">
        <div className="flex items-center justify-between px-5 py-4 border-b border-[rgba(0,0,0,0.06)]">
          <div>
            <h3 className="text-gray-900">Recent Uploads</h3>
            <p className="text-xs text-gray-400 mt-0.5">{files.length} file{files.length !== 1 ? "s" : ""}</p>
          </div>
          <span className="text-xs bg-[#f0fdf4] text-[#16a34a] px-2.5 py-1 rounded-lg font-medium">
            {files.filter((f) => f.status === "done").length} summarised
          </span>
        </div>

        {/* Table header */}
        <div className="hidden sm:grid grid-cols-[auto_1fr_100px_130px_160px_40px] gap-4 px-5 py-2.5 bg-[#f8fafc] border-b border-[rgba(0,0,0,0.05)]">
          {["", "File Name", "Format", "Uploaded", "Action", ""].map((h, i) => (
            <span key={i} className="text-xs font-medium text-gray-400 uppercase tracking-wide">{h}</span>
          ))}
        </div>

        {/* Rows */}
        <div className="divide-y divide-[rgba(0,0,0,0.04)]">
          {files.map((f) => {
            const isProcessing = processingIds.has(f.id);
            return (
              <div
                key={f.id}
                className="flex flex-col sm:grid sm:grid-cols-[auto_1fr_100px_130px_160px_40px] gap-3 sm:gap-4 items-start sm:items-center px-5 py-3.5 hover:bg-[#fafafa] transition-colors group"
              >
                {/* Icon */}
                <FileIcon format={f.format} />

                {/* Name + size */}
                <div className="min-w-0">
                  <p className="text-sm text-gray-800 truncate">{f.name}</p>
                  <p className="text-xs text-gray-400">{f.size}</p>
                </div>

                {/* Badge */}
                <div>
                  <FormatBadge format={f.format} />
                </div>

                {/* Date */}
                <p className="text-xs text-gray-400">{f.date}</p>

                {/* Action */}
                <div>
                  {f.status === "done" ? (
                    <span className="inline-flex items-center gap-1.5 text-xs text-[#16a34a] font-medium bg-[#f0fdf4] px-3 py-1.5 rounded-lg">
                      <CheckCircle2 size={13} />
                      Summary Ready
                    </span>
                  ) : isProcessing ? (
                    <span className="inline-flex items-center gap-1.5 text-xs text-[#9333ea] font-medium bg-[#fdf4ff] px-3 py-1.5 rounded-lg">
                      <Loader2 size={13} className="animate-spin" />
                      Processing…
                    </span>
                  ) : (
                    <button
                      onClick={() => generateSummary(f.id)}
                      className="inline-flex items-center gap-1.5 text-xs font-medium bg-gray-900 text-white px-3 py-1.5 rounded-lg hover:bg-gray-700 active:scale-95 transition-all duration-150 shadow-sm hover:shadow"
                    >
                      <Sparkles size={13} />
                      Generate Summary
                    </button>
                  )}
                </div>

                {/* Row actions (visible on hover) */}
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-all"
                    onClick={() => removeFile(f.id)}
                    aria-label="Delete file"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>
            );
          })}

          {files.length === 0 && (
            <div className="flex flex-col items-center justify-center gap-3 py-14 text-gray-400">
              <File size={32} className="text-gray-200" />
              <p className="text-sm">No files uploaded yet</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
