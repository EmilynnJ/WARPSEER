import adapter from '@sveltejs/adapter-vercel';

const config = {
  kit: {
    adapter: adapter({
      out: 'build',
      precompress: false,
      envPrefix: '',
    }),
    alias: {
      $lib: 'src/lib'
    }
  }
};

export default config;
