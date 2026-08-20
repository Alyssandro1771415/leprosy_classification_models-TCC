/// <reference types="@capacitor-firebase/authentication" />

import type { CapacitorConfig } from "@capacitor/cli"

const config: CapacitorConfig = {
  appId: "com.alyssandro.leprosyidentifier",
  appName: "leprosy-identifier",
  webDir: "dist",
  server: {
    // http evita Mixed Content ao chamar a API local (http://IP:5000) no WebView
    androidScheme: "http",
    cleartext: true,
  },
  android: {
    adjustMarginsForEdgeToEdge: "force",
  },
  plugins: {
    FirebaseAuthentication: {
      skipNativeAuth: false,
      providers: ["google.com"],
      authDomain: "leprosy-classifier.firebaseapp.com",
    },
  },
}

export default config
