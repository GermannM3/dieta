import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/models.dart';
import '../services/api_service.dart';

class AppState extends ChangeNotifier {
  AppState(this._api);

  final ApiService _api;
  static const _tokenKey = 'auth_token';

  bool loading = true;
  String? token;
  UserModel? user;
  ProfileModel? profile;
  List<MealModel> todayMeals = [];
  Map<String, dynamic>? todayStats;
  JourneyData? journey;
  List<Map<String, dynamic>> fatHistory = [];
  List<ChatMessage> dietologHistory = [];
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
    final data = await _api.login(email, password);
    await _saveAuth(data['token'] as String, data['user'] as Map<String, dynamic>);
    await refreshData();
  }

  Future<void> register(String email, String password, String name) async {
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
    notifyListeners();
  }

  Future<void> logout() async {
    token = null;
    user = null;
    profile = null;
    todayMeals = [];
    todayStats = null;
    journey = null;
    fatHistory = [];
    dietologHistory = [];
    _api.setToken(null);
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    notifyListeners();
  }

  Future<void> refreshData() async {
    if (token == null) return;
    try {
      profile = await _api.getProfile();
      final today = DateTime.now().toIso8601String().split('T').first;
      todayMeals = await _api.getMeals(date: today);
      todayStats = await _api.getStats();
      journey = await _api.getJourney();
      fatHistory = await _api.getFatHistory();
      error = null;
    } catch (e) {
      error = e.toString();
    }
    notifyListeners();
  }

  Future<void> loadDietologHistory() async {
    dietologHistory = await _api.getDietologHistory();
    notifyListeners();
  }

  Future<String> sendDietologMessage(String message) async {
    final response = await _api.askDietolog(message);
    await loadDietologHistory();
    return response;
  }

  Future<void> clearDietologChat() async {
    await _api.clearDietologHistory();
    dietologHistory = [];
    notifyListeners();
  }

  Future<void> saveProfile(ProfileModel p) async {
    profile = await _api.updateProfile(p.toUpdateJson());
    journey = await _api.getJourney();
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
    if (profile != null) {
      profile = ProfileModel(
        name: profile!.name,
        gender: profile!.gender,
        age: profile!.age,
        weight: profile!.weight,
        height: profile!.height,
        activityLevel: profile!.activityLevel,
        dailyTarget: profile!.dailyTarget,
        waterTarget: profile!.waterTarget,
        stepsTarget: profile!.stepsTarget,
        mood: profile!.mood,
        waterMl: total,
        score: profile!.score,
        streakDays: profile!.streakDays,
        isPremium: profile!.isPremium,
        bodyFatPercent: profile!.bodyFatPercent,
        goalFatPercent: profile!.goalFatPercent,
        consciousStreak: profile!.consciousStreak,
        longestStreak: profile!.longestStreak,
        totalConsciousDays: profile!.totalConsciousDays,
        journeyDay: profile!.journeyDay,
        startingWeight: profile!.startingWeight,
      );
    }
    notifyListeners();
  }

  Future<void> setMood(String mood) async {
    profile = await _api.updateProfile({'mood': mood});
    notifyListeners();
  }

  Future<FatMeasurement> measureFat({
    required double waist,
    required double hip,
    double? neck,
    double? goal,
  }) async {
    final m = await _api.measureFat(
      waistCm: waist,
      hipCm: hip,
      neckCm: neck,
      goalFatPercent: goal,
    );
    await refreshData();
    return m;
  }
}
