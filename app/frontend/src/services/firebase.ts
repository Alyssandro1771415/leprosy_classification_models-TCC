import { Capacitor } from "@capacitor/core"
import { initializeApp } from "firebase/app"
import {
  getAuth,
  GoogleAuthProvider,
  initializeAuth,
  indexedDBLocalPersistence,
} from "firebase/auth"

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
}

const app = initializeApp(firebaseConfig)

function createAuth() {
  if (Capacitor.isNativePlatform()) {
    return initializeAuth(app, {
      persistence: indexedDBLocalPersistence,
    })
  }

  return getAuth(app)
}

export const auth = createAuth()
export const googleProvider = new GoogleAuthProvider()
