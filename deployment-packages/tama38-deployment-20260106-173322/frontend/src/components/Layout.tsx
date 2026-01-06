import { ReactNode, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import Sidebar from './Sidebar';
import Header from './Header';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const { i18n } = useTranslation();
  const isRTL = ['he', 'ar'].includes(i18n.language);
  const layoutRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (layoutRef.current) {
      // Force apply flex-direction with !important via setProperty
      if (isRTL) {
        layoutRef.current.style.setProperty('flex-direction', 'row-reverse', 'important');
      } else {
        layoutRef.current.style.setProperty('flex-direction', 'row', 'important');
      }
    }
  }, [isRTL]);

  return (
    <div 
      ref={layoutRef}
      className={`flex h-screen bg-gray-50 ${isRTL ? 'rtl-layout' : ''}`}
      data-rtl={isRTL ? 'true' : 'false'}
      style={isRTL ? { flexDirection: 'row-reverse' } : { flexDirection: 'row' }}
    >
      <div style={isRTL ? { order: 2 } : { order: 1 }}>
        <Sidebar />
      </div>
      <div className="flex-1 flex flex-col overflow-hidden" style={isRTL ? { order: 1 } : { order: 2 }}>
        <Header />
        <main className={`flex-1 overflow-y-auto p-6 ${isRTL ? 'text-right' : ''}`}>
          {children}
        </main>
      </div>
    </div>
  );
}

