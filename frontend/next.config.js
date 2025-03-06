/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // API プロキシ設定
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NODE_ENV === 'development' 
          ? 'http://localhost:8000/api/:path*' // 開発環境
          : '/api/:path*' // 本番環境（Vercel）
      },
    ];
  },
  images: {
    domains: ['rwtnxdkuzhglmbnwoxvs.supabase.co'],
  },
};

module.exports = nextConfig;
