window.onload = function() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    let img = null;
    let isDrawing = false;
    let startX, startY, endX, endY;

    // Append canvas to the DOM where the image is displayed
    const imgElement = document.querySelector('img#processed-image');  // Change this to the correct image ID if necessary
    if (imgElement) {
        imgElement.parentElement.appendChild(canvas);
        loadImage(imgElement.src);
    }

    // Function to load the image onto the canvas
    function loadImage(src) {
        img = new Image();
        img.src = src;
        img.onload = function() {
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);
        };
    }

    // Start drawing the ROI when mouse is pressed down
    canvas.addEventListener('mousedown', function(e) {
        isDrawing = true;
        const rect = canvas.getBoundingClientRect();
        startX = e.clientX - rect.left;
        startY = e.clientY - rect.top;
    });

    // Draw rectangle as the ROI
    canvas.addEventListener('mousemove', function(e) {
        if (isDrawing) {
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0);
            ctx.strokeStyle = 'green';
            ctx.lineWidth = 2;
            ctx.strokeRect(startX, startY, x - startX, y - startY);
        }
    });

    // Stop drawing and capture ROI coordinates
    canvas.addEventListener('mouseup', function(e) {
        isDrawing = false;
        const rect = canvas.getBoundingClientRect();
        endX = e.clientX - rect.left;
        endY = e.clientY - rect.top;
        const roiCoords = {
            startX: startX,
            startY: startY,
            endX: endX,
            endY: endY
        };
        sendCoordinatesToFlask(roiCoords);
    });

    // Function to send ROI coordinates to Flask
    function sendCoordinatesToFlask(roiCoords) {
        fetch('/get_roi_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(roiCoords)
        })
        .then(response => response.json())
        .then(data => {
            // Update the UI with the returned latitudes, longitudes, and other info
            document.getElementById('lat-long').innerText = `Lat/Long: ${data.lat_long}`;
            document.getElementById('side-lengths').innerText = `Side Lengths: ${data.side_lengths}`;
            document.getElementById('area').innerText = `Area: ${data.area}`;
        })
        .catch(error => console.error('Error:', error));
    }
};
