import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "@/hooks/use-toast";

export const AuthForm = ({ onAuthSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAuth = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isLogin) {
        // Вход через наш API
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/auth/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email,
            password
          })
        });
        
        if (response.ok) {
          const data = await response.json();
          // Сохраняем токен в localStorage
          localStorage.setItem('authToken', data.access_token);
          localStorage.setItem('user', JSON.stringify(data.user));
          console.log("Успешный вход:", data);
          toast({ title: "Добро пожаловать!" });
          onAuthSuccess();
        } else {
          const errorData = await response.json();
          throw new Error(errorData.detail || "Ошибка входа");
        }
      } else {
        // Регистрация через наш API
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/auth/register`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email,
            password,
            name: email.split('@')[0] // Используем часть email как имя
          })
        });
        
        if (response.ok) {
          const data = await response.json();
          console.log("Результат регистрации:", data);
          
          if (data.requires_confirmation) {
            toast({ 
              title: "Проверьте email", 
              description: "Мы отправили письмо с подтверждением. Проверьте папку спам.",
              variant: "default"
            });
          } else {
            // Если подтверждение не требуется
            localStorage.setItem('authToken', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            toast({ title: "Регистрация успешна! Добро пожаловать!" });
            onAuthSuccess();
          }
        } else {
          const errorData = await response.json();
          throw new Error(errorData.detail || "Ошибка регистрации");
        }
      }
    } catch (error) {
      console.error("Ошибка аутентификации:", error);
      
      let errorMessage = error.message;
      
      // Переводим основные ошибки на русский
      if (error.message.includes("Invalid login credentials") || error.message.includes("Неверный email или пароль")) {
        errorMessage = "Неверный email или пароль";
      } else if (error.message.includes("User already registered") || error.message.includes("уже зарегистрирован")) {
        errorMessage = "Пользователь с таким email уже зарегистрирован";
      } else if (error.message.includes("Password should be at least") || error.message.includes("минимум")) {
        errorMessage = "Пароль должен содержать минимум 6 символов";
      } else if (error.message.includes("Unable to validate email address") || error.message.includes("формат email")) {
        errorMessage = "Некорректный формат email";
      } else if (error.message.includes("Email not confirmed") || error.message.includes("не подтвержден")) {
        errorMessage = "Email не подтвержден. Проверьте почту и нажмите на ссылку подтверждения.";
      }
      
      toast({
        title: "Ошибка",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setLoading(true);
    try {
      // Вход под демо-аккаунтом через наш API
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: "demo@example.com",
          password: "demo123456"
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        // Сохраняем токен в localStorage
        localStorage.setItem('authToken', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        toast({ title: "Вход в демо-режиме успешен!" });
        onAuthSuccess();
      } else {
        // Если демо-аккаунт не существует, создаем его
        if (response.status === 401) {
          const registerResponse = await fetch(`${import.meta.env.VITE_API_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              email: "demo@example.com",
              password: "demo123456",
              name: "Демо Пользователь"
            })
          });
          
          if (registerResponse.ok) {
            const registerData = await registerResponse.json();
            // Сохраняем токен в localStorage
            localStorage.setItem('authToken', registerData.access_token);
            localStorage.setItem('user', JSON.stringify(registerData.user));
            toast({ title: "Демо-аккаунт создан! Добро пожаловать!" });
            onAuthSuccess();
          } else {
            throw new Error("Не удалось создать демо-аккаунт");
          }
        } else {
          throw new Error("Ошибка входа");
        }
      }
    } catch (error) {
      console.error("Ошибка демо-входа:", error);
      toast({
        title: "Ошибка демо-входа",
        description: "Попробуйте зарегистрироваться вручную",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-primary/10 via-accent/5 to-info/10">
      <Card className="w-full max-w-md shadow-card-hover">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold bg-gradient-primary bg-clip-text text-transparent">
            🥗 Трекер Калорий
          </CardTitle>
          <CardDescription>
            {isLogin ? "Войдите в аккаунт" : "Создайте аккаунт"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleAuth} className="space-y-4">
            <div className="space-y-2">
              <Input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Input
                type="password"
                placeholder="Пароль"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <Button 
              type="submit" 
              className="w-full" 
              disabled={loading}
            >
              {loading ? "Загрузка..." : (isLogin ? "Войти" : "Зарегистрироваться")}
            </Button>
          </form>
          
          {/* Кнопка демо-входа */}
          <div className="mt-4">
            <Button 
              onClick={handleDemoLogin}
              variant="outline"
              className="w-full"
              disabled={loading}
            >
              🎭 Демо-вход (без регистрации)
            </Button>
          </div>
          
          <div className="mt-4 text-center">
            <button
              type="button"
              onClick={() => setIsLogin(!isLogin)}
              className="text-sm text-primary hover:underline"
            >
              {isLogin ? "Нет аккаунта? Зарегистрируйтесь" : "Есть аккаунт? Войдите"}
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};