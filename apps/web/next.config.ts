import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: "export",
  images: { unoptimized: true },
  trailingSlash: true,
  // Avoid picking C:\Users\Wu\package-lock.json as monorepo root
  outputFileTracingRoot: path.join(__dirname),
};

export default nextConfig;
