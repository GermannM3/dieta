import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "@/hooks/use-toast";
import { Users, Crown, Activity, Database } from "lucide-react";

export const AdminPanel = ({ user }) => {
  const [webUsers, setWebUsers] = useState([]);
  const [telegramUsers, setTelegramUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState({});

  // Проверяем, является ли пользователь администратором
  const isAdmin = user?.email === 'germannm@vk.com';

  useEffect(() => {
    if (isAdmin) {
      loadUsers();
    }
  }, [isAdmin]);

  const loadUsers = async () => {
    setLoading(true);
    try {
      // Загружаем веб-пользователей
      const webResponse = await fetch('/api/admin/web-users', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (webResponse.ok) {
        const webData = await webResponse.json();
        setWebUsers(webData.users || []);
      }

      // Загружаем телеграм-пользователей
      const tgResponse = await fetch('/api/admin/telegram-users', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (tgResponse.ok) {
        const tgData = await tgResponse.json();
        setTelegramUsers(tgData.users || []);
      }
    } catch (error) {
      console.error('Ошибка загрузки пользователей:', error);
      toast({
        title: "Ошибка",
        description: "Не удалось загрузить пользователей",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const togglePremium = async (userId, userType, currentPremium) => {
    setUpdating({ ...updating, [`${userType}-${userId}`]: true });
    
    try {
      const response = await fetch('/api/admin/toggle-premium', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          user_id: userId,
          user_type: userType,
          premium: !currentPremium
        })
      });

      if (response.ok) {
        toast({
          title: "Успешно",
          description: `Премиум ${!currentPremium ? 'активирован' : 'деактивирован'}`,
        });
        
        // Обновляем локальное состояние
        if (userType === 'web') {
          setWebUsers(prev => prev.map(user => 
            user.id === userId ? { ...user, is_premium: !currentPremium } : user
          ));
        } else {
          setTelegramUsers(prev => prev.map(user => 
            user.tg_id === userId ? { ...user, is_premium: !currentPremium } : user
          ));
        }
      } else {
        throw new Error('Ошибка обновления');
      }
    } catch (error) {
      console.error('Ошибка обновления премиума:', error);
      toast({
        title: "Ошибка",
        description: "Не удалось обновить премиум статус",
        variant: "destructive",
      });
    } finally {
      setUpdating({ ...updating, [`${userType}-${userId}`]: false });
    }
  };

  if (!isAdmin) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-red-600">Доступ запрещен</CardTitle>
          <CardDescription>
            У вас нет прав для доступа к админ-панели
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Загрузка админ-панели...</CardTitle>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Crown className="h-5 w-5 text-yellow-500" />
          Админ-панель
        </CardTitle>
        <CardDescription>
          Управление пользователями и премиум-подписками
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="web" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="web" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              Веб-пользователи ({webUsers.length})
            </TabsTrigger>
            <TabsTrigger value="telegram" className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Telegram ({telegramUsers.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="web" className="space-y-4">
            <div className="space-y-2">
              {webUsers.map((user) => (
                <div key={user.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{user.name || user.email}</span>
                      {user.is_premium && (
                        <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                          <Crown className="h-3 w-3 mr-1" />
                          Премиум
                        </Badge>
                      )}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {user.email} • Зарегистрирован: {new Date(user.created_at).toLocaleDateString()}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Switch
                      checked={user.is_premium || false}
                      onCheckedChange={() => togglePremium(user.id, 'web', user.is_premium)}
                      disabled={updating[`web-${user.id}`]}
                    />
                    {updating[`web-${user.id}`] && (
                      <div className="text-xs text-muted-foreground">Обновление...</div>
                    )}
                  </div>
                </div>
              ))}
              {webUsers.length === 0 && (
                <div className="text-center text-muted-foreground py-8">
                  Веб-пользователи не найдены
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="telegram" className="space-y-4">
            <div className="space-y-2">
              {telegramUsers.map((user) => (
                <div key={user.tg_id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">
                        {user.name || `Пользователь ${user.tg_id}`}
                      </span>
                      {user.is_premium && (
                        <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                          <Crown className="h-3 w-3 mr-1" />
                          Премиум
                        </Badge>
                      )}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      ID: {user.tg_id} • Баллы: {user.score || 0} • Дней подряд: {user.streak_days || 0}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Switch
                      checked={user.is_premium || false}
                      onCheckedChange={() => togglePremium(user.tg_id, 'telegram', user.is_premium)}
                      disabled={updating[`telegram-${user.tg_id}`]}
                    />
                    {updating[`telegram-${user.tg_id}`] && (
                      <div className="text-xs text-muted-foreground">Обновление...</div>
                    )}
                  </div>
                </div>
              ))}
              {telegramUsers.length === 0 && (
                <div className="text-center text-muted-foreground py-8">
                  Telegram пользователи не найдены
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>

        <div className="mt-6 pt-4 border-t">
          <Button onClick={loadUsers} variant="outline" className="w-full">
            <Database className="h-4 w-4 mr-2" />
            Обновить данные
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}; 