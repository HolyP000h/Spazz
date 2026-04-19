import 'package:flutter/material.dart';
import 'dart:async';
import 'dart:convert';
import 'dart:math';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:geolocator/geolocator.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'subscription_screen.dart';

class MapScreen extends StatefulWidget {
  const MapScreen({super.key});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  GoogleMapController? _mapController;
  Position? _myPosition;
  bool _loading = true;
  bool _isPremium = false;
  String _token = '';
  String _userId = '';

  Set<Marker> _markers = {};
  Set<Circle> _hotspotCircles = {};

  List<dynamic> _nearbyUsers = [];
  List<dynamic> _wisps = [];
  List<dynamic> _hotspots = [];

  Timer? _locationTimer;
  Timer? _fetchTimer;

  static const _baseUrl = 'https://www.spazzapp.com';

  @override
  void initState() {
    super.initState();
    _init();
  }

  @override
  void dispose() {
    _locationTimer?.cancel();
    _fetchTimer?.cancel();
    _mapController?.dispose();
    super.dispose();
  }

  Future<void> _init() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('token') ?? '';
    _userId = prefs.getString('user_id') ?? '';

    // Check premium
    try {
      final res = await http.get(
        Uri.parse('$_baseUrl/api/user/$_userId'),
        headers: {'Authorization': 'Bearer $_token'},
      );
      if (res.statusCode == 200) {
        final data = json.decode(res.body);
        _isPremium = data['is_premium'] ?? false;
      }
    } catch (_) {}

    await _getLocation();

    // Ping location every 30 seconds
    _locationTimer = Timer.periodic(const Duration(seconds: 30), (_) => _pingLocation());

    // Fetch nearby data every 15 seconds
    _fetchTimer = Timer.periodic(const Duration(seconds: 15), (_) => _fetchNearby());

    await _fetchNearby();
    setState(() => _loading = false);
  }

  Future<void> _getLocation() async {
    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) return;

    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) return;
    }

    try {
      final pos = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
      setState(() => _myPosition = pos);
      await _pingLocation();
    } catch (_) {}
  }

  Future<void> _pingLocation() async {
    if (_myPosition == null) return;
    try {
      await http.post(
        Uri.parse('$_baseUrl/api/location/update'),
        headers: {
          'Authorization': 'Bearer $_token',
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'user_id': _userId,
          'lat': _myPosition!.latitude,
          'lng': _myPosition!.longitude,
        }),
      );
    } catch (_) {}
  }

  Future<void> _fetchNearby() async {
    if (_myPosition == null) return;
    try {
      final res = await http.get(
        Uri.parse(
            '$_baseUrl/api/nearby?lat=${_myPosition!.latitude}&lng=${_myPosition!.longitude}&user_id=$_userId'),
        headers: {'Authorization': 'Bearer $_token'},
      );
      if (res.statusCode == 200) {
        final data = json.decode(res.body);
        setState(() {
          _nearbyUsers = data['users'] ?? [];
          _wisps = data['wisps'] ?? [];
          _hotspots = data['hotspots'] ?? [];
        });
        _buildMarkers();
      }
    } catch (_) {
      // Use mock data if backend isn't ready
      _buildMockMarkers();
    }
  }

  void _buildMarkers() {
    final markers = <Marker>{};
    final circles = <Circle>{};

    // My location marker
    if (_myPosition != null) {
      markers.add(Marker(
        markerId: const MarkerId('me'),
        position: LatLng(_myPosition!.latitude, _myPosition!.longitude),
        infoWindow: const InfoWindow(title: 'You'),
        icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueViolet),
      ));
    }

    // Nearby users
    for (final user in _nearbyUsers) {
      markers.add(Marker(
        markerId: MarkerId('user_${user['id']}'),
        position: LatLng(user['lat'], user['lng']),
        infoWindow: InfoWindow(title: user['username'] ?? 'Hunter'),
        icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueBlue),
      ));
    }

    // Wisps (collectibles)
    for (final wisp in _wisps) {
      markers.add(Marker(
        markerId: MarkerId('wisp_${wisp['id']}'),
        position: LatLng(wisp['lat'], wisp['lng']),
        infoWindow: InfoWindow(
          title: '✨ Wisp',
          snippet: '+${wisp['xp'] ?? 10} XP',
        ),
        icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueYellow),
        onTap: () => _collectWisp(wisp),
      ));
    }

    // Hotspot heatmap (premium only)
    if (_isPremium) {
      for (final hotspot in _hotspots) {
        final intensity = (hotspot['visit_count'] ?? 1).toDouble();
        circles.add(Circle(
          circleId: CircleId('hotspot_${hotspot['id']}'),
          center: LatLng(hotspot['lat'], hotspot['lng']),
          radius: 50 + (intensity * 10).clamp(0, 200),
          fillColor: Color.fromRGBO(
            255,
            (50 - intensity * 5).clamp(0, 50).toInt(),
            0,
            (0.1 + intensity * 0.05).clamp(0.1, 0.5),
          ),
          strokeColor: Colors.transparent,
          strokeWidth: 0,
        ));
      }
    }

    setState(() {
      _markers = markers;
      _hotspotCircles = circles;
    });
  }

  void _buildMockMarkers() {
    if (_myPosition == null) return;
    final rand = Random();
    final markers = <Marker>{};
    final circles = <Circle>{};

    // My marker
    markers.add(Marker(
      markerId: const MarkerId('me'),
      position: LatLng(_myPosition!.latitude, _myPosition!.longitude),
      infoWindow: const InfoWindow(title: 'You'),
      icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueViolet),
    ));

    // Mock nearby users
    for (int i = 0; i < 3; i++) {
      final lat = _myPosition!.latitude + (rand.nextDouble() - 0.5) * 0.01;
      final lng = _myPosition!.longitude + (rand.nextDouble() - 0.5) * 0.01;
      markers.add(Marker(
        markerId: MarkerId('mock_user_$i'),
        position: LatLng(lat, lng),
        infoWindow: InfoWindow(title: 'Hunter ${i + 1}'),
        icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueBlue),
      ));
    }

    // Mock wisps
    for (int i = 0; i < 5; i++) {
      final lat = _myPosition!.latitude + (rand.nextDouble() - 0.5) * 0.008;
      final lng = _myPosition!.longitude + (rand.nextDouble() - 0.5) * 0.008;
      markers.add(Marker(
        markerId: MarkerId('mock_wisp_$i'),
        position: LatLng(lat, lng),
        infoWindow: const InfoWindow(title: '✨ Wisp', snippet: '+10 XP'),
        icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueYellow),
      ));
    }

    // Mock hotspots (premium)
    if (_isPremium) {
      for (int i = 0; i < 3; i++) {
        final lat = _myPosition!.latitude + (rand.nextDouble() - 0.5) * 0.015;
        final lng = _myPosition!.longitude + (rand.nextDouble() - 0.5) * 0.015;
        circles.add(Circle(
          circleId: CircleId('mock_hotspot_$i'),
          center: LatLng(lat, lng),
          radius: 80 + rand.nextDouble() * 120,
          fillColor: const Color.fromRGBO(255, 50, 0, 0.25),
          strokeColor: Colors.transparent,
          strokeWidth: 0,
        ));
      }
    }

    setState(() {
      _markers = markers;
      _hotspotCircles = circles;
    });
  }

  Future<void> _collectWisp(Map<String, dynamic> wisp) async {
    try {
      await http.post(
        Uri.parse('$_baseUrl/api/wisp/collect'),
        headers: {
          'Authorization': 'Bearer $_token',
          'Content-Type': 'application/json',
        },
        body: json.encode({'wisp_id': wisp['id'], 'user_id': _userId}),
      );
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('✨ Wisp collected! +${wisp['xp'] ?? 10} XP'),
          backgroundColor: const Color(0xFF7C3AED),
          duration: const Duration(seconds: 2),
        ),
      );
      _fetchNearby();
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      body: Stack(
        children: [
          // Map
          _myPosition == null
              ? const Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      CircularProgressIndicator(color: Color(0xFF7C3AED)),
                      SizedBox(height: 16),
                      Text('Getting your location...',
                          style: TextStyle(color: Color(0xFF888899))),
                    ],
                  ),
                )
              : GoogleMap(
                  initialCameraPosition: CameraPosition(
                    target: LatLng(_myPosition!.latitude, _myPosition!.longitude),
                    zoom: 15.5,
                  ),
                  onMapCreated: (c) => _mapController = c,
                  markers: _markers,
                  circles: _hotspotCircles,
                  myLocationEnabled: true,
                  myLocationButtonEnabled: false,
                  zoomControlsEnabled: false,
                  mapType: MapType.normal,
                  style: _darkMapStyle,
                ),

          // Top bar
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                children: [
                  // Live users count
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: const Color(0xCC13131A),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      children: [
                        Container(
                          width: 8,
                          height: 8,
                          decoration: const BoxDecoration(
                            color: Color(0xFF22C55E),
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 6),
                        Text('${_nearbyUsers.length} nearby',
                            style: const TextStyle(color: Colors.white, fontSize: 13)),
                      ],
                    ),
                  ),
                  const Spacer(),
                  // Premium hotspot button
                  GestureDetector(
                    onTap: () {
                      if (!_isPremium) {
                        Navigator.push(context,
                            MaterialPageRoute(builder: (_) => const SubscriptionScreen()));
                      }
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      decoration: BoxDecoration(
                        color: _isPremium
                            ? const Color(0xCC7C3AED)
                            : const Color(0xCC13131A),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                          color: _isPremium
                              ? const Color(0xFF7C3AED)
                              : const Color(0xFF444460),
                        ),
                      ),
                      child: Row(
                        children: [
                          const Text('🔥', style: TextStyle(fontSize: 14)),
                          const SizedBox(width: 4),
                          Text(
                            _isPremium ? 'Heatmap ON' : 'Heatmap 👑',
                            style: TextStyle(
                              color: _isPremium ? Colors.white : const Color(0xFF888899),
                              fontSize: 13,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Bottom legend
          Positioned(
            bottom: 20,
            left: 16,
            right: 16,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                color: const Color(0xCC13131A),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _LegendItem(color: const Color(0xFF7C3AED), label: 'You'),
                  _LegendItem(color: Colors.blue, label: 'Hunters'),
                  _LegendItem(color: Colors.yellow, label: 'Wisps'),
                  if (_isPremium)
                    _LegendItem(color: Colors.orange, label: 'Hotspots'),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _LegendItem extends StatelessWidget {
  final Color color;
  final String label;

  const _LegendItem({required this.color, required this.label});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 10,
          height: 10,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 5),
        Text(label, style: const TextStyle(color: Colors.white, fontSize: 12)),
      ],
    );
  }
}

const _darkMapStyle = '''
[
  {"elementType": "geometry", "stylers": [{"color": "#0A0A0F"}]},
  {"elementType": "labels.text.fill", "stylers": [{"color": "#746855"}]},
  {"elementType": "labels.text.stroke", "stylers": [{"color": "#242f3e"}]},
  {"featureType": "road", "elementType": "geometry", "stylers": [{"color": "#1E1E2E"}]},
  {"featureType": "road", "elementType": "geometry.stroke", "stylers": [{"color": "#212a37"}]},
  {"featureType": "road.highway", "elementType": "geometry", "stylers": [{"color": "#2a2a3a"}]},
  {"featureType": "water", "elementType": "geometry", "stylers": [{"color": "#0d1b2a"}]},
  {"featureType": "poi", "elementType": "geometry", "stylers": [{"color": "#13131A"}]},
  {"featureType": "transit", "elementType": "geometry", "stylers": [{"color": "#2f3948"}]}
]
''';
