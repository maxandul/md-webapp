// 🛠️ Utility-Funktionen

// Datum formatieren (YYYY-MM-DD → DD.MM.YYYY)
function formatDate(dateString) {
    if (!dateString) return '';
    const parts = dateString.split('-');
    if (parts.length !== 3) return dateString;
    return `${parts[2]}.${parts[1]}.${parts[0]}`;
}

// Datum formatieren für Input (DD.MM.YYYY → YYYY-MM-DD)
function formatDateForInput(dateString) {
    if (!dateString) return '';
    const parts = dateString.split('.');
    if (parts.length !== 3) return dateString;
    return `${parts[2]}-${parts[1]}-${parts[0]}`;
}

// Status-Text bereinigen
function cleanStatus(status) {
    const map = {
        'Geplant': 'Geplant',
        'In Bearbeitung': 'In Bearbeitung',
        'Abgeschlossen': 'Abgeschlossen'
    };
    return map[status] || status;
}

// Fehler anzeigen
function showAlert(message, type = 'error') {
    const alertDiv = document.createElement('div');
    alertDiv.className = type === 'error' ? 'error-message' : 'success-message';
    alertDiv.textContent = message;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Loading Spinner anzeigen/verstecken
function setLoading(elementId, isLoading) {
    const element = document.getElementById(elementId);
    if (element) {
        element.disabled = isLoading;
        if (isLoading) {
            element.dataset.originalText = element.textContent;
            element.textContent = 'Laden...';
        } else {
            element.textContent = element.dataset.originalText || element.textContent;
        }
    }
}

// Token aus Session holen
function getToken() {
    return sessionStorage.getItem('app_token');
}

// User-Daten aus Session holen
function getUserData() {
    const data = sessionStorage.getItem('user_data');
    return data ? JSON.parse(data) : null;
}

// Check ob eingeloggt
function checkAuth() {
    if (!getToken() || !getUserData()) {
        window.location.href = 'index.html';
        return false;
    }
    return true;
}
```

---

## 🧪 **Test: Dashboard**

1. **Server läuft**
2. **Browser:** `http://localhost:5000`
3. **Login** mit einem Token (z.B. `FK67890_...`)

**Du solltest sehen:**
- ✅ Dashboard-Header mit deinem Namen
- ✅ 4 Statistik-Karten (Gesamt, Geplant, etc.)
- ✅ Liste der Gespräche als Cards
- ✅ Klick auf Card → Weiterleitung (404 ist ok)

**Im Server-Terminal solltest du sehen:**
```
127.0.0.1 - - [21/Jan/2026 13:20:15] "GET /api/gespraeche HTTP/1.1" 200 -