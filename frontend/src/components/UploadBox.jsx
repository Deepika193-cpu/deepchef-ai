import { useRef, useState } from 'react';
import Button from './Button';

const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
// 3MB raw ≈ 4MB once base64-encoded — matches Groq's documented limit for
// base64 image payloads (see backend/app/services/vision_recognition.py).
const MAX_SIZE_MB = 3;

export default function UploadBox({ onFileSelected }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [preview, setPreview] = useState(null);
  const [error, setError] = useState(null);

  function validate(file) {
    if (!ACCEPTED_TYPES.includes(file.type)) {
      return 'Please upload a JPG, PNG, or WEBP image.';
    }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      return `Image must be under ${MAX_SIZE_MB}MB.`;
    }
    return null;
  }

  function handleFile(file) {
    const err = validate(file);
    if (err) {
      setError(err);
      return;
    }
    setError(null);
    setPreview(URL.createObjectURL(file));
    onFileSelected(file);
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  }

  function removeImage() {
    setPreview(null);
    setError(null);
    onFileSelected(null);
  }

  return (
    <div>
      {!preview ? (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          className={`cursor-pointer rounded-card border-2 border-dashed p-10 text-center transition-colors ${
            dragging ? 'border-primary bg-primary-light' : 'border-slate-200 bg-secondary hover:border-primary/40'
          }`}
        >
          <p className="font-medium text-ink-900 mb-1">Drag and drop a food photo</p>
          <p className="text-sm text-ink-600 mb-4">or click to browse · JPG, PNG, WEBP up to {MAX_SIZE_MB}MB</p>
          <Button variant="primary" size="sm">
            Browse files
          </Button>
          <input
            ref={inputRef}
            type="file"
            accept={ACCEPTED_TYPES.join(',')}
            className="hidden"
            onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
          />
        </div>
      ) : (
        <div className="relative rounded-card overflow-hidden border border-slate-100">
          <img src={preview} alt="Uploaded food" className="w-full h-64 object-cover" />
          <button
            onClick={removeImage}
            className="absolute top-3 right-3 h-8 w-8 rounded-full bg-white/90 shadow-soft flex items-center justify-center text-ink-600 hover:text-danger"
            aria-label="Remove image"
          >
            ✕
          </button>
        </div>
      )}
      {error && <p className="text-sm text-danger mt-2">{error}</p>}
    </div>
  );
}