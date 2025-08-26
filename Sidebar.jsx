import { 
  LayoutDashboard, 
  Users, 
  UserCheck, 
  BarChart3, 
  Settings, 
  MessageSquare, 
  FileText, 
  Eye,
  Phone,
  LogOut,
  ClipboardList
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

const Sidebar = ({ activeTab, onTabChange }) => {
  const menuItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: 'لوحة التحكم' },
    { id: 'registrations', icon: ClipboardList, label: 'طلبات التسجيل' },
    { id: 'children', icon: Users, label: 'إدارة الأطفال' },
    { id: 'staff', icon: UserCheck, label: 'إدارة الموظفين' },
    { id: 'reports', icon: BarChart3, label: 'التقارير والتحليلات' },
    { id: 'monitoring', icon: Eye, label: 'المراقبة المباشرة' },
    { id: 'messages', icon: MessageSquare, label: 'الرسائل والإشعارات' },
    { id: 'exports', icon: FileText, label: 'تصدير البيانات' },
    { id: 'settings', icon: Settings, label: 'الإعدادات' },
  ];

  return (
    <div className="sidebar w-64 flex flex-col">
      {/* Header */}
      <div className="p-6 border-b">
        <div className="flex items-center space-x-3 space-x-reverse">
          <img 
            src="/src/assets/bright-kids-logo.png" 
            alt="Bright Kids Logo" 
            className="w-10 h-10"
          />
          <div>
            <h1 className="text-lg font-bold text-bright-admin">Bright Kids</h1>
            <p className="text-sm text-muted-foreground">لوحة الإدارة</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <div className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => onTabChange(item.id)}
                className={cn(
                  "sidebar-item w-full flex items-center space-x-3 space-x-reverse text-right",
                  isActive && "active"
                )}
              >
                <Icon size={20} />
                <span className="font-medium">{item.label}</span>
              </button>
            );
          })}
        </div>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t">
        <div className="space-y-3">
          {/* Emergency Contact */}
          <Button 
            variant="outline" 
            className="w-full justify-start space-x-2 space-x-reverse"
            onClick={() => window.open('tel:+966594288121')}
          >
            <Phone size={16} />
            <span>اتصال طوارئ</span>
          </Button>
          
          {/* Admin Info */}
          <div className="flex items-center space-x-3 space-x-reverse p-3 bg-gray-50 rounded-lg">
            <div className="w-8 h-8 rounded-full bg-bright-admin flex items-center justify-center">
              <span className="text-white text-sm font-bold">أ</span>
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium">أحمد المدير</p>
              <p className="text-xs text-muted-foreground">مدير عام</p>
            </div>
          </div>
          
          {/* Logout */}
          <Button 
            variant="ghost" 
            className="w-full justify-start space-x-2 space-x-reverse text-bright-danger hover:text-bright-danger hover:bg-bright-danger/10"
          >
            <LogOut size={16} />
            <span>تسجيل الخروج</span>
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;

