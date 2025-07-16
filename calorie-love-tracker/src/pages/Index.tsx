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

  useEffect(() => {
    // Получаем текущую сессию
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      if (session) {
        loadUserProfile(session.user.id);
      } else {
        setLoading(false);
      }
    });

    // Слушаем изменения авторизации
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
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

      if (error && error.code !== "PGRST116") throw error;
      setUser(data);
    } catch (error) {
      console.error("Error loading profile:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = async () => {
    const { error } = await supabase.auth.signOut();
    if (error) {
      toast({
        title: "Ошибка",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Загрузка...</p>
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="min-h-screen">
        
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
        
        <div className="container mx-auto px-4 py-8">
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
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Index;
