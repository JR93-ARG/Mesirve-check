import PantallaAnalisis from "./PantallaAnalisis";
import AdminPanel from "./AdminPanel";
import FondoAnimado from "./components/FondoAnimado";

export default function App() {
  const esAdmin = window.location.pathname.startsWith("/admin");
  return (
    <>
      <FondoAnimado />
      {esAdmin ? <AdminPanel /> : <PantallaAnalisis />}
    </>
  );
}
