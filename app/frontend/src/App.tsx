import { BrowserRouter, Navigate, Routes, Route } from "react-router-dom"

import Splash from "./pages/Splash"
import Login from "./pages/Login"
import Register from "./pages/Register"
import Home from "./pages/Home"
import Layout from "./layout/Layout"
import NewAnalysis from "./pages/NewAnalysis"
import AnalyzeConsent from "./pages/AnalyzeConsent"
import AnalyzeResult from "./pages/AnalyzeResult"
import AnalysisOverview from "./pages/AnalysisOverview"
import About from "./pages/About"
import MyData from "./pages/MyData"

import PrivateRoute from "./routes/PrivateRoute"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Splash />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route
          element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }
        >
          <Route path="/home" element={<Home />} />
          <Route path="/analyze/new" element={<NewAnalysis />} />
          <Route path="/analyze/consent" element={<AnalyzeConsent />} />
          <Route path="/analyze/result" element={<AnalyzeResult />} />
          <Route path="/analysis/:id" element={<AnalysisOverview />} />
          <Route path="/about" element={<About />} />
          <Route path="/my-data" element={<MyData />} />
          <Route path="/analyze" element={<Navigate to="/home" replace />} />
          <Route path="/analyze/focus" element={<Navigate to="/home" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
