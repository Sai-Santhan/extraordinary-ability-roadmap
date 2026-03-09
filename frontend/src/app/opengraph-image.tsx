import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "Immigration Roadmap — AI-Powered Immigration Planning";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "60px 70px",
          background: "linear-gradient(135deg, #0f0a1e 0%, #1a1333 40%, #0f172a 100%)",
          fontFamily: "Inter, system-ui, sans-serif",
        }}
      >
        {/* Top: URL bar */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "10px",
            color: "#94a3b8",
            fontSize: 18,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              width: 36,
              height: 36,
              borderRadius: 8,
              background: "linear-gradient(135deg, #7c3aed, #4f46e5)",
            }}
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 32 32"
              fill="none"
            >
              <path
                d="M16 4 L18.5 13.5 L28 16 L18.5 18.5 L16 28 L13.5 18.5 L4 16 L13.5 13.5 Z"
                fill="white"
              />
            </svg>
          </div>
          <span>immigration-roadmap.com</span>
        </div>

        {/* Middle: Title + subtitle */}
        <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          <h1
            style={{
              fontSize: 64,
              fontWeight: 700,
              color: "#ffffff",
              lineHeight: 1.1,
              margin: 0,
              letterSpacing: "-0.02em",
            }}
          >
            Immigration Roadmap
          </h1>
          <div
            style={{
              width: 80,
              height: 4,
              borderRadius: 2,
              background: "linear-gradient(90deg, #7c3aed, #4f46e5)",
            }}
          />
          <p
            style={{
              fontSize: 24,
              color: "#c4b5fd",
              margin: 0,
              lineHeight: 1.5,
              maxWidth: 600,
            }}
          >
            AI-powered planning for EB-1A, EB-1B, EB-1C, NIW, and O-1
            <br />
            immigration pathways.
          </p>
        </div>

        {/* Bottom: badges */}
        <div style={{ display: "flex", gap: "12px" }}>
          {["EB-1A", "EB-1B", "EB-1C", "NIW", "O-1"].map((label) => (
            <div
              key={label}
              style={{
                padding: "6px 16px",
                borderRadius: 999,
                border: "1px solid rgba(124, 58, 237, 0.4)",
                background: "rgba(124, 58, 237, 0.1)",
                color: "#c4b5fd",
                fontSize: 16,
                fontWeight: 500,
              }}
            >
              {label}
            </div>
          ))}
        </div>
      </div>
    ),
    { ...size }
  );
}
