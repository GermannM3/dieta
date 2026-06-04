import 'package:flutter_test/flutter_test.dart';
import 'package:tvoy_dietolog/main.dart';

void main() {
  testWidgets('App smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const TvoyDietologApp());
    expect(find.text('Твой Диетолог'), findsOneWidget);
  });
}
