import { BrowserRouter, Routes, Route } from "react-router-dom"
import Footer from "../components/Footer"
import Login from "../pages/Login"
import Home from "../pages/Home"

export function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/home" element={<Home />} />
      </Routes>
      <Footer />
    </BrowserRouter>
  )
}