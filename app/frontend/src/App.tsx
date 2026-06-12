import { BrowserRouter, Routes, Route } from "react-router-dom"

import Login from "./pages/Login"
import Register from "./pages/Register"
import Home from "./pages/Home"
import Layout from "./layout/Layout"
import Analyze from "./pages/Analyze"
import ModelFocus from "./pages/ModelFocus"
import About from "./pages/About"

import PrivateRoute from "./routes/PrivateRoute"
import Footer from "./components/Footer"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route
          element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }
        >
          <Route path="/home" element={<Home />} />
          <Route path="/analyze" element={<Analyze />} />
          <Route path="/analyze/focus" element={<ModelFocus />} />
          <Route path="/about" element={<About />} />
        </Route>
      </Routes>

      <Footer />
    </BrowserRouter>
  )
}