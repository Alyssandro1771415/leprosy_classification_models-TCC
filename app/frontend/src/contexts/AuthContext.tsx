import { FirebaseAuthentication } from "@capacitor-firebase/authentication"
import { Capacitor } from "@capacitor/core"
import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react"
import {
  GoogleAuthProvider,
  type User,
  type UserCredential,
  onAuthStateChanged,
  signInWithCredential,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  signOut,
} from "firebase/auth"
import { auth, googleProvider } from "../services/firebase"

type AuthContextType = {
  user: User | null
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<void>
  loginWithGoogle: () => Promise<UserCredential>
  logout: () => Promise<void>
}

const AuthContext = createContext({} as AuthContextType)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user)
      setLoading(false)
    })

    return unsubscribe
  }, [])

  async function login(email: string, password: string) {
    await signInWithEmailAndPassword(auth, email, password)
  }

  async function register(email: string, password: string) {
    await createUserWithEmailAndPassword(auth, email, password)
  }

  async function loginWithGoogle(): Promise<UserCredential> {
    if (Capacitor.isNativePlatform()) {
      const result = await FirebaseAuthentication.signInWithGoogle()
      const idToken = result.credential?.idToken

      if (!idToken) {
        throw new Error("Token do Google não recebido")
      }

      const credential = GoogleAuthProvider.credential(idToken)
      return signInWithCredential(auth, credential)
    }

    return signInWithPopup(auth, googleProvider)
  }

  async function logout() {
    if (Capacitor.isNativePlatform()) {
      try {
        await FirebaseAuthentication.signOut()
      } catch {
        // Ignora se já estiver deslogado na camada nativa
      }
    }

    await signOut(auth)
  }

  return (
    <AuthContext.Provider
      value={{ user, login, register, loginWithGoogle, logout }}
    >
      {!loading && children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
