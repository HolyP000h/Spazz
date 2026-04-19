import 'package:flutter/material.dart';

class MapScreen extends StatelessWidget {
  const MapScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      appBar: AppBar(
        backgroundColor: const Color(0xFF13131A),
        title: const Text('Hunt', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: Row(
              children: [
                const Icon(Icons.bolt, color: Color(0xFFFFD700), size: 18),
                const SizedBox(width: 4),
                const Text('0', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
              ],
            ),
          ),
        ],
      ),
      body: const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.map, size: 80, color: Color(0xFF2A2A3A)),
            SizedBox(height: 16),
            Text('Map coming soon', style: TextStyle(color: Color(0xFF666680))),
            SizedBox(height: 8),
            Text('Wisps will appear near you', style: TextStyle(color: Color(0xFF444460), fontSize: 13)),
          ],
        ),
      ),
    );
  }
}
