module.exports = {
    reactStrictMode: true,
    trailingSlash: true,
    output: 'export',
    exportPathMap: async function (
      defaultPathMap,
      { dev, dir, outDir, distDir, buildId }
    ) {
      return {
        '/': { page: '/' },
        '/tasks': { page: '/tasks' },
        '/email': { page: '/email' },
        '/calendar': { page: '/calendar' },
        '/nlp': { page: '/nlp' },
      }
    },
  }
