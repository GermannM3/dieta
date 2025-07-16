import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "@/hooks/use-toast";
import { Trophy, Star, Flame, Target } from "lucide-react";

export const ScoreTracker = ({ user, onScoreUpdate }) => {
  const [dailyScore, setDailyScore] = useState(0);

  useEffect(() => {
    if (user) {
      calculateDailyScore();
    }
  }, [user]);

  const calculateDailyScore = async () => {
    if (!user) return;

    let score = 0;
    
    // Базовые очки за заполнение профиля
    if (user.name && user.age && user.weight && user.height) {
      score += 10;
    }

    // Очки за настроение
    if (user.mood) {
      const moodPoints = {
        'excellent': 20,
        'good': 15,
        'okay': 10,
        'bad': 5,
        'terrible': 2
      };
      score += moodPoints[user.mood] || 0;
    }

    // Очки за воду (1 очко за каждые 250мл)
    if (user.water_ml) {
      score += Math.floor(user.water_ml / 250);
    }

    // Очки за streak
    if (user.streak_days) {
      score += user.streak_days * 5;
    }

    setDailyScore(score);

    // Обновляем общий счёт в базе данных
    try {
      const { error } = await supabase
        .from("profiles")
        .update({ score: (user.score || 0) + score })
        .eq("user_id", user.user_id);

      if (error) throw error;
      
      onScoreUpdate?.((user.score || 0) + score);
    } catch (error) {
      console.error("Error updating score:", error);
    }
  };

  const getScoreLevel = (score) => {
    if (score >= 1000) return { level: "Мастер", icon: Trophy, color: "text-yellow-500" };
    if (score >= 500) return { level: "Эксперт", icon: Star, color: "text-purple-500" };
    if (score >= 200) return { level: "Активный", icon: Flame, color: "text-orange-500" };
    return { level: "Новичок", icon: Target, color: "text-green-500" };
  };

  const getStreakMessage = () => {
    const days = user?.streak_days || 0;
    if (days === 0) return "Начните вести учёт!";
    if (days === 1) return "Отличное начало! 🎯";
    if (days < 7) return `${days} дней подряд! 🔥`;
    if (days < 30) return `${days} дней! Вы молодец! 🏆`;
    return `${days} дней! Невероятно! 🌟`;
  };

  if (!user) return null;

  const { level, icon: LevelIcon, color } = getScoreLevel(user.score || 0);

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center gap-2">
          <LevelIcon className={`h-5 w-5 ${color}`} />
          Очки и достижения
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-2xl font-bold">{user.score || 0}</div>
            <div className="text-sm text-muted-foreground">Общий счёт</div>
          </div>
          <Badge variant="outline" className={color}>
            {level}
          </Badge>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="text-center p-3 bg-muted/50 rounded-lg">
            <div className="text-lg font-semibold text-primary">{dailyScore}</div>
            <div className="text-xs text-muted-foreground">Сегодня</div>
          </div>
          <div className="text-center p-3 bg-muted/50 rounded-lg">
            <div className="text-lg font-semibold text-accent">{user.streak_days || 0}</div>
            <div className="text-xs text-muted-foreground">Дней подряд</div>
          </div>
        </div>

        <div className="text-center text-sm text-muted-foreground">
          {getStreakMessage()}
        </div>

        <div className="text-xs text-muted-foreground space-y-1">
          <div>• Заполнение профиля: +10 очков</div>
          <div>• Отличное настроение: +20 очков</div>
          <div>• Каждые 250мл воды: +1 очко</div>
          <div>• День подряд: +5 очков</div>
        </div>
      </CardContent>
    </Card>
  );
};