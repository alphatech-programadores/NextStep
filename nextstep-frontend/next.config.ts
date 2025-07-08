/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Any other configurations you might have...

  // This is the crucial part for proxying requests:
  async rewrites() {
    return [
      {
        source: '/api/:path*', // Catches requests starting with /api/
        destination: 'http://127.0.0.1:5000/api/:path*', // Forwards them to your Flask backend
      },
    ];
  },
};

module.exports = nextConfig;