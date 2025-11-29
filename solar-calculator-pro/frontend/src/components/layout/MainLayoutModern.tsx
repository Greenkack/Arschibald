/**
 * Modern Main Layout with shadcn/ui
 * 
 * Responsive layout with Sheet sidebar, modern header, and breadcrumbs
 */

import React from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import {
  Home,
  Sun,
  Zap,
  Table,
  Package,
  Users,
  FileText,
  Box,
  Settings,
  Shield,
  Menu,
  Moon,
  Bell,
  User,
  LogOut,
  ChevronRight,
  Folder
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger, SheetHeader, SheetTitle } from '@/components/ui/sheet';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { cn } from '@/lib/utils';

interface NavItem {
  title: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
}

interface NavGroup {
  title: string;
  items: NavItem[];
}

const navigationGroups: NavGroup[] = [
  {
    title: 'Main',
    items: [
      { title: 'Dashboard', href: '/dashboard', icon: Home },
    ],
  },
  {
    title: 'Calculators',
    items: [
      { title: 'Solar Calculator', href: '/solar', icon: Sun },
      { title: 'Solar Projects', href: '/solar-projects', icon: Folder },
      { title: 'Heat Pump', href: '/heatpump', icon: Zap },
    ],
  },
  {
    title: 'Business',
    items: [
      { title: 'Price Matrix', href: '/price-matrix', icon: Table },
      { title: 'Products', href: '/products', icon: Package },
      { title: 'CRM', href: '/crm', icon: Users },
    ],
  },
  {
    title: 'Tools',
    items: [
      { title: 'PDF Generator', href: '/pdf', icon: FileText },
      { title: '3D Visualization', href: '/3d-view', icon: Box },
    ],
  },
  {
    title: 'System',
    items: [
      { title: 'Admin Panel', href: '/admin', icon: Shield },
      { title: 'Settings', href: '/settings', icon: Settings },
    ],
  },
];

const SidebarContent: React.FC<{ currentPath: string; onNavigate?: () => void }> = ({
  currentPath,
  onNavigate,
}) => {
  const navigate = useNavigate();

  const handleNavigation = (href: string) => {
    navigate(href);
    onNavigate?.();
  };

  return (
    <div className="flex h-full flex-col">
      {/* Logo/Brand */}
      <div className="p-6">
        <h2 className="text-2xl font-bold text-primary">Solar Calc Pro</h2>
        <p className="text-sm text-muted-foreground">v1.0.0</p>
      </div>

      <Separator />

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4">
        {navigationGroups.map((group, idx) => (
          <div key={group.title} className={cn('mb-6', idx === 0 && 'mt-0')}>
            <h3 className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              {group.title}
            </h3>
            <div className="space-y-1">
              {group.items.map((item) => {
                const Icon = item.icon;
                const isActive =
                  currentPath === item.href ||
                  (item.href !== '/dashboard' && currentPath.startsWith(item.href));

                return (
                  <Button
                    key={item.href}
                    variant={isActive ? 'secondary' : 'ghost'}
                    className={cn(
                      'w-full justify-start',
                      isActive && 'bg-secondary font-semibold'
                    )}
                    onClick={() => handleNavigation(item.href)}
                  >
                    <Icon className="mr-2 h-4 w-4" />
                    {item.title}
                    {item.badge && (
                      <Badge variant="destructive" className="ml-auto">
                        {item.badge}
                      </Badge>
                    )}
                  </Button>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      <Separator />

      {/* Footer */}
      <div className="p-4">
        <div className="rounded-lg bg-muted p-3 text-sm">
          <p className="font-semibold">Tipp des Tages</p>
          <p className="text-muted-foreground">
            Nutze Tastenkombinationen für schnellere Navigation
          </p>
        </div>
      </div>
    </div>
  );
};

const getBreadcrumbs = (pathname: string) => {
  const paths = pathname.split('/').filter(Boolean);
  const breadcrumbs: { label: string; href: string }[] = [
    { label: 'Home', href: '/dashboard' },
  ];

  const routeLabels: Record<string, string> = {
    dashboard: 'Dashboard',
    solar: 'Solar Calculator',
    'solar-projects': 'Solar Projects',
    heatpump: 'Heat Pump',
    'price-matrix': 'Price Matrix',
    products: 'Products',
    crm: 'CRM',
    pdf: 'PDF Generator',
    '3d-view': '3D Visualization',
    admin: 'Admin Panel',
    settings: 'Settings',
  };

  let currentPath = '';
  paths.forEach((path) => {
    currentPath += `/${path}`;
    const label = routeLabels[path] || path.charAt(0).toUpperCase() + path.slice(1);
    breadcrumbs.push({ label, href: currentPath });
  });

  return breadcrumbs;
};

const MainLayoutModern: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = React.useState(false);

  const breadcrumbs = getBreadcrumbs(location.pathname);

  return (
    <div className="flex h-screen bg-background">
      {/* Desktop Sidebar - Hidden on Mobile */}
      <aside className="hidden w-64 border-r bg-card lg:block">
        <SidebarContent currentPath={location.pathname} />
      </aside>

      {/* Main Content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Header */}
        <header className="border-b bg-card">
          <div className="flex h-16 items-center gap-4 px-4">
            {/* Mobile Menu Button */}
            <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="lg:hidden">
                  <Menu className="h-5 w-5" />
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="w-64 p-0">
                <SheetHeader className="sr-only">
                  <SheetTitle>Navigation</SheetTitle>
                </SheetHeader>
                <SidebarContent
                  currentPath={location.pathname}
                  onNavigate={() => setSidebarOpen(false)}
                />
              </SheetContent>
            </Sheet>

            {/* Breadcrumbs */}
            <Breadcrumb className="flex-1">
              <BreadcrumbList>
                {breadcrumbs.map((crumb, idx) => (
                  <React.Fragment key={crumb.href}>
                    {idx > 0 && (
                      <BreadcrumbSeparator>
                        <ChevronRight className="h-4 w-4" />
                      </BreadcrumbSeparator>
                    )}
                    <BreadcrumbItem>
                      {idx === breadcrumbs.length - 1 ? (
                        <BreadcrumbPage>{crumb.label}</BreadcrumbPage>
                      ) : (
                        <BreadcrumbLink
                          onClick={() => navigate(crumb.href)}
                          className="cursor-pointer"
                        >
                          {crumb.label}
                        </BreadcrumbLink>
                      )}
                    </BreadcrumbItem>
                  </React.Fragment>
                ))}
              </BreadcrumbList>
            </Breadcrumb>

            {/* Right Actions */}
            <div className="flex items-center gap-2">
              {/* Theme Toggle */}
              <Button variant="ghost" size="icon">
                <Moon className="h-5 w-5" />
              </Button>

              {/* Notifications */}
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="h-5 w-5" />
                <Badge
                  variant="destructive"
                  className="absolute -right-1 -top-1 h-5 w-5 rounded-full p-0 text-xs"
                >
                  3
                </Badge>
              </Button>

              {/* User Menu */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                    <Avatar>
                      <AvatarImage src="/avatar.png" alt="User" />
                      <AvatarFallback>AD</AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuLabel>
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium">Admin User</p>
                      <p className="text-xs text-muted-foreground">admin@example.com</p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => navigate('/profile')}>
                    <User className="mr-2 h-4 w-4" />
                    Profile
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => navigate('/settings')}>
                    <Settings className="mr-2 h-4 w-4" />
                    Settings
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => navigate('/logout')}>
                    <LogOut className="mr-2 h-4 w-4" />
                    Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto bg-background">
          <div className="container mx-auto p-6">
            <Outlet />
          </div>
        </main>

        {/* Footer */}
        <footer className="border-t bg-card">
          <div className="flex h-12 items-center justify-between px-4 text-sm text-muted-foreground">
            <p>© 2025 Solar Calc Pro - All rights reserved</p>
            <div className="flex gap-4">
              <a href="#" className="hover:text-foreground">
                Docs
              </a>
              <a href="#" className="hover:text-foreground">
                Support
              </a>
              <a href="#" className="hover:text-foreground">
                Privacy
              </a>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default MainLayoutModern;
