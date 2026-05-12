import { configure } from 'quasar/wrappers'

export default configure(function (/* ctx */) {
  return {
    boot: ['pinia', 'axios'],

    css: ['app.css'],

    extras: ['material-icons'],

    build: {
      target: {
        browser: ['es2019', 'edge88', 'firefox78', 'chrome87', 'safari13.1'],
        node: 'node20'
      },
      vueRouterMode: 'hash',
      typescript: {
        strict: true
      }
    },

    devServer: {
      port: 5173,
      proxy: {
        '/api': {
          target: 'http://localhost:7860',
          changeOrigin: true
        }
      }
    },

    framework: {
      config: { dark: true },
      plugins: ['Dialog', 'Notify']
    },

    animations: [],

    ssr: {
      pwa: false,
      prodPort: 3000,
      middlewares: ['render']
    },

    pwa: {
      workboxMode: 'generateSW',
      injectPwaMetaTags: true,
      swFilename: 'sw.js',
      manifestFilename: 'manifest.json',
      useCredentialsForManifestTag: false
    },

    cordova: {},
    capacitor: {
      hideSplashscreen: true
    },

    electron: {
      preloadScripts: ['electron-preload'],
      inspectPort: 5858,
      bundler: 'packager',
      packager: {}
    },

    bex: {
      contentScripts: ['my-content-script']
    }
  }
})
