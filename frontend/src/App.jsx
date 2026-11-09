import { BrowserRouter, Route, Routes } from "react-router-dom";
import SearchPage from "./components/SearchPage";
import SiteDetail from "./components/SiteDetail";

function App() {
  return (
    <BrowserRouter>
      <header className="app-header">★ Stargazing Planner</header>
      <Routes>
        {/* The search page stays on screen; site details open on top of it at /sites/12 */}
        <Route path="/" element={<SearchPage />}>
          <Route path="sites/:siteId" element={<SiteDetail />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
