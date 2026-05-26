import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  retries: 0,
  reporter: [["list"]],

  use: {
    baseURL: "http://127.0.0.1:5173",
    headless: true,
    screenshot: "off",
    video: "off",
    trace: "off",
  },

  projects: [
    {
      name: "ipad-portrait",
      use: { viewport: { width: 768, height: 1024 } },
    },
    {
      name: "ipad-air",
      use: { viewport: { width: 834, height: 1194 } },
    },
    {
      name: "mobile-narrow",
      use: { viewport: { width: 390, height: 844 } },
    },
  ],

  webServer: {
    command: "npm run dev",
    url: "http://127.0.0.1:5173",
    reuseExistingServer: !process.env["CI"],
    timeout: 30_000,
  },
});
