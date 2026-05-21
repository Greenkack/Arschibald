/**
 * Lazy Image Component
 * 
 * Implements lazy loading for images using Intersection Observer API.
 * Images are only loaded when they enter the viewport.
 */

import React, { useState, useEffect, useRef } from 'react';

export interface LazyImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src: string;
  alt: string;
  placeholder?: string;
  threshold?: number;
  rootMargin?: string;
  onLoad?: () => void;
  onError?: () => void;
}

export const LazyImage: React.FC<LazyImageProps> = ({
  src,
  alt,
  placeholder = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"%3E%3Crect fill="%23f0f0f0" width="400" height="300"/%3E%3C/svg%3E',
  threshold = 0.01,
  rootMargin = '50px',
  onLoad,
  onError,
  className = '',
  style,
  ...props
}) => {
  const [imageSrc, setImageSrc] = useState<string>(placeholder);
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    if (!imgRef.current) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setImageSrc(src);
            observer.disconnect();
          }
        });
      },
      {
        threshold,
        rootMargin,
      }
    );

    observer.observe(imgRef.current);

    return () => {
      observer.disconnect();
    };
  }, [src, threshold, rootMargin]);

  const handleLoad = () => {
    setIsLoaded(true);
    onLoad?.();
  };

  const handleError = () => {
    setHasError(true);
    onError?.();
  };

  return (
    <img
      ref={imgRef}
      src={imageSrc}
      alt={alt}
      className={`lazy-image ${isLoaded ? 'loaded' : ''} ${hasError ? 'error' : ''} ${className}`}
      style={{
        transition: 'opacity 0.3s ease-in-out',
        opacity: isLoaded ? 1 : 0.5,
        ...style,
      }}
      onLoad={handleLoad}
      onError={handleError}
      {...props}
    />
  );
};

/**
 * Lazy Background Image Component
 * 
 * Implements lazy loading for background images.
 */

export interface LazyBackgroundProps {
  src: string;
  placeholder?: string;
  threshold?: number;
  rootMargin?: string;
  children?: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
}

export const LazyBackground: React.FC<LazyBackgroundProps> = ({
  src,
  placeholder,
  threshold = 0.01,
  rootMargin = '50px',
  children,
  className = '',
  style,
}) => {
  const [backgroundImage, setBackgroundImage] = useState<string | undefined>(
    placeholder ? `url(${placeholder})` : undefined
  );
  const [isLoaded, setIsLoaded] = useState(false);
  const divRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!divRef.current) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            // Preload the image
            const img = new Image();
            img.src = src;
            img.onload = () => {
              setBackgroundImage(`url(${src})`);
              setIsLoaded(true);
            };
            observer.disconnect();
          }
        });
      },
      {
        threshold,
        rootMargin,
      }
    );

    observer.observe(divRef.current);

    return () => {
      observer.disconnect();
    };
  }, [src, threshold, rootMargin]);

  return (
    <div
      ref={divRef}
      className={`lazy-background ${isLoaded ? 'loaded' : ''} ${className}`}
      style={{
        backgroundImage,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        transition: 'opacity 0.3s ease-in-out',
        opacity: isLoaded ? 1 : 0.7,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/**
 * Progressive Image Component
 * 
 * Loads a low-quality placeholder first, then the full-quality image.
 */

export interface ProgressiveImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src: string;
  placeholderSrc: string;
  alt: string;
  threshold?: number;
  rootMargin?: string;
}

export const ProgressiveImage: React.FC<ProgressiveImageProps> = ({
  src,
  placeholderSrc,
  alt,
  threshold = 0.01,
  rootMargin = '50px',
  className = '',
  style,
  ...props
}) => {
  const [currentSrc, setCurrentSrc] = useState(placeholderSrc);
  const [isFullQuality, setIsFullQuality] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    if (!imgRef.current) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            // Load full quality image
            const img = new Image();
            img.src = src;
            img.onload = () => {
              setCurrentSrc(src);
              setIsFullQuality(true);
            };
            observer.disconnect();
          }
        });
      },
      {
        threshold,
        rootMargin,
      }
    );

    observer.observe(imgRef.current);

    return () => {
      observer.disconnect();
    };
  }, [src, threshold, rootMargin]);

  return (
    <img
      ref={imgRef}
      src={currentSrc}
      alt={alt}
      className={`progressive-image ${isFullQuality ? 'full-quality' : 'placeholder'} ${className}`}
      style={{
        filter: isFullQuality ? 'none' : 'blur(10px)',
        transition: 'filter 0.3s ease-in-out',
        ...style,
      }}
      {...props}
    />
  );
};
