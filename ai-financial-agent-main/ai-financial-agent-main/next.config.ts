import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  /* config options here */
  experimental: {
    ppr: true,
  },
  transpilePackages: [
    'react-markdown',
    'remark-gfm',
    'micromark',
    'mdast-util-from-markdown',
    'micromark-util-decode-string',
    'micromark-util-decode-numeric-character-reference',
    'micromark-util-symbol',
    'mdast-util-to-string',
  ],
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
};

export default nextConfig;
