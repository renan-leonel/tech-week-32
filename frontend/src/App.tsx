import { Toaster } from '@/components/ui/toaster';
import { Toaster as Sonner } from '@/components/ui/sonner';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Index from './pages/Index';
import NotFound from './pages/NotFound';
import PdfViewer from './pages/PdfViewer';
import DiagnosisPage from './pages/DiagnosisPage';

const queryClient = new QueryClient();

const App = () => (
	<QueryClientProvider client={queryClient}>
		<Toaster />
		<Sonner />
		<BrowserRouter>
			<Routes>
				<Route path='/' element={<Index />} />
				<Route path='/pdf' element={<PdfViewer />} />
				<Route
					path='/diagnosis/:sensorId'
					element={<DiagnosisPage />}
				/>
				<Route path='*' element={<NotFound />} />
			</Routes>
		</BrowserRouter>
	</QueryClientProvider>
);

export default App;
