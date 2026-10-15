import type { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "de.flextrawurst.pro",
  appName: "Flextrawurst Pro",
  webDir: "out",
  // Wenn die App auf dem Gerät läuft, verbindet sie sich mit dem Live-Server
  // Für Produktion: server.url auf https://pro.flextrawurst.de setzen
  server: {
    url: "https://pro.flextrawurst.de",
    cleartext: false,
    androidScheme: "https",
  },
  android: {
    buildOptions: {
      keystorePath: undefined,
      keystoreAlias: undefined,
    },
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: "#050810",
      showSpinner: false,
    },
    StatusBar: {
      style: "DARK",
      backgroundColor: "#050810",
    },
  },
};

export default config;
