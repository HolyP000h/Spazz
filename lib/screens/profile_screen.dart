import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../services/auth_service.dart';
import '../services/api_service.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  Map<String, dynamic>? _user;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final res = await ApiService.get('/api/me');
      setState(() { _user = res; _loading = false; });
    } catch (_) {
      setState(() => _loading = false);
    }
  }

  Future<void> _logout() async {
    await AuthService.clearSession();
    if (mounted) context.go('/login');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      appBar: AppBar(
        backgroundColor: const Color(0xFF13131A),
        title: const Text('Profile', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout, color: Color(0xFF666680)),
            onPressed: _logout,
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _user == null
              ? const Center(child: Text('Failed to load', style: TextStyle(color: Colors.white)))
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    children: [
                      // Avatar
                      Container(
                        width: 90, height: 90,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          gradient: const LinearGradient(
                            colors: [Color(0xFF7C3AED), Color(0xFF06B6D4)],
                          ),
                        ),
                        child: Center(
                          child: Text(
                            (_user!['username'] ?? '?')[0].toUpperCase(),
                            style: const TextStyle(fontSize: 36, fontWeight: FontWeight.w800, color: Colors.white),
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                      Text(_user!['username'] ?? '', style: const TextStyle(
                        fontSize: 22, fontWeight: FontWeight.w700, color: Colors.white,
                      )),
                      if (_user!['is_premium'] == true)
                        Container(
                          margin: const EdgeInsets.only(top: 6),
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
                          decoration: BoxDecoration(
                            gradient: const LinearGradient(colors: [Color(0xFFFFD700), Color(0xFFFFA500)]),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: const Text('PREMIUM', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Colors.black)),
                        ),
                      const SizedBox(height: 32),
                      // Stats
                      _statsGrid(),
                    ],
                  ),
                ),
    );
  }

  Widget _statsGrid() {
    final stats = [
      {'label': 'Wisps', 'value': _user!['wisps_collected']?.toString() ?? '0', 'icon': Icons.bolt},
      {'label': 'Coins', 'value': _user!['credits']?.toString() ?? '0', 'icon': Icons.monetization_on},
      {'label': 'Steps', 'value': _user!['steps']?.toString() ?? '0', 'icon': Icons.directions_walk},
      {'label': 'Level', 'value': _user!['level']?.toString() ?? '1', 'icon': Icons.star},
    ];

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2, crossAxisSpacing: 12, mainAxisSpacing: 12, childAspectRatio: 1.4,
      ),
      itemCount: stats.length,
      itemBuilder: (_, i) {
        final s = stats[i];
        return Container(
          decoration: BoxDecoration(
            color: const Color(0xFF13131A),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFF1E1E2E)),
          ),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Icon(s['icon'] as IconData, color: const Color(0xFF7C3AED), size: 22),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(s['value'] as String, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w700, color: Colors.white)),
                  Text(s['label'] as String, style: const TextStyle(fontSize: 12, color: Color(0xFF666680))),
                ],
              ),
            ],
          ),
        );
      },
    );
  }
}
