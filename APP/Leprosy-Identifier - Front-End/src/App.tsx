import { BrowserRouter, Routes, Route } from "react-router-dom"

import Login from "./pages/Login"
import Home from "./pages/Home"
import Layout from "./layout/Layout"
import Analyze from "./pages/Analyze"
import About from "./pages/About"

import Footer from "./components/Footer"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />

        <Route element={<Layout />}>
          <Route path="/home" element={<Home />} />

          <Route path="/analyze" element={<Analyze/>}></Route>

          <Route path="/about" element={<About/>}></Route>
        </Route>
      </Routes>
      <Footer />
    </BrowserRouter>
  )
}