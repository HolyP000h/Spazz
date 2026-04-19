import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ShopScreen extends StatefulWidget {
  const ShopScreen({super.key});

  @override
  State<ShopScreen> createState() => _ShopScreenState();
}

class _ShopScreenState extends State<ShopScreen> {
  List<Map<String, dynamic>> _items = [];
  bool _loading = true;
  int _coins = 0;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final shopRes = await ApiService.get('/api/shop');
      final meRes = await ApiService.get('/api/me');
      setState(() {
        _items = List<Map<String, dynamic>>.from(shopRes['items'] ?? []);
        _coins = meRes['credits'] ?? 0;
        _loading = false;
      });
    } catch (_) {
      setState(() => _loading = false);
    }
  }

  Future<void> _buy(String itemId) async {
    try {
      await ApiService.post('/api/shop/buy', {'item_id': itemId});
      _load();
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Purchased! ✨'), backgroundColor: Color(0xFF7C3AED)),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString()), backgroundColor: const Color(0xFFEF4444)),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      appBar: AppBar(
        backgroundColor: const Color(0xFF13131A),
        title: const Text('Shop', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: Row(
              children: [
                const Icon(Icons.monetization_on, color: Color(0xFFFFD700), size: 18),
                const SizedBox(width: 4),
                Text('$_coins', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
              ],
            ),
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : GridView.builder(
              padding: const EdgeInsets.all(16),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2, crossAxisSpacing: 12, mainAxisSpacing: 12, childAspectRatio: 0.75,
              ),
              itemCount: _items.length,
              itemBuilder: (_, i) {
                final item = _items[i];
                return Container(
                  decoration: BoxDecoration(
                    color: const Color(0xFF13131A),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: const Color(0xFF1E1E2E)),
                  ),
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(item['emoji'] ?? '✨', style: const TextStyle(fontSize: 36)),
                      const SizedBox(height: 8),
                      Text(item['name'] ?? '', style: const TextStyle(
                        color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14,
                      )),
                      const SizedBox(height: 4),
                      Text(item['description'] ?? '', style: const TextStyle(
                        color: Color(0xFF666680), fontSize: 11,
                      ), maxLines: 2, overflow: TextOverflow.ellipsis),
                      const Spacer(),
                      ElevatedButton(
                        onPressed: () => _buy(item['id']),
                        style: ElevatedButton.styleFrom(
                          minimumSize: const Size(double.infinity, 36),
                          padding: EdgeInsets.zero,
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.monetization_on, size: 14, color: Color(0xFFFFD700)),
                            const SizedBox(width: 4),
                            Text('${item['cost']}', style: const TextStyle(fontWeight: FontWeight.w700)),
                          ],
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
    );
  }
}
