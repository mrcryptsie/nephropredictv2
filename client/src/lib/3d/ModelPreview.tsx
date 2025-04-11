import { useRef, useEffect } from "react";

// Simple 3D Model Preview component with hover animation
export default function ModelPreview() {
  const previewRef = useRef<HTMLDivElement>(null);
  const innerRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    const previewEl = previewRef.current;
    const innerEl = innerRef.current;
    
    if (!previewEl || !innerEl) return;
    
    const handleMouseMove = (e: MouseEvent) => {
      const rect = previewEl.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      const xRotation = ((y - rect.height / 2) / rect.height) * 10;
      const yRotation = ((x - rect.width / 2) / rect.width) * -10;
      
      innerEl.style.transform = `perspective(1000px) rotateX(${xRotation}deg) rotateY(${yRotation}deg)`;
    };
    
    const handleMouseLeave = () => {
      innerEl.style.transform = "perspective(1000px) rotateX(0) rotateY(0)";
    };
    
    previewEl.addEventListener("mousemove", handleMouseMove);
    previewEl.addEventListener("mouseleave", handleMouseLeave);
    
    return () => {
      previewEl.removeEventListener("mousemove", handleMouseMove);
      previewEl.removeEventListener("mouseleave", handleMouseLeave);
    };
  }, []);
  
  return (
    <div className="model-preview" ref={previewRef}>
      <div
        ref={innerRef}
        className="model-preview-inner bg-white rounded-2xl p-6 shadow-[0_10px_25px_-5px_rgba(0,0,0,0.05),_0_8px_10px_-6px_rgba(0,0,0,0.02)]"
      >
        <div className="flex justify-between items-center mb-4">
          <div className="font-semibold">Aperçu du modèle IRC</div>
          <div className="flex space-x-1">
            <div className="w-2 h-2 rounded-full bg-accent-400 pulse-dot"></div>
            <div
              className="w-2 h-2 rounded-full bg-primary-400 pulse-dot"
              style={{ animationDelay: "0.5s" }}
            ></div>
            <div
              className="w-2 h-2 rounded-full bg-secondary-400 pulse-dot"
              style={{ animationDelay: "1s" }}
            ></div>
          </div>
        </div>

        <div className="rounded-xl bg-neutral-100 p-4 mb-4">
          <div className="h-40 flex items-center justify-center">
            <svg
              className="w-full h-full text-neutral-300"
              viewBox="0 0 100 50"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M0,25 Q25,0 50,25 T100,25"
                stroke="currentColor"
                strokeWidth="2"
                fill="none"
              />
              <path
                d="M0,35 Q25,10 50,35 T100,35"
                stroke="currentColor"
                strokeWidth="2"
                fill="none"
                opacity="0.5"
              />
              <path
                d="M0,40 Q25,15 50,40 T100,40"
                stroke="currentColor"
                strokeWidth="2"
                fill="none"
                opacity="0.3"
              />
            </svg>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="bg-neutral-100 rounded-lg p-3">
            <div className="text-xs text-neutral-500 mb-1">Précision</div>
            <div className="text-lg font-semibold">85%</div>
          </div>
          <div className="bg-neutral-100 rounded-lg p-3">
            <div className="text-xs text-neutral-500 mb-1">Prédictions</div>
            <div className="text-lg font-semibold">10,842</div>
          </div>
        </div>

        <div className="bg-gradient-to-r from-primary-500 to-secondary-600 text-white rounded-lg p-4">
          <div className="text-sm font-medium mb-2">Version actuelle</div>
          <div className="text-xl font-semibold">model_groupe2_ai.pkl</div>
        </div>
      </div>
    </div>
  );
}
