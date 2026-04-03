// 1. Setup & Global State
let firstLoad = true;
let lockedTargetId = null;
let lastDistance = 999999;
let markers = {};
let myLat, myLon; 

// Initialize the Map (Dark Mode)
var map = L.map('map', { 
    zoomControl: false,
    zoomSnap: 0.1 
}).setView([39.3331, -82.9824], 14);

L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: 'SPAZZ Stealth Radar',
    maxZoom: 20
}).addTo(map);

// 2. The Main Radar Loop (Runs every 3 seconds)
async function updateRadar() {
    try {
        const response = await fetch('/api/users');
        const data = await response.json();
        const currentIds = new Set(data.map(u => u.id));
        const allCoords = [];
        const mapEl = document.getElementById('map');

        data.forEach(user => {
            const color = user.wisp_class === 'whisp-red' ? '#ff0000' : 
                          (user.type === 'user' ? '#8a2be2' : '#00ffff');

            // --- Manage Markers ---
            if (markers[user.id]) {
                markers[user.id].setLatLng([user.lat, user.lon]);
            } else {
                markers[user.id] = L.circleMarker([user.lat, user.lon], {
                    radius: user.type === 'user' ? 10 : 7,
                    fillColor: color,
                    color: '#fff',
                    weight: 2,
                    fillOpacity: 0.8
                }).addTo(map);

                // --- 🔒 LOCK ON LOGIC ---
                markers[user.id].on('click', () => { 
                    lockedTargetId = user.id; 
                    console.log("🔒 LOCKED ONTO: " + user.username);
                    
                    // Show the Discovery Card when clicked
                    const card = document.getElementById('discovery-card');
                    if (card) card.style.display = 'block';
                    
                    // Update card text if possible
                    const nameEl = document.getElementById('username');
                    if (nameEl) nameEl.innerText = user.username || "Unknown Entity";
                });
            }
            allCoords.push([user.lat, user.lon]);

            // --- 🎯 HUNT LOGIC (If this is our target) ---
            if (lockedTargetId === user.id && myLat) {
                const dist = getHaversineDistance(myLat, myLon, user.lat, user.lon);

                // --- 📈 PROXIMITY BAR UPDATE ---
                // Fills up as you get within 300 meters
                let fillPercent = Math.max(0, Math.min(100, 100 - (dist / 3))); 
                const fillEl = document.getElementById('proximity-fill');
                if(fillEl) fillEl.style.height = fillPercent + "%";

                // 🏆 THE COLLECTION TRIGGER (Within 15 meters)
                if (dist < 15) {
                    triggerWinEffect(user);
                    return; 
                }

                // ⚡ THE SPAZZ EFFECT
                let jitter = 0, blur = 0;
                if (dist < 40) { jitter = 15; blur = 5; } 
                else if (dist < 150) { jitter = 5; blur = 1; }

                // 👣 Wrong Way Penalty (Fade out)
                mapEl.style.opacity = (dist > lastDistance) ? "0.4" : "1.0";
                lastDistance = dist;

                // Apply Glitch to Map
                mapEl.style.filter = `blur(${blur}px) contrast(${100 + jitter * 10}%)`;
                mapEl.style.transform = `translate(${Math.random() * jitter}px, ${Math.random() * jitter}px)`;
                
                document.getElementById('status').innerText = `🎯 TRACKING: ${Math.round(dist)}m`;
            }
        });

        // --- 🎥 THE CAMERA FIX ---
        // Only fit bounds ONCE at the start. After that, GPS takes over.
        if (firstLoad && allCoords.length > 0) {
            map.fitBounds(L.latLngBounds(allCoords), { padding: [50, 50] });
            firstLoad = false;
            const boot = document.getElementById('boot-screen');
            if (boot) {
                boot.style.opacity = '0';
                setTimeout(() => boot.remove(), 1000);
            }
        }

        // Cleanup old markers
        Object.keys(markers).forEach(id => {
            if (!currentIds.has(id)) { map.removeLayer(markers[id]); delete markers[id]; }
        });

    } catch (err) { console.error("Radar Error:", err); }
}

// 3. The GPS "Glide" Tracker
function startTracking() {
    const geoOptions = {
        enableHighAccuracy: true, 
        maximumAge: 0, 
        timeout: 10000 
    };

    navigator.geolocation.watchPosition((position) => {
        myLat = position.coords.latitude;
        myLon = position.coords.longitude;

        // Smoothly glide the map to your feet
        map.panTo([myLat, myLon], { animate: true, duration: 1.5 });
        
        // Ensure zoom is tight for walking
        if (map.getZoom() < 17) map.setZoom(17, { animate: true }); 
        
        console.log("📍 GPS Update:", myLat, myLon);
    }, (err) => {
        console.warn("GPS Signal Weak", err);
        const status = document.getElementById('status');
        if (status) status.innerText = "SIGNAL WEAK...";
    }, geoOptions);
}

// 4. Haversine Formula (Distance Math)
function getHaversineDistance(lat1, lon1, lat2, lon2) {
    const R = 6371e3; 
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon/2) * Math.sin(dLon/2);
    return R * (2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)));
}

// 5. The "Win" Effect
function triggerWinEffect(user) {
    console.log("🏆 COLLECTED!");
    fetch(`/api/collect/${user.id}`, { method: 'POST' });
    
    document.getElementById('map').style.filter = "invert(1) hue-rotate(180deg)";
    document.getElementById('status').innerText = "SIGNAL HARVESTED!";
    lockedTargetId = null;

    const flash = document.createElement('div');
    flash.className = 'collection-flash';
    document.body.appendChild(flash);
    setTimeout(() => flash.remove(), 500);
    
    setTimeout(() => { 
        document.getElementById('map').style.filter = "none"; 
        document.getElementById('discovery-card').style.display = 'none';
    }, 2000);
}

// Kick it off
startTracking();
setInterval(updateRadar, 3000);
