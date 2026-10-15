import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Für Capacitor-APK-Build: NEXT_EXPORT=1 npm run build
  ...(process.env.NEXT_EXPORT === "1" ? { output: "export" } : {}),

  // API-Proxy zu Port 8030 (Welt-API)
  async rewrites() {
    return [
      // WebSocket muss vor dem allgemeinen /api/-Block stehen
      {
        source: "/api/ws/:path*",
        destination: "http://localhost:8030/ws/:path*",
      },
      {
        source: "/api/:path*",
        destination: "http://localhost:8030/:path*",
      },
      {
        source: "/gordslider/:path*",
        destination: "http://localhost:8787/gordslider/:path*",
      },
    ];
  },

  // Bilder von der eigenen Domain erlauben
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "flextrawurst.de",
      },
      {
        protocol: "https",
        hostname: "pro.flextrawurst.de",
      },
    ],
  },

  // Turbopack-Root explizit setzen (unterdrückt Warnung)
  turbopack: {
    root: "/root/flextrawurst-pro",
  },
};

export default nextConfig;
