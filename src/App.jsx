import Home from "./pages/Home";
import CustomPredictionPage from "./pages/CustomPredictionPage";

export default function App() {
  const path = window.location.pathname;

  if (path === "/custom-prediction") {
    return <CustomPredictionPage />;
  }

  return <Home />;
}