import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { AuthForm } from "../components/AuthForm";
import { ProfileForm } from "../components/ProfileForm";
import { MealEntryForm } from "../components/MealEntryForm";
import { DailySummary } from "../components/DailySummary";
import { FoodTable } from "../components/FoodTable";
import { MoodTracker } from "../components/MoodTracker";
import { WaterTracker } from "../components/WaterTracker";
import { PresetPicker } from "../components/PresetPicker";
import { AdminPanel } from "../components/AdminPanel";
import { Button } from "@/components/ui/button";
import { LogOut } from "lucide-react";
import { toast } from "@/hooks/use-toast";

const Index = () => {
  const [session, setSession] = useState(null);
  const [user, setUser] = useState(null);
  const [meals, setMeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAuth, setShowAuth] = useState(false);
  const [showGuestMode, setShowGuestMode] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('checking'); // 'checking', 'connected', 'error'

  useEffect(() => {
    // Если есть токен бэкенда — пробуем авторизовать через /api/auth/me
    const tryBackendSession = async () => {
      const token = localStorage.getItem('token');
      if (!token) return false;
      try {
        const base = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
        const resp = await fetch(`${base}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!resp.ok) return false;
        const me = await resp.json();
        // Устанавливаем синтетическую сессию, чтобы показать личный кабинет
        setSession({ user: { id: me.id, email: me.email } });
        setUser({
          user_id: me.id,
          email: me.email,
          name: me.name,
          is_confirmed: me.is_confirmed,
          created_at: me.created_at,
        });
        setLoading(false);
        return true;
      } catch (e) {
        console.error('Backend session check failed:', e);
        return false;
      }
    };

    // Проверяем подключение к Supabase
    const checkConnection = async () => {
      try {
        const { data, error } = await supabase.from('profiles').select('count').limit(1);
        if (error) throw error;
        setConnectionStatus('connected');
      } catch (error) {
        console.error("Ошибка подключения к базе данных:", error);
        setConnectionStatus('error');
      }
    };

    (async () => {
      await checkConnection();

      // Основной источник — Supabase
      const { data: { session }, error } = await supabase.auth.getSession();
      if (error) {
        console.error("Ошибка получения сессии:", error);
        toast({
          title: "Проблема с подключением",
          description: "Не удается подключиться к серверу аутентификации. Попробуйте позже.",
          variant: "destructive",
        });
      }
      setSession(session);
      if (session) {
        loadUserProfile(session.user.id);
      } else {
        // Если Supabase-сессии нет — пробуем сессию по бэкенд-токену
        const ok = await tryBackendSession();
        if (!ok) setLoading(false);
      }
    })();

    // Слушаем изменения авторизации Supabase
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      console.log("Auth state changed:", _event, session);
      setSession(session);
      if (session) {
        loadUserProfile(session.user.id);
      } else {
        setUser(null);
        setMeals([]);
        setLoading(false);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  const loadUserProfile = async (userId) => {
    try {
      const { data, error } = await supabase
        .from("profiles")
        .select("*")
        .eq("user_id", userId)
        .maybeSingle();

      if (error && error.code !== "PGRST116") {
        console.error("Ошибка загрузки профиля:", error);
        throw error;
      }
      setUser(data);
    } catch (error) {
      console.error("Error loading profile:", error);
      toast({
        title: "Ошибка загрузки профиля",
        description: "Не удается загрузить данные профиля. Проверьте подключение к интернету.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = async () => {
    // Выходим из Supabase (если был вход через него)
    await supabase.auth.signOut();
    // Чистим бэкенд-токен
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setSession(null);
    setUser(null);
  };

  // В начале рендера, после проверки loading
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Загрузка...</p>
          {connectionStatus === 'error' && (
            <p className="text-destructive mt-2 text-sm">
              ⚠️ Проблемы с подключением к базе данных
            </p>
          )}
        </div>
      </div>
    );
  }

  // Если нет сессии, показываем главную страницу
  if (!session) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary/5 via-accent/5 to-info/5">
        <div className="container mx-auto px-4 py-8">
          {/* Статус подключения */}
          {connectionStatus === 'error' && (
            <div className="mb-4 p-3 bg-destructive/10 border border-destructive/20 rounded-lg text-center">
              <p className="text-destructive text-sm">
                ⚠️ Проблемы с подключением к серверу. Функции регистрации могут быть недоступны.
              </p>
            </div>
          )}
          
          {connectionStatus === 'connected' && (
            <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-center">
              <p className="text-green-700 text-sm">
                ✅ Подключение к серверу установлено
              </p>
            </div>
          )}
          
          {/* Telegram Bot Link в правом верхнем углу */}
          <div className="fixed top-4 right-4 z-50">
            <a 
              href="https://t.me/tvoy_diet_bot" 
              target="_blank" 
              rel="noopener noreferrer"
              className="group flex flex-col items-center bg-white/90 backdrop-blur-sm rounded-lg p-3 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 border border-primary/20"
            >
              <img 
                src="/kangaroo-icon.svg" 
                alt="Telegram Bot" 
                className="w-8 h-8 mb-1"
              />
              <span className="text-xs font-medium text-center text-primary group-hover:text-primary/80">
                Наш ТГ-бот<br/>с ИИ-диетологом
              </span>
            </a>
          </div>
          
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-primary via-accent to-info bg-clip-text text-transparent mb-4">
              🥗 Трекер Калорий
            </h1>
            <p className="text-muted-foreground mb-6">
              Ведите учет калорий легко и просто
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
                onClick={() => setShowAuth(true)}
                className="bg-gradient-to-r from-primary to-accent"
              >
                Войти / Регистрация
              </Button>
              <Button 
                variant="outline"
                onClick={() => setShowGuestMode(true)}
                className="border-info text-info hover:bg-info/10"
              >
                Попробовать без регистрации
              </Button>
            </div>
          </div>
          
          {showAuth && <AuthForm onAuthSuccess={() => setShowAuth(false)} />}
          
          {showGuestMode && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <DailySummary 
                  user={null} 
                  meals={meals} 
                  setMeals={setMeals} 
                />
                <MealEntryForm 
                  user={null} 
                  onMealAdded={() => {
                    // Для гостей отправляем кастомное событие
                    window.dispatchEvent(new CustomEvent('guestMealsChanged'));
                  }}
                />
              </div>
              
              <FoodTable meals={meals} />
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-accent/5 to-info/5">
      <div className="container mx-auto px-4 py-8">
        
        {/* Telegram Bot Link в правом верхнем углу */}
        <div className="fixed top-4 right-4 z-50">
          <a 
            href="https://t.me/tvoy_diet_bot" 
            target="_blank" 
            rel="noopener noreferrer"
            className="group flex flex-col items-center bg-white/90 backdrop-blur-sm rounded-lg p-3 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 border border-primary/20"
          >
            <img 
              src="/kangaroo-icon.svg" 
              alt="Telegram Bot" 
              className="w-8 h-8 mb-1"
            />
            <span className="text-xs font-medium text-center text-primary group-hover:text-primary/80">
              Наш ТГ-бот<br/>с ИИ-диетологом
            </span>
          </a>
        </div>

        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              🥗 Трекер Калорий
            </h1>
            <p className="text-muted-foreground">
              Привет, {user?.name || session.user.email}!
            </p>
          </div>
          <Button 
            variant="outline" 
            onClick={handleSignOut}
            className="flex items-center gap-2"
          >
            <LogOut className="h-4 w-4" />
            Выйти
          </Button>
        </div>

        {/* Main Content */}
        <div className="space-y-6">
          {/* Profile Section */}
          {!user && (
            <ProfileForm 
              user={user} 
              setUser={setUser}
              onProfileCreated={() => loadUserProfile(session.user.id)}
            />
          )}

          {/* Dashboard */}
          {user && (
            <>
              {/* Mood and Water Tracking */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <MoodTracker 
                  user={user} 
                  onMoodUpdate={(mood) => setUser(prev => ({...prev, mood}))}
                />
                <WaterTracker 
                  user={user} 
                  onWaterUpdate={(water_ml) => setUser(prev => ({...prev, water_ml}))}
                />
              </div>

              {/* Main Dashboard */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <DailySummary 
                  user={user} 
                  meals={meals} 
                  setMeals={setMeals} 
                />
                <MealEntryForm 
                  user={user} 
                  onMealAdded={() => {
                    // Обновление происходит через realtime подписку в DailySummary
                  }}
                />
              </div>

              {/* Presets */}
              <PresetPicker 
                user={user}
                onPresetSelected={(preset) => {
                  // Добавляем все продукты из пресета
                  preset.food_items.forEach(async (item) => {
                    try {
                      await supabase.from("meals").insert({
                        user_id: user.user_id,
                        food_name: item.name,
                        weight_grams: item.weight,
                        calories: item.calories,
                      });
                    } catch (error) {
                      console.error("Error adding preset item:", error);
                    }
                  });
                }}
              />
              
              <FoodTable meals={meals} />

              <div className="text-center">
                <Button 
                  variant="outline" 
                  onClick={() => setUser(null)}
                  className="mt-4"
                >
                  Редактировать профиль
                </Button>
              </div>

              {/* Admin Panel */}
              {user?.email === 'germannm@vk.com' && (
                <div className="mt-8">
                  <AdminPanel user={user} />
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Index;
