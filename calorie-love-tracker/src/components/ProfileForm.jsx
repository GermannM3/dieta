import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { toast } from "@/hooks/use-toast";
import { User } from "lucide-react";

export const ProfileForm = ({ user, setUser, onProfileCreated }) => {
  const [formData, setFormData] = useState({
    name: "",
    gender: "",
    age: "",
    weight: "",
    height: "",
    activity_level: "",
    water_target: "",
    steps_target: ""
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      setFormData({
        name: user.name || "",
        gender: user.gender || "",
        age: user.age?.toString() || "",
        weight: user.weight?.toString() || "",
        height: user.height?.toString() || "",
        activity_level: user.activity_level?.toString() || "",
        water_target: user.water_target?.toString() || "2000",
        steps_target: user.steps_target?.toString() || "10000"
      });
    }
  }, [user]);

  const calculateDailyTarget = (gender, age, weight, height, activityLevel) => {
    // Формула Миффлина-Сан Жеора
    let bmr;
    if (gender === "male") {
      bmr = 10 * weight + 6.25 * height - 5 * age + 5;
    } else {
      bmr = 10 * weight + 6.25 * height - 5 * age - 161;
    }
    return Math.round(bmr * activityLevel);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const { data: { user: authUser } } = await supabase.auth.getUser();
      if (!authUser) throw new Error("Пользователь не авторизован");

      const dailyTarget = calculateDailyTarget(
        formData.gender,
        parseInt(formData.age),
        parseFloat(formData.weight),
        parseFloat(formData.height),
        parseFloat(formData.activity_level)
      );

      const profileData = {
        user_id: authUser.id,
        name: formData.name,
        gender: formData.gender,
        age: parseInt(formData.age),
        weight: parseFloat(formData.weight),
        height: parseFloat(formData.height),
        activity_level: parseFloat(formData.activity_level),
        daily_target: dailyTarget,
        water_target: parseInt(formData.water_target) || 2000,
        steps_target: parseInt(formData.steps_target) || 10000
      };

      let result;
      if (user) {
        result = await supabase
          .from("profiles")
          .update(profileData)
          .eq("user_id", authUser.id)
          .select()
          .single();
      } else {
        result = await supabase
          .from("profiles")
          .insert(profileData)
          .select()
          .single();
      }

      if (result.error) throw result.error;

      setUser(result.data);
      toast({ title: user ? "Профиль обновлен!" : "Профиль создан!" });
      onProfileCreated?.();
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
    <Card className="shadow-card">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <User className="h-5 w-5 text-primary" />
          {user ? "Редактировать профиль" : "Создать профиль"}
        </CardTitle>
        <CardDescription>
          Заполните информацию для расчета дневной нормы калорий
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Имя</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="gender">Пол</Label>
              <Select
                value={formData.gender}
                onValueChange={(value) => setFormData({ ...formData, gender: value })}
                required
              >
                <SelectTrigger>
                  <SelectValue placeholder="Выберите пол" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="male">Мужской</SelectItem>
                  <SelectItem value="female">Женский</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="age">Возраст</Label>
              <Input
                id="age"
                type="number"
                value={formData.age}
                onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                required
                min="1"
                max="150"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="weight">Вес (кг)</Label>
              <Input
                id="weight"
                type="number"
                step="0.1"
                value={formData.weight}
                onChange={(e) => setFormData({ ...formData, weight: e.target.value })}
                required
                min="1"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="height">Рост (см)</Label>
              <Input
                id="height"
                type="number"
                value={formData.height}
                onChange={(e) => setFormData({ ...formData, height: e.target.value })}
                required
                min="1"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="activity">Уровень активности</Label>
            <Select
              value={formData.activity_level}
              onValueChange={(value) => setFormData({ ...formData, activity_level: value })}
              required
            >
              <SelectTrigger>
                <SelectValue placeholder="Выберите уровень активности" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1.2">Сидячий образ жизни</SelectItem>
                <SelectItem value="1.375">Легкая активность (1-3 раза в неделю)</SelectItem>
                <SelectItem value="1.55">Умеренная активность (3-5 раз в неделю)</SelectItem>
                <SelectItem value="1.725">Высокая активность (6-7 раз в неделю)</SelectItem>
                <SelectItem value="1.9">Очень высокая активность</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="water_target">Цель по воде (мл/день)</Label>
              <Input
                id="water_target"
                type="number"
                value={formData.water_target}
                onChange={(e) => setFormData({ ...formData, water_target: e.target.value })}
                min="500"
                max="5000"
                step="250"
                placeholder="2000"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="steps_target">Цель по шагам (шагов/день)</Label>
              <Input
                id="steps_target"
                type="number"
                value={formData.steps_target}
                onChange={(e) => setFormData({ ...formData, steps_target: e.target.value })}
                min="1000"
                max="50000"
                step="1000"
                placeholder="10000"
              />
            </div>
          </div>

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Сохранение..." : (user ? "Обновить профиль" : "Создать профиль")}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};