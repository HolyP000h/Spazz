// 1. Initialize Global Variables
let firstLoad = true;
let lastDistance = 999999;
let lockedTargetId = null;
let markers = {};

var map = L.map('map', { zoomControl: false }).setView([39.3331, -82.9824], 14);

// 2. Add Dark Matter tiles
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: 'SPAZZ Stealth Radar | &copy; CARTO',
    subdomains: 'abcd',
    maxZoom: 20
}).addTo(map);

// 3. The Main Engine
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

            // 1. Marker Management
            if (markers[user.id]) {
                markers[user.id].setLatLng([user.lat, user.lon]);
            } else {
                markers[user.id] = L.circleMarker([user.lat, user.lon], {
                    radius: user.type === 'user' ? 10 : 7,
                    fillColor: color,
                    color: '#fff',
                    weight: 2,
                    fillOpacity: 0.8,
                    className: user.wisp_class || '' 
                }).addTo(map).bindPopup(`<b>${user.username}</b>`);

                markers[user.id].on('click', () => { 
                    lockedTargetId = user.id; 
                    console.log("🔒 LOCKED ONTO:", user.username);
                });
            }
            allCoords.push([user.lat, user.lon]);

            // 2. SPAZZ & VICTORY LOGIC (Only runs for the Locked Target)
            if (lockedTargetId === user.id) {
                // Use currentLat/Lon from your GPS tracker
                const distance = getHaversineDistance(currentLat || 39.3331, currentLon || -82.9824, user.lat, user.lon);
                
                // 🏆 VICTORY CHECK
                if (distance < 15) {
                    console.log("🏆 VICTORY: Target Reached!");
                    yourOldCollectFunction(user.id); 
                    lockedTargetId = null; // Unlock after collection
                    return; 
                }

                // ⚡ THE SPAZZ SCALE
                let jitter = 0, blur = 0;
                if (distance < 30) { jitter = 15; blur = 5; document.getElementById('status').innerText = "⚠️ CRITICAL PROXIMITY"; } 
                else if (distance < 150) { jitter = 4; blur = 1; document.getElementById('status').innerText = "📡 SIGNAL GAIN"; } 
                else { document.getElementById('status').innerText = `🎯 TRACKING: ${Math.round(distance)}m`; }

                // 👣 Wrong Way Detection
                mapEl.style.opacity = (distance > lastDistance) ? "0.4" : "1.0";
                mapEl.style.transition = "opacity 0.5s ease";
                lastDistance = distance;

                // ⚡ Apply Visual Glitch
                mapEl.style.filter = `blur(${blur}px) contrast(${100 + jitter * 10}%)`;
                mapEl.style.transform = `translate(${Math.random() * jitter}px, ${Math.random() * jitter}px)`;
            }
        });

        // 3. Cleanup & Auto-Zoom
        Object.keys(markers).forEach(id => {
            if (!currentIds.has(id)) { map.removeLayer(markers[id]); delete markers[id]; }
        });

        if (firstLoad && allCoords.length > 0) {
            map.fitBounds(L.latLngBounds(allCoords), { padding: [100, 100] });
            firstLoad = false;
            const boot = document.getElementById('boot-screen');
            if (boot) { boot.style.opacity = '0'; setTimeout(() => boot.remove(), 1000); }
        }
    } catch (err) { console.error("⚠️ Radar Sync Error:", err); }
}