import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/models.dart';
import '../providers/app_state.dart';
import '../theme/app_theme.dart';

class DietologTab extends StatefulWidget {
  const DietologTab({super.key});

  @override
  State<DietologTab> createState() => _DietologTabState();
}

class _DietologTabState extends State<DietologTab> {
  final _controller = TextEditingController();
  final _scroll = ScrollController();
  final List<ChatMessage> _messages = [];
  bool _loading = false;

  Future<void> _send() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _loading) return;
    _controller.clear();
    setState(() {
      _messages.add(ChatMessage(role: 'user', content: text));
      _loading = true;
    });
    _scrollToBottom();

    try {
      final api = context.read<AppState>().api;
      final history = _messages
          .map((m) => {'role': m.role, 'content': m.content})
          .toList();
      final response = await api.askDietolog(text, history);
      setState(() {
        _messages.add(ChatMessage(role: 'assistant', content: response));
      });
    } catch (e) {
      setState(() {
        _messages.add(ChatMessage(role: 'assistant', content: 'Ошибка: $e'));
      });
    } finally {
      setState(() => _loading = false);
      _scrollToBottom();
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scroll.hasClients) {
        _scroll.animateTo(
          _scroll.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                AppColors.primary.withOpacity(0.1),
                AppColors.accent.withOpacity(0.1),
              ],
            ),
          ),
          child: const Row(
            children: [
              Text('👨‍⚕️', style: TextStyle(fontSize: 28)),
              SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('ИИ-диетолог', style: TextStyle(fontWeight: FontWeight.bold)),
                    Text(
                      'Консультации с учётом вашего профиля',
                      style: TextStyle(fontSize: 12, color: AppColors.mutedForeground),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        Expanded(
          child: _messages.isEmpty
              ? const Center(
                  child: Padding(
                    padding: EdgeInsets.all(24),
                    child: Text(
                      'Спросите о питании, калориях или составьте план на день.\n\nНапример: «Что съесть на ужин при дефиците калорий?»',
                      textAlign: TextAlign.center,
                      style: TextStyle(color: AppColors.mutedForeground, height: 1.5),
                    ),
                  ),
                )
              : ListView.builder(
                  controller: _scroll,
                  padding: const EdgeInsets.all(16),
                  itemCount: _messages.length,
                  itemBuilder: (context, i) {
                    final msg = _messages[i];
                    final isUser = msg.role == 'user';
                    return Align(
                      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                      child: Container(
                        margin: const EdgeInsets.only(bottom: 8),
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.8),
                        decoration: BoxDecoration(
                          color: isUser
                              ? AppColors.primary.withOpacity(0.12)
                              : AppColors.muted,
                          borderRadius: BorderRadius.only(
                            topLeft: const Radius.circular(16),
                            topRight: const Radius.circular(16),
                            bottomLeft: Radius.circular(isUser ? 16 : 4),
                            bottomRight: Radius.circular(isUser ? 4 : 16),
                          ),
                        ),
                        child: Text(msg.content),
                      ),
                    );
                  },
                ),
        ),
        if (_loading)
          const Padding(
            padding: EdgeInsets.all(8),
            child: LinearProgressIndicator(minHeight: 2),
          ),
        SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: const InputDecoration(
                      hintText: 'Ваш вопрос...',
                      contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                    ),
                    textInputAction: TextInputAction.send,
                    onSubmitted: (_) => _send(),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filled(
                  onPressed: _send,
                  icon: const Icon(Icons.send, color: Colors.white),
                  style: IconButton.styleFrom(backgroundColor: AppColors.primary),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
