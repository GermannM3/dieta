import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/models.dart';
import '../services/api_service.dart';

class AppState extends ChangeNotifier {
  AppState(this._api);

  final ApiService _api;
  static const _tokenKey = 'auth_token';
  static const _userKey = 'auth_user';

  bool loading = true;
  String? token;
  UserModel? user;
  ProfileModel? profile;
  List<MealModel> todayMeals = [];
  Map<String, dynamic>? todayStats;
  String? error;

  ApiService get api => _api;

  Future<void> init() async {
    loading = true;
    notifyListeners();
    final prefs = await SharedPreferences.getInstance();
    token = prefs.getString(_tokenKey);
    if (token != null) {
      _api.setToken(token);
      try {
        user = await _api.me();
        await refreshData();
      } catch (e) {
        await logout();
      }
    }
    loading = false;
    notifyListeners();
  }

  Future<void> login(String email, String password) async {
    error = null;
    final data = await _api.login(email, password);
    await _saveAuth(data['token'] as String, data['user'] as Map<String, dynamic>);
    await refreshData();
  }

  Future<void> register(String email, String password, String name) async {
    error = null;
    final data = await _api.register(email, password, name: name);
    await _saveAuth(data['token'] as String, data['user'] as Map<String, dynamic>);
    await refreshData();
  }

  Future<void> _saveAuth(String newToken, Map<String, dynamic> userJson) async {
    token = newToken;
    user = UserModel.fromJson(userJson);
    _api.setToken(token);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, newToken);
    await prefs.setString(_userKey, userJson.toString());
    notifyListeners();
  }

  Future<void> logout() async {
    token = null;
    user = null;
    profile = null;
    todayMeals = [];
    todayStats = null;
    _api.setToken(null);
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_userKey);
    notifyListeners();
  }

  Future<void> refreshData() async {
    if (token == null) return;
    try {
      profile = await _api.getProfile();
      final today = DateTime.now().toIso8601String().split('T').first;
      todayMeals = await _api.getMeals(date: today);
      todayStats = await _api.getStats();
      error = null;
    } catch (e) {
      error = e.toString();
    }
    notifyListeners();
  }

  Future<void> saveProfile(ProfileModel p) async {
    profile = await _api.updateProfile(p.toUpdateJson());
    notifyListeners();
  }

  Future<void> addMeal(MealModel meal) async {
    await _api.addMeal(meal);
    await refreshData();
  }

  Future<void> deleteMeal(int id) async {
    await _api.deleteMeal(id);
    await refreshData();
  }

  Future<void> addWater(int ml) async {
    final total = await _api.updateWater(ml);
    profile = profile?.copyWithWater(total) ??
        ProfileModel(waterMl: total);
    notifyListeners();
  }

  Future<void> setMood(String mood) async {
    profile = await _api.updateProfile({'mood': mood});
    notifyListeners();
  }
}

extension _ProfileCopy on ProfileModel {
  ProfileModel copyWithWater(int waterMl) => ProfileModel(
        name: name,
        gender: gender,
        age: age,
        weight: weight,
        height: height,
        activityLevel: activityLevel,
        dailyTarget: dailyTarget,
        waterTarget: waterTarget,
        stepsTarget: stepsTarget,
        mood: mood,
        waterMl: waterMl,
        score: score,
        streakDays: streakDays,
        isPremium: isPremium,
      );
}
