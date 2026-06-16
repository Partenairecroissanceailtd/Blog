import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://www.partenairecroissance.com',
  trailingSlash: 'always',
  integrations: [sitemap()],
  build: {
    format: 'directory'
  }
});
