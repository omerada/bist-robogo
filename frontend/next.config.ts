import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Strict mode
  reactStrictMode: true,

  // Docker standalone output
  output: "standalone",

  // Image optimization
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**.bist-robogo.com",
      },
    ],
  },

  // Environment variables (client-side erişim)
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000",
  },

  // Experimental features
  experimental: {
    optimizePackageImports: [
      "lucide-react",
      "recharts",
      "@tremor/react",
      "date-fns",
    ],
  },

  // Headers
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
    ];
  },
};

export default nextConfig;
