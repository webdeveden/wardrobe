import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import vuedevtools from "vite-plugin-vue-devtools";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [vue(), vuedevtools(), tailwindcss()],
});
