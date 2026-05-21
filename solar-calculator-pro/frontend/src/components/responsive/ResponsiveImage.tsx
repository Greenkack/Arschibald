import React from 'react';
import '../../styles/responsive.css';

interface ResponsiveImageProps {
  src: string;
  alt: string;
  className?: string;
  fit?: 'cover' | 'contain' | 'auto';
  loading?: 'lazy' | 'eager';
  srcSet?: string;
  sizes?: string;
}

/**
 * Responsive image component
 * Automatically scales and optimizes images for different screen sizes
 */
export const ResponsiveImage: React.FC<ResponsiveImageProps> = ({
  src,
  alt,
  className = '',
  fit = 'auto',
  loading = 'lazy',
  srcSet,
  sizes,
}) => {
  const imageClass = [
    fit === 'cover' && 'responsive-image-cover',
    fit === 'contain' && 'responsive-image-contain',
    fit === 'auto' && 'responsive-image',
    className,
  ].filter(Boolean).join(' ');

  return (
    <img
      src={src}
      alt={alt}
      className={imageClass}
      loading={loading}
      srcSet={srcSet}
      sizes={sizes}
    />
  );
};
