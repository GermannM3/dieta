import { useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { toast } from "@/hooks/use-toast";
import { Utensils, Trash2, Clock } from "lucide-react";

export const FoodTable = ({ meals }) => {
  const [deletingId, setDeletingId] = useState(null);

  const deleteMeal = async (mealId) => {
    setDeletingId(mealId);
    try {
      const { error } = await supabase
        .from("meals")
        .delete()
        .eq("id", mealId);

      if (error) throw error;

      toast({ title: "Прием пищи удален" });
    } catch (error) {
      toast({
        title: "Ошибка",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setDeletingId(null);
    }
  };

  const formatTime = (timeString) => {
    return timeString.slice(0, 5);
  };

  const getMealType = (time) => {
    const hour = parseInt(time.split(':')[0]);
    if (hour < 10) return { type: "Завтрак", color: "bg-yellow-100 text-yellow-800" };
    if (hour < 14) return { type: "Обед", color: "bg-green-100 text-green-800" };
    if (hour < 18) return { type: "Полдник", color: "bg-blue-100 text-blue-800" };
    return { type: "Ужин", color: "bg-purple-100 text-purple-800" };
  };

  if (!meals.length) {
    return (
      <Card className="shadow-card">
        <CardContent className="flex flex-col items-center justify-center h-32 text-center">
          <Utensils className="h-8 w-8 text-muted-foreground mb-2" />
          <p className="text-muted-foreground">Приемы пищи не найдены</p>
          <p className="text-sm text-muted-foreground">Добавьте первый прием пищи</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-card">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Utensils className="h-5 w-5 text-primary" />
          Дневник питания
        </CardTitle>
        <CardDescription>
          Все ваши приемы пищи за сегодня
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Время</TableHead>
                <TableHead>Тип</TableHead>
                <TableHead>Продукт</TableHead>
                <TableHead>Вес (г)</TableHead>
                <TableHead>Калории</TableHead>
                <TableHead>Действия</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {meals.map((meal) => {
                const mealType = getMealType(meal.time);
                return (
                  <TableRow key={meal.id}>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Clock className="h-4 w-4 text-muted-foreground" />
                        {formatTime(meal.time)}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={mealType.color}>
                        {mealType.type}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-medium">
                      {meal.food_name}
                    </TableCell>
                    <TableCell>
                      {parseFloat(meal.weight_grams)} г
                    </TableCell>
                    <TableCell>
                      <span className="font-semibold text-primary">
                        {Math.round(parseFloat(meal.calories))} ккал
                      </span>
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => deleteMeal(meal.id)}
                        disabled={deletingId === meal.id}
                        className="text-destructive hover:text-destructive"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
        
        <div className="mt-4 p-4 bg-accent/10 rounded-lg">
          <div className="text-center">
            <p className="text-sm text-muted-foreground">
              Всего калорий: <span className="font-semibold text-primary">
                {Math.round(meals.reduce((sum, meal) => sum + parseFloat(meal.calories), 0))} ккал
              </span>
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};