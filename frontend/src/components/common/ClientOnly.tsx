import { useEffect, useState, ReactNode } from 'react';

interface ClientOnlyProps {
  children: ReactNode;
  fallback?: ReactNode;
}

/**
 * ClientOnly component ensures that children are only rendered on the client side.
 * This helps prevent hydration errors when components use browser-specific APIs.
 */
export default function ClientOnly({ children, fallback = null }: ClientOnlyProps) {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  return isClient ? <>{children}</> : <>{fallback}</>;
}
