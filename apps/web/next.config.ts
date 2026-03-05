import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Turbopack root is causing module resolution issues
  // Reverting to default behavior
};

export default nextConfig;
