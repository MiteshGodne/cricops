// App.jsx
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import AppRoutes from './routes/AppRoutes';
import { Toaster } from 'react-hot-toast';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Navbar />
        <Toaster position="top-right" />
        <main className="max-w-6xl mx-auto p-4">
          <AppRoutes />
        </main>
      </AuthProvider>
    </BrowserRouter>
  );
}
