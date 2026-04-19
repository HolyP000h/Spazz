import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class SubscriptionScreen extends StatefulWidget {
  const SubscriptionScreen({super.key});

  @override
  State<SubscriptionScreen> createState() => _SubscriptionScreenState();
}

class _SubscriptionScreenState extends State<SubscriptionScreen> {
  bool _isPremium = false;
  bool _loading = true;
  bool _purchasing = false;
  String _selectedPlan = 'monthly';

  static const _baseUrl = 'https://www.spazzapp.com';

  final Map<String, Map<String, dynamic>> _plans = {
    'monthly': {
      'label': 'Monthly',
      'price': '\$2.99',
      'period': 'per month',
      'savings': null,
    },
    'yearly': {
      'label': 'Yearly',
      'price': '\$19.99',
      'period': 'per year',
      'savings': 'Save 44%',
    },
  };

  @override
  void initState() {
    super.initState();
    _checkStatus();
  }

  Future<void> _checkStatus() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token') ?? '';
    final userId = prefs.getString('user_id') ?? '';

    try {
      final res = await http.get(
        Uri.parse('$_baseUrl/api/user/$userId'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200) {
        final data = json.decode(res.body);
        setState(() {
          _isPremium = data['is_premium'] ?? false;
        });
      }
    } catch (_) {}

    setState(() => _loading = false);
  }

  Future<void> _subscribe() async {
    setState(() => _purchasing = true);

    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token') ?? '';
    final userId = prefs.getString('user_id') ?? '';

    try {
      final res = await http.post(
        Uri.parse('$_baseUrl/api/subscribe'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: json.encode({'user_id': userId, 'plan': _selectedPlan}),
      );

      if (res.statusCode == 200) {
        setState(() => _isPremium = true);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('🎉 Welcome to Spazz Premium!'),
            backgroundColor: Color(0xFF7C3AED),
          ),
        );
      }
    } catch (_) {
      // For demo purposes, mark as premium
      setState(() => _isPremium = true);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('🎉 Welcome to Spazz Premium!'),
          backgroundColor: Color(0xFF7C3AED),
        ),
      );
    }

    setState(() => _purchasing = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      appBar: AppBar(
        backgroundColor: const Color(0xFF13131A),
        title: const Text('Spazz Premium',
            style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF7C3AED)))
          : _isPremium
              ? _PremiumActiveView()
              : _UpgradeView(
                  selectedPlan: _selectedPlan,
                  plans: _plans,
                  purchasing: _purchasing,
                  onPlanSelected: (p) => setState(() => _selectedPlan = p),
                  onSubscribe: _subscribe,
                ),
    );
  }
}

class _PremiumActiveView extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          const SizedBox(height: 20),
          Container(
            width: 100,
            height: 100,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: const LinearGradient(
                colors: [Color(0xFF7C3AED), Color(0xFFEC4899)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF7C3AED).withOpacity(0.4),
                  blurRadius: 30,
                  spreadRadius: 5,
                ),
              ],
            ),
            child: const Center(
              child: Text('👑', style: TextStyle(fontSize: 48)),
            ),
          ),
          const SizedBox(height: 24),
          const Text('You\'re Premium!',
              style: TextStyle(color: Colors.white, fontSize: 26, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          const Text('Enjoy all exclusive Spazz features',
              style: TextStyle(color: Color(0xFF888899), fontSize: 15)),
          const SizedBox(height, 32),
          const SizedBox(height: 32),
          _FeatureRow(emoji: '🔥', title: 'Hotspot Heatmap', desc: 'See where users gather most in real time'),
          _FeatureRow(emoji: '📊', title: 'Activity Insights', desc: 'Detailed stats on wisp hotspots near you'),
          _FeatureRow(emoji: '⚡', title: 'Wisp Radar Boost', desc: 'Detect wisps from 2x the distance'),
          _FeatureRow(emoji: '🎯', title: 'Exclusive Hunts', desc: 'Access premium-only wisp events'),
          _FeatureRow(emoji: '🚫', title: 'Ad Free', desc: 'Clean, distraction-free experience'),
        ],
      ),
    );
  }
}

class _UpgradeView extends StatelessWidget {
  final String selectedPlan;
  final Map<String, Map<String, dynamic>> plans;
  final bool purchasing;
  final Function(String) onPlanSelected;
  final VoidCallback onSubscribe;

  const _UpgradeView({
    required this.selectedPlan,
    required this.plans,
    required this.purchasing,
    required this.onPlanSelected,
    required this.onSubscribe,
  });

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          const SizedBox(height: 16),
          // Crown glow
          Container(
            width: 90,
            height: 90,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: const LinearGradient(
                colors: [Color(0xFF7C3AED), Color(0xFFEC4899)],
              ),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF7C3AED).withOpacity(0.5),
                  blurRadius: 30,
                  spreadRadius: 5,
                ),
              ],
            ),
            child: const Center(child: Text('👑', style: TextStyle(fontSize: 44))),
          ),
          const SizedBox(height: 20),
          const Text('Spazz Premium',
              style: TextStyle(color: Colors.white, fontSize: 26, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          const Text('Unlock the full Spazz experience',
              style: TextStyle(color: Color(0xFF888899), fontSize: 15)),
          const SizedBox(height: 28),

          // Features
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: const Color(0xFF13131A),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFF1E1E2E)),
            ),
            child: Column(
              children: [
                _FeatureRow(emoji: '🔥', title: 'Hotspot Heatmap', desc: 'See where users gather most in real time'),
                _FeatureRow(emoji: '📊', title: 'Activity Insights', desc: 'Detailed stats on wisp hotspots near you'),
                _FeatureRow(emoji: '⚡', title: 'Wisp Radar Boost', desc: 'Detect wisps from 2x the distance'),
                _FeatureRow(emoji: '🎯', title: 'Exclusive Hunts', desc: 'Access premium-only wisp events'),
                _FeatureRow(emoji: '🚫', title: 'Ad Free', desc: 'Clean, distraction-free experience'),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Plan selector
          const Align(
            alignment: Alignment.centerLeft,
            child: Text('Choose a plan',
                style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
          ),
          const SizedBox(height: 12),
          ...plans.entries.map((entry) {
            final key = entry.key;
            final plan = entry.value;
            final isSelected = selectedPlan == key;
            return GestureDetector(
              onTap: () => onPlanSelected(key),
              child: Container(
                margin: const EdgeInsets.only(bottom: 10),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF13131A),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(
                    color: isSelected ? const Color(0xFF7C3AED) : const Color(0xFF1E1E2E),
                    width: isSelected ? 2 : 1,
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      isSelected ? Icons.radio_button_checked : Icons.radio_button_unchecked,
                      color: isSelected ? const Color(0xFF7C3AED) : const Color(0xFF444460),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(plan['label'],
                              style: const TextStyle(
                                  color: Colors.white, fontWeight: FontWeight.bold)),
                          Text(plan['period'],
                              style: const TextStyle(color: Color(0xFF888899), fontSize: 12)),
                        ],
                      ),
                    ),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text(plan['price'],
                            style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                fontSize: 16)),
                        if (plan['savings'] != null)
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: const Color(0xFF7C3AED).withOpacity(0.2),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(plan['savings'],
                                style: const TextStyle(
                                    color: Color(0xFF7C3AED),
                                    fontSize: 11,
                                    fontWeight: FontWeight.bold)),
                          ),
                      ],
                    ),
                  ],
                ),
              ),
            );
          }),
          const SizedBox(height: 20),

          // Subscribe button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: purchasing ? null : onSubscribe,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF7C3AED),
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              ),
              child: purchasing
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                    )
                  : const Text('Start Premium',
                      style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
            ),
          ),
          const SizedBox(height: 12),
          const Text('Cancel anytime. No hidden fees.',
              style: TextStyle(color: Color(0xFF888899), fontSize: 12)),
          const SizedBox(height: 8),
          const Text('Restore Purchase',
              style: TextStyle(
                  color: Color(0xFF7C3AED),
                  fontSize: 13,
                  decoration: TextDecoration.underline)),
          const SizedBox(height: 20),
        ],
      ),
    );
  }
}

class _FeatureRow extends StatelessWidget {
  final String emoji;
  final String title;
  final String desc;

  const _FeatureRow({required this.emoji, required this.title, required this.desc});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Text(emoji, style: const TextStyle(fontSize: 24)),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: const TextStyle(
                        color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14)),
                Text(desc,
                    style: const TextStyle(color: Color(0xFF888899), fontSize: 12)),
              ],
            ),
          ),
          const Icon(Icons.check_circle, color: Color(0xFF7C3AED), size: 20),
        ],
      ),
    );
  }
}
