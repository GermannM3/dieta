import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Droplets, Zap, Target } from "lucide-react";

const ProgressCircle = ({ value, max, color, size = 80, strokeWidth = 8 }) => {
  const percentage = Math.min((value / max) * 100, 100);
  const circumference = 2 * Math.PI * (size / 2 - strokeWidth);
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="relative">
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={size / 2 - strokeWidth}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="none"
          className="text-muted"
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={size / 2 - strokeWidth}
          stroke={color}
          strokeWidth={strokeWidth}
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="transition-all duration-300 ease-in-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-sm font-bold">{Math.round(percentage)}%</span>
      </div>
    </div>
  );
};

export const ProgressCircles = ({ user, meals }) => {
  if (!user) return null;

  const todayCalories = meals?.reduce((sum, meal) => sum + (meal.calories || 0), 0) || 0;
  const targetCalories = user.daily_target || 2000;
  const waterTarget = user.water_target || 2000;
  const currentWater = user.water_ml || 0;

  // Рассчитываем активность (примерно, можно заменить на реальные данные)
  const activityTarget = 100; // 100% активности
  const currentActivity = Math.min(
    ((todayCalories / targetCalories) * 50) + 
    ((currentWater / waterTarget) * 30) + 
    ((user.mood === 'excellent' ? 20 : user.mood === 'good' ? 15 : 10)),
    100
  );

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center gap-2">
          <Target className="h-5 w-5" />
          Прогресс дня
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-6">
          {/* Калории */}
          <div className="flex flex-col items-center space-y-3">
            <ProgressCircle
              value={todayCalories}
              max={targetCalories}
              color="hsl(var(--primary))"
              size={80}
            />
            <div className="text-center">
              <div className="flex items-center gap-1 text-sm font-medium">
                <Zap className="h-4 w-4 text-primary" />
                Калории
              </div>
              <div className="text-xs text-muted-foreground">
                {Math.round(todayCalories)} / {targetCalories}
              </div>
            </div>
          </div>

          {/* Вода */}
          <div className="flex flex-col items-center space-y-3">
            <ProgressCircle
              value={currentWater}
              max={waterTarget}
              color="hsl(var(--info))"
              size={80}
            />
            <div className="text-center">
              <div className="flex items-center gap-1 text-sm font-medium">
                <Droplets className="h-4 w-4 text-info" />
                Вода
              </div>
              <div className="text-xs text-muted-foreground">
                {currentWater} / {waterTarget} мл
              </div>
            </div>
          </div>

          {/* Активность */}
          <div className="flex flex-col items-center space-y-3">
            <ProgressCircle
              value={currentActivity}
              max={100}
              color="hsl(var(--accent))"
              size={80}
            />
            <div className="text-center">
              <div className="flex items-center gap-1 text-sm font-medium">
                <Target className="h-4 w-4 text-accent" />
                Активность
              </div>
              <div className="text-xs text-muted-foreground">
                Общая активность
              </div>
            </div>
          </div>
        </div>

        {/* Мотивационное сообщение */}
        {todayCalories >= targetCalories && currentWater >= waterTarget && (
          <div className="mt-4 p-3 bg-gradient-to-r from-primary/10 to-accent/10 rounded-lg text-center">
            <span className="text-sm font-medium">🎉 Отличная работа! Цели дня достигнуты!</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};