import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
	server: {
		host: '::',
		port: 8080,
	},
	plugins: [react()],
	resolve: {
		alias: {
			'@': path.resolve(__dirname, './src'),
		},
		extensions: ['.ts', '.tsx', '.js', '.jsx', '.json'],
	},
	build: {
		target: 'esnext',
		rollupOptions: {
			external: [],
		},
		commonjsOptions: {
			include: [/node_modules/],
		},
	},
	optimizeDeps: {
		include: ['clsx', 'tailwind-merge'],
	},
	esbuild: {
		target: 'esnext',
	},
}));
