import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export interface BreadcrumbItem {
  label: string;
  path: string;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
}

export default function Breadcrumbs({ items }: BreadcrumbsProps) {
  const { i18n } = useTranslation();
  const isRTL = ['he', 'ar'].includes(i18n.language);

  if (items.length === 0) return null;

  return (
    <nav className="flex items-center space-x-2 text-sm text-gray-600 mb-4" aria-label="Breadcrumb">
      <ol className={`flex items-center ${isRTL ? 'flex-row-reverse space-x-reverse' : 'space-x-2'}`}>
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          
          return (
            <li key={item.path} className="flex items-center">
              {index > 0 && (
                <span className={`mx-2 text-gray-400 ${isRTL ? 'rotate-180' : ''}`}>
                  ›
                </span>
              )}
              {isLast ? (
                <span className="text-gray-900 font-medium" aria-current="page">
                  {item.label}
                </span>
              ) : (
                <Link
                  to={item.path}
                  className="text-teal-600 hover:text-teal-700 hover:underline transition-colors"
                >
                  {item.label}
                </Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

