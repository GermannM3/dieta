import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Target, TrendingUp, Calendar } from "lucide-react";

export const DailySummary = ({ user, meals, setMeals }) => {
  const [todayMeals, setTodayMeals] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadTodayMeals = async () => {
    setLoading(true);
    try {
      const today = new Date().toISOString().split('T')[0];
      let mealsData = [];

      if (user) {
        // Зарегистрированный пользователь
        const { data: { user: authUser } } = await supabase.auth.getUser();
        if (!authUser) return;

        const { data, error } = await supabase
          .from("meals")
          .select("*")
          .eq("user_id", authUser.id)
          .eq("date", today)
          .order("time", { ascending: true });

        if (error) throw error;
        mealsData = data || [];
      } else {
        // Гость - загружаем из localStorage
        const sessionMeals = JSON.parse(localStorage.getItem('guestMeals') || '[]');
        mealsData = sessionMeals.filter(meal => meal.date === today);
      }

      setTodayMeals(mealsData);
      setMeals(mealsData);
    } catch (error) {
      console.error("Error loading meals:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTodayMeals();
  }, [user]);

  // Слушаем обновления в реальном времени
  useEffect(() => {
    if (!user) return;

    const channel = supabase
      .channel('meals-changes')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'meals'
        },
        () => {
          loadTodayMeals();
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [user]);

  // Для гостей - слушаем изменения localStorage
  useEffect(() => {
    if (user) return;

    const handleStorageChange = () => {
      loadTodayMeals();
    };

    window.addEventListener('storage', handleStorageChange);
    // Также слушаем кастомное событие для изменений в том же окне
    window.addEventListener('guestMealsChanged', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('guestMealsChanged', handleStorageChange);
    };
  }, [user]);

  if (!user) {
    const totalCalories = todayMeals.reduce((sum, meal) => sum + parseFloat(meal.calories || 0), 0);
    const defaultTarget = 2000; // Дефолтная цель для гостей
    
    return (
      <Card className="shadow-card border-info/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5 text-info" />
            Дневная сводка (гостевой режим)
          </CardTitle>
          <CardDescription>
            Сегодня употреблено калорий
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center space-y-2">
            <div className="text-3xl font-bold text-info">
              {Math.round(totalCalories)}
            </div>
            <p className="text-sm text-muted-foreground">ккал</p>
          </div>
          <div className="text-center text-sm text-muted-foreground">
            Приемов пищи сегодня: {todayMeals.length}
          </div>
          <div className="text-center">
            <Badge variant="outline" className="text-info border-info/50">
              Зарегистрируйтесь для установки цели
            </Badge>
          </div>
        </CardContent>
      </Card>
    );
  }

  const totalCalories = todayMeals.reduce((sum, meal) => sum + parseFloat(meal.calories), 0);
  const targetCalories = user.daily_target;
  const remainingCalories = targetCalories - totalCalories;
  const progressPercentage = Math.min((totalCalories / targetCalories) * 100, 100);

  const getStatusColor = () => {
    if (remainingCalories <= 0) return "health-danger";
    if (remainingCalories <= targetCalories * 0.2) return "health-warning";
    return "health-success";
  };

  const getStatusText = () => {
    if (remainingCalories <= 0) return "Превышение нормы";
    if (remainingCalories <= targetCalories * 0.2) return "Близко к цели";
    return "В пределах нормы";
  };

  return (
    <Card className="shadow-card">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calendar className="h-5 w-5 text-primary" />
          Дневная сводка
        </CardTitle>
        <CardDescription>
          Ваш прогресс по калориям на сегодня
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="text-center space-y-2">
          <div className="text-3xl font-bold text-primary">
            {Math.round(totalCalories)} / {targetCalories}
          </div>
          <p className="text-sm text-muted-foreground">ккал</p>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Прогресс</span>
            <span>{Math.round(progressPercentage)}%</span>
          </div>
          <Progress 
            value={progressPercentage} 
            className="h-2"
            style={{
              backgroundColor: "hsl(var(--muted))"
            }}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center space-y-1">
            <div className="flex items-center justify-center gap-1">
              <Target className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium">Цель</span>
            </div>
            <p className="text-lg font-semibold">{targetCalories}</p>
          </div>
          
          <div className="text-center space-y-1">
            <div className="flex items-center justify-center gap-1">
              <TrendingUp className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium">Употреблено</span>
            </div>
            <p className="text-lg font-semibold">{Math.round(totalCalories)}</p>
          </div>

          <div className="text-center space-y-1">
            <div className="flex items-center justify-center gap-1">
              <span className="text-sm font-medium">Осталось</span>
            </div>
            <p className={`text-lg font-semibold text-${getStatusColor()}`}>
              {remainingCalories > 0 ? Math.round(remainingCalories) : 0}
            </p>
          </div>
        </div>

        <div className="text-center">
          <Badge 
            variant={remainingCalories <= 0 ? "destructive" : "default"}
            className="text-sm"
          >
            {getStatusText()}
          </Badge>
        </div>

        <div className="text-center text-sm text-muted-foreground">
          Приемов пищи сегодня: {todayMeals.length}
        </div>
      </CardContent>
    </Card>
  );
};