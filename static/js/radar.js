async function updateRadar() {
    try {
        const response = await fetch('/api/users');
        const data = await response.json();
        
        console.log("Radar Data Received:", data); // Check your Browser Console (F12) for this!

        data.forEach(user => {
            // Determine color: Purple for users, Cyan for wisps
            const markerColor = user.type === 'wisp' ? '#00ffff' : '#8a2be2';

            L.circleMarker([user.lat, user.lon], {
                radius: user.type === 'wisp' ? 6 : 10,
                fillColor: markerColor,
                color: '#fff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            })
            .addTo(map)
            .bindPopup(`<b>${user.username}</b><br>Type: ${user.type}`);
        });
    } catch (err) {
        console.error("Radar failed to lock onto signals:", err);
    }
}

// Fire the radar
updateRadar();
