import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "@/hooks/use-toast";
import { Smile, Meh, Frown, Heart, Star } from "lucide-react";

const moods = [
  { value: "excellent", label: "Отлично", icon: Star, color: "bg-green-500" },
  { value: "good", label: "Хорошо", icon: Smile, color: "bg-blue-500" },
  { value: "okay", label: "Нормально", icon: Meh, color: "bg-yellow-500" },
  { value: "bad", label: "Плохо", icon: Frown, color: "bg-orange-500" },
  { value: "terrible", label: "Ужасно", icon: Heart, color: "bg-red-500" }
];

export const MoodTracker = ({ user, onMoodUpdate }) => {
  const [currentMood, setCurrentMood] = useState(user?.mood || null);
  const [loading, setLoading] = useState(false);

  const handleMoodSelect = async (moodValue) => {
    if (!user) return;
    
    setLoading(true);
    try {
      const { error } = await supabase
        .from("profiles")
        .update({ mood: moodValue })
        .eq("user_id", user.user_id);

      if (error) throw error;

      setCurrentMood(moodValue);
      onMoodUpdate?.(moodValue);
      
      toast({
        title: "Настроение обновлено",
        description: `Ваше настроение: ${moods.find(m => m.value === moodValue)?.label}`,
      });
    } catch (error) {
      toast({
        title: "Ошибка",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg">Как настроение?</CardTitle>
        <CardDescription>
          Отследите ваше самочувствие сегодня
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-5 gap-2">
          {moods.map((mood) => {
            const Icon = mood.icon;
            const isSelected = currentMood === mood.value;
            
            return (
              <Button
                key={mood.value}
                variant={isSelected ? "default" : "outline"}
                size="sm"
                disabled={loading}
                onClick={() => handleMoodSelect(mood.value)}
                className={`flex flex-col gap-1 h-auto py-3 ${
                  isSelected ? "ring-2 ring-primary/20" : ""
                }`}
              >
                <Icon className="h-4 w-4" />
                <span className="text-xs font-medium">{mood.label}</span>
              </Button>
            );
          })}
        </div>
        
        {currentMood && (
          <div className="mt-3 text-center">
            <Badge variant="outline" className="text-xs">
              Текущее настроение: {moods.find(m => m.value === currentMood)?.label}
            </Badge>
          </div>
        )}
      </CardContent>
    </Card>
  );
};