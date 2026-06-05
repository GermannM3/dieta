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
  bool _loading = false;
  bool _historyLoaded = false;

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    try {
      await context.read<AppState>().loadDietologHistory();
    } finally {
      if (mounted) setState(() => _historyLoaded = true);
    }
  }

  List<ChatMessage> get _messages => context.watch<AppState>().dietologHistory;

  Future<void> _send() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _loading) return;
    _controller.clear();
    setState(() => _loading = true);
    _scrollToBottom();

    try {
      await context.read<AppState>().sendDietologMessage(text);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$e')));
      }
    } finally {
      if (mounted) setState(() => _loading = false);
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
    final profile = context.watch<AppState>().profile;

    return Column(
      children: [
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                AppColors.primary.withOpacity(0.12),
                AppColors.accent.withOpacity(0.12),
              ],
            ),
          ),
          child: Row(
            children: [
              const Text('👨‍⚕️', style: TextStyle(fontSize: 28)),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('ИИ-диетолог', style: TextStyle(fontWeight: FontWeight.bold)),
                    Text(
                      profile?.isComplete == true
                          ? '${profile!.name}, ${profile.dailyTarget?.toInt() ?? "?"} ккал/день · помню наш диалог'
                          : 'Заполни профиль — ответы станут точнее',
                      style: const TextStyle(fontSize: 12, color: AppColors.mutedForeground),
                    ),
                  ],
                ),
              ),
              if (_messages.isNotEmpty)
                IconButton(
                  icon: const Icon(Icons.delete_outline, size: 20),
                  tooltip: 'Очистить историю',
                  onPressed: () async {
                    await context.read<AppState>().clearDietologChat();
                  },
                ),
            ],
          ),
        ),
        Expanded(
          child: !_historyLoaded
              ? const Center(child: CircularProgressIndicator())
              : _messages.isEmpty
                  ? const Center(
                      child: Padding(
                        padding: EdgeInsets.all(24),
                        child: Text(
                          'Привет! Я знаю твой профиль и помню разговор.\n\n'
                          'Спроси про завтрак, перекус, дефицит калорий или состав блюда.',
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
                            margin: const EdgeInsets.only(bottom: 10),
                            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                            constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.82),
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
                            child: Text(msg.content, style: const TextStyle(height: 1.35)),
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
                      hintText: 'Спроси диетолога...',
                      contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    ),
                    textInputAction: TextInputAction.send,
                    onSubmitted: (_) => _send(),
                    maxLines: 3,
                    minLines: 1,
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filled(
                  onPressed: _send,
                  icon: const Icon(Icons.send, color: Colors.white, size: 20),
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
