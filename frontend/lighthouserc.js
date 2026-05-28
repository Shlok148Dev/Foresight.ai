module.exports = {
  ci: {
    collect: {
      url: ["http://localhost:3000"],
      numberOfRuns: 1,
    },
    assert: {
      preset: "lighthouse:no-pwa",
      assertions: {
        "categories:performance": ["warn", { minScore: 0.7 }],
        "categories:accessibility": ["warn", { minScore: 0.85 }],
        "categories:best-practices": ["warn", { minScore: 0.85 }],
        "categories:seo": ["warn", { minScore: 0.85 }],
        // Warn-only so the check doesn't block the CI pipeline
        "uses-optimized-images": "off",
        "uses-webp-images": "off",
      },
    },
    upload: {
      target: "temporary-public-storage",
    },
  },
};
