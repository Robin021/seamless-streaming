import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
// import {resolve} from 'path';

// const rootDir = resolve(__dirname, 'src');
// const assetsDir = resolve(rootDir, 'assets');
// const typesDir = resolve(__dirname, 'types');

// https://vitejs.dev/config/
export default defineConfig(({command}) => {
  let define = {};
  return {
    plugins: [react()],
    define: define,
  };
});
