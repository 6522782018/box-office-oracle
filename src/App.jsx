import Home from "./pages/Home";
import CustomPredictionPage from "./pages/CustomPredictionPage";
import { getAppPath } from "./appPaths";

export default function App() {
  const path = getAppPath();

  if (path === "/custom-prediction") {
    return <CustomPredictionPage />;
  }

  return <Home />;
}