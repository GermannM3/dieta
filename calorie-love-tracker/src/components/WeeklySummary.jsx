import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { supabase } from "@/integrations/supabase/client";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { TrendingUp } from "lucide-react";

export const WeeklySummary = ({ user }) => {
  const [weeklyData, setWeeklyData] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      loadWeeklyData();
    }
  }, [user]);

  const loadWeeklyData = async () => {
    if (!user) return;
    
    setLoading(true);
    try {
      const today = new Date();
      const fromDate = new Date(today);
      fromDate.setDate(today.getDate() - 6);

      const fromStr = fromDate.toISOString().split("T")[0];
      const toStr = today.toISOString().split("T")[0];

      // Получаем данные о приемах пищи за неделю
      const { data: meals, error: mealsError } = await supabase
        .from("meals")
        .select("date, calories")
        .eq("user_id", user.user_id)
        .gte("date", fromStr)
        .lte("date", toStr);

      if (mealsError) throw mealsError;

      // Создаем структуру данных для всех 7 дней
      const weekData = [];
      for (let i = 0; i < 7; i++) {
        const currentDate = new Date(fromDate);
        currentDate.setDate(fromDate.getDate() + i);
        const dateStr = currentDate.toISOString().split("T")[0];
        
        weekData.push({
          date: dateStr,
          dayName: currentDate.toLocaleDateString('ru-RU', { weekday: 'short' }),
          kcal: 0,
          water: i === 6 ? (user.water_ml || 0) : 0 // Показываем воду только за сегодня
        });
      }

      // Группируем калории по дням
      meals?.forEach((meal) => {
        const dayIndex = weekData.findIndex(day => day.date === meal.date);
        if (dayIndex !== -1) {
          weekData[dayIndex].kcal += meal.calories || 0;
        }
      });

      setWeeklyData(weekData);
    } catch (error) {
      console.error("Error loading weekly data:", error);
    } finally {
      setLoading(false);
    }
  };

  if (!user) return null;

  const totalWeekCalories = weeklyData.reduce((sum, day) => sum + day.kcal, 0);
  const avgDailyCalories = weeklyData.length > 0 ? Math.round(totalWeekCalories / 7) : 0;

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Сводка за неделю
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4 text-center">
          <div className="p-3 bg-muted/50 rounded-lg">
            <div className="text-lg font-semibold text-primary">{totalWeekCalories}</div>
            <div className="text-xs text-muted-foreground">Всего калорий</div>
          </div>
          <div className="p-3 bg-muted/50 rounded-lg">
            <div className="text-lg font-semibold text-accent">{avgDailyCalories}</div>
            <div className="text-xs text-muted-foreground">Среднее в день</div>
          </div>
        </div>

        {weeklyData.length > 0 && (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={weeklyData} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
                <XAxis 
                  dataKey="dayName" 
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis 
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(value) => `${value}`}
                />
                <Tooltip 
                  formatter={(value, name) => [
                    `${value} ${name === 'kcal' ? 'ккал' : 'мл'}`, 
                    name === 'kcal' ? 'Калории' : 'Вода'
                  ]}
                  labelFormatter={(label, payload) => {
                    if (payload && payload.length > 0) {
                      const date = payload[0].payload.date;
                      return new Date(date).toLocaleDateString('ru-RU');
                    }
                    return label;
                  }}
                />
                <Legend />
                <Bar 
                  dataKey="kcal" 
                  fill="hsl(var(--primary))" 
                  name="Калории"
                  radius={[2, 2, 0, 0]}
                />
                <Bar 
                  dataKey="water" 
                  fill="hsl(var(--info))" 
                  name="Вода"
                  radius={[2, 2, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {loading && (
          <div className="text-center text-muted-foreground">
            Загружаем данные...
          </div>
        )}
      </CardContent>
    </Card>
  );
};