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

  // Функция для тестирования подключения к API
  const testApiConnection = async () => {
    try {
      console.log("Тестирование подключения к API...");
      const base = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
      const response = await fetch(`${base}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      console.log("Статус API:", response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log("API ответ:", data);
        toast({
          title: "✅ API доступен",
          description: "Сервер работает корректно",
        });
      } else {
        throw new Error(`API недоступен: ${response.status}`);
      }
    } catch (error) {
      console.error("Ошибка подключения к API:", error);
      toast({
        title: "❌ API недоступен",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  const handleAuth = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      console.log("Попытка аутентификации:", { email, isLogin });
      console.log("API URL:", import.meta.env.VITE_API_URL);

      if (isLogin) {
        // Вход через наш API
        const base = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
        const response = await fetch(`${base}/auth/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email,
            password
          })
        });
        
        console.log("Ответ сервера:", response.status, response.statusText);
        
        if (response.ok) {
          const data = await response.json();
          console.log("Успешный вход:", data);
          
          // Сохраняем токен под ключом 'token' (как читает админка)
          localStorage.setItem('token', data.access_token);
          localStorage.setItem('user', JSON.stringify(data.user));
          
          toast({ 
            title: "Добро пожаловать!",
            description: `Вход выполнен для ${data.user?.email || email}`
          });
          onAuthSuccess();
        } else {
          const errorData = await response.json().catch(() => ({ detail: "Неизвестная ошибка" }));
          console.error("Ошибка входа:", errorData);
          throw new Error(errorData.detail || `Ошибка входа: ${response.status}`);
        }
      } else {
        // Регистрация через наш API
        const base = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
        const response = await fetch(`${base}/auth/register`, {
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
        
        console.log("Ответ сервера регистрации:", response.status, response.statusText);
        
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
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            toast({ title: "Регистрация успешна! Добро пожаловать!" });
            onAuthSuccess();
          }
        } else {
          const errorData = await response.json().catch(() => ({ detail: "Неизвестная ошибка" }));
          console.error("Ошибка регистрации:", errorData);
          throw new Error(errorData.detail || `Ошибка регистрации: ${response.status}`);
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
      } else if (error.message.includes("Failed to fetch") || error.message.includes("NetworkError")) {
        errorMessage = "Ошибка подключения к серверу. Проверьте интернет-соединение.";
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
      console.log("Попытка демо-входа");
      
      // Вход под демо-аккаунтом через наш API
      const base = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
      const response = await fetch(`${base}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: "demo@example.com",
          password: "demo123456"
        })
      });
      
      console.log("Ответ демо-входа:", response.status);
      
      if (response.ok) {
        const data = await response.json();
        // Сохраняем токен под ключом 'token'
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        toast({ title: "Вход в демо-режиме успешен!" });
        onAuthSuccess();
      } else {
        // Если демо-аккаунт не существует, создаем его
        if (response.status === 401) {
          console.log("Создаем демо-аккаунт");
          const registerResponse = await fetch(`${import.meta.env.VITE_API_URL}/auth/register`, {
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
            // Сохраняем токен под ключом 'token'
            localStorage.setItem('token', registerData.access_token);
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

          {/* Кнопка тестирования API */}
          <div className="mt-2">
            <Button 
              onClick={testApiConnection}
              variant="ghost"
              size="sm"
              className="w-full text-xs"
            >
              🔧 Тест подключения к API
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