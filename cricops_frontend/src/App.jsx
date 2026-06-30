// App.jsx
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import AppRoutes from './routes/AppRoutes';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Navbar />
        <main className="max-w-6xl mx-auto p-4">
          <AppRoutes />
        </main>
      </AuthProvider>
    </BrowserRouter>
  );
}
