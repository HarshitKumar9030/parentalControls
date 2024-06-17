document.addEventListener('DOMContentLoaded', () => {
    loadTrafficData();
    loadAllowedWebsites();
    loadBlockedWebsites();
});

function loadTrafficData() {
    fetch('http://localhost:5000/api/traffic')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById('traffic-table');
            tableBody.innerHTML = '';
            data.forEach(entry => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${entry.src_ip}</td>
                    <td>${entry.dest_ip}</td>
                    <td>${entry.domain}</td>
                    <td>${entry.timestamp}</td>
                    <td class="${entry.flagged ? 'flagged' : ''}">${entry.flagged ? 'Yes' : 'No'}</td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error fetching traffic data:', error);
        });
}

function loadAllowedWebsites() {
    fetch('http://localhost:5000/api/allowed_websites')
        .then(response => response.json())
        .then(data => {
            const list = document.getElementById('allowed-websites-list');
            list.innerHTML = '';
            data.forEach(domain => {
                const listItem = document.createElement('li');
                listItem.textContent = domain;
                listItem.appendChild(createDeleteButton(() => deleteAllowedWebsite(domain)));
                list.appendChild(listItem);
            });
        })
        .catch(error => {
            console.error('Error fetching allowed websites:', error);
        });
}

function loadBlockedWebsites() {
    fetch('http://localhost:5000/api/blocked_websites')
        .then(response => response.json())
        .then(data => {
            const list = document.getElementById('blocked-websites-list');
            list.innerHTML = '';
            data.forEach(domain => {
                const listItem = document.createElement('li');
                listItem.textContent = domain;
                listItem.appendChild(createDeleteButton(() => deleteBlockedWebsite(domain)));
                list.appendChild(listItem);
            });
        })
        .catch(error => {
            console.error('Error fetching blocked websites:', error);
        });
}

function createDeleteButton(onClick) {
    const button = document.createElement('button');
    button.textContent = 'Delete';
    button.style.marginLeft = '10px';
    button.onclick = onClick;
    return button;
}

function addAllowedWebsite() {
    const input = document.getElementById('allowed-website-input');
    const domain = input.value.trim();
    if (domain) {
        fetch('http://localhost:5000/api/allowed_websites', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ domain })
        })
        .then(response => response.json())
        .then(() => {
            input.value = '';
            loadAllowedWebsites();
        })
        .catch(error => {
            console.error('Error adding allowed website:', error);
        });
    }
}

function deleteAllowedWebsite(domain) {
    fetch('http://localhost:5000/api/allowed_websites', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ domain })
    })
    .then(response => response.json())
    .then(loadAllowedWebsites)
    .catch(error => {
        console.error('Error deleting allowed website:', error);
    });
}

function addBlockedWebsite() {
    const input = document.getElementById('blocked-website-input');
    const domain = input.value.trim();
    if (domain) {
        fetch('http://localhost:5000/api/blocked_websites', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ domain })
        })
        .then(response => response.json())
        .then(() => {
            input.value = '';
            loadBlockedWebsites();
        })
        .catch(error => {
            console.error('Error adding blocked website:', error);
        });
    }
}

function deleteBlockedWebsite(domain) {
    fetch('http://localhost:5000/api/blocked_websites', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ domain })
    })
    .then(response => response.json())
    .then(loadBlockedWebsites)
    .catch(error => {
        console.error('Error deleting blocked website:', error);
    });
}
