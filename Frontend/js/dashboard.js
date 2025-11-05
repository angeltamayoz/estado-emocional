// dashboard.js — versión estable y corregida
// ==========================================

console.log("📊 Cargando dashboard.js...");

const API = window.API_BASE;

// ✅ Verifica autenticación al cargar la página
document.addEventListener("DOMContentLoaded", async () => {
  const token = localStorage.getItem("token");
  const username = localStorage.getItem("username");
  const role = localStorage.getItem("role");

  if (!token || !username) {
    console.warn("⚠️ No hay token o username en localStorage. Redirigiendo...");
    window.location.href = "login.html";
    return;
  }

  // Mostrar nombre en el header
  const welcome = document.getElementById("welcome");
  if (welcome) welcome.textContent = `Hola, ${username}`;

  // Inicializar dashboard (cargar estadísticas y conectar WS)
  try {
    await initDashboard(token);
    
    // Configurar botones de tipo de gráfica
    const plotContainer = document.querySelector('.plot-container');
    const plotButtons = document.querySelectorAll('[data-plot-type]');
    const userPlotImg = document.getElementById('userPlotImg');
    
    if (plotButtons.length && userPlotImg) {
      let currentType = 'evolution';
      
      function loadPlot(type) {
        if (plotContainer) plotContainer.classList.add('loading');
        userPlotImg.src = `${API}/user-plot?token=${encodeURIComponent(token)}&kind=${type}&ts=${Date.now()}`;
      }
      
      // Click handlers para los botones de tipo de gráfica
      plotButtons.forEach(btn => {
        btn.addEventListener('click', () => {
          const type = btn.dataset.plotType;
          if (type === currentType) return;
          
          // Update active state
          plotButtons.forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          
          // Load new plot
          currentType = type;
          loadPlot(type);
        });
      });
      
      // Cuando la imagen carga, quitar estado loading
      userPlotImg.onload = () => {
        if (plotContainer) plotContainer.classList.remove('loading');
      };
      
      // Cargar gráfica inicial
      loadPlot('evolution');
    }
  } catch (err) {
    console.error("Error inicializando dashboard:", err);
  }

  // Manejador del formulario de encuestas
  const surveyForm = document.getElementById("surveyForm");
  if (surveyForm) {
    // Validación en tiempo real + sliders feedback
    const fields = {
      mood: document.getElementById("mood"),
      sleep_hours: document.getElementById("sleep_hours"),
      appetite: document.getElementById("appetite"),
      concentration: document.getElementById("concentration")
    };
    function validateMood(val) { return val >= 1 && val <= 10; }
    function validateSleep(val) { return val >= 0 && val <= 24; }
    function validateAppetite(val) { return val >= 0 && val <= 10; }
    function validateConcentration(val) { return val >= 0 && val <= 10; }
    function setFieldState(field, valid) {
      if (valid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
      } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
      }
    }
    // slider feedback (value + emoji/description)
    const moodValueEl = document.getElementById('moodValue');
    const moodEmoji = document.getElementById('moodEmoji');
    const moodText = document.getElementById('moodText');
    const sleepValueEl = document.getElementById('sleepValue');
    const sleepEmoji = document.getElementById('sleepEmoji');
    const sleepText = document.getElementById('sleepText');
    const appetiteValueEl = document.getElementById('appetiteValue');
    const appetiteEmoji = document.getElementById('appetiteEmoji');
    const appetiteText = document.getElementById('appetiteText');
    const concentrationValueEl = document.getElementById('concentrationValue');
    const concentrationEmoji = document.getElementById('concentrationEmoji');
    const concentrationText = document.getElementById('concentrationText');

    function moodDescriptor(v) {
      v = Number(v);
      if (v <= 2) return ['😭', 'Muy triste'];
      if (v <= 4) return ['☹️', 'Triste'];
      if (v <= 6) return ['😐', 'Neutral'];
      if (v <= 8) return ['🙂', 'Contento'];
      return ['😄', 'Muy feliz'];
    }
    function appetiteDescriptor(v) {
      v = Number(v);
      if (v <= 2) return ['🥺', 'Muy bajo'];
      if (v <= 4) return ['😕', 'Bajo'];
      if (v <= 6) return ['😐', 'Normal'];
      if (v <= 8) return ['😊', 'Bueno'];
      return ['🤩', 'Excelente'];
    }
    function concentrationDescriptor(v) {
      v = Number(v);
      if (v <= 2) return ['😵', 'Muy baja'];
      if (v <= 4) return ['😕', 'Baja'];
      if (v <= 6) return ['😐', 'Normal'];
      if (v <= 8) return ['🧐', 'Buena'];
      return ['💡', 'Excelente'];
    }
    function sleepDescriptor(v) {
      v = Number(v);
      if (v < 4) return ['😴', 'Muy poco sueño'];
      if (v < 6) return ['😐', 'Poco sueño'];
      if (v <= 8) return ['🛌', 'Descanso adecuado'];
      return ['😌', 'Buen descanso'];
    }

    fields.mood.addEventListener('input', e => {
      const val = +e.target.value;
      moodValueEl.textContent = val;
      const [emoji,txt] = moodDescriptor(val);
      moodEmoji.textContent = emoji; moodText.textContent = txt;
      setFieldState(e.target, validateMood(val));
    });
    fields.sleep_hours.addEventListener('input', e => {
      const val = +e.target.value;
      sleepValueEl.textContent = val;
      const [emoji,txt] = sleepDescriptor(val);
      sleepEmoji.textContent = emoji; sleepText.textContent = txt;
      setFieldState(e.target, validateSleep(val));
    });
    fields.appetite.addEventListener('input', e => {
      const val = +e.target.value;
      appetiteValueEl.textContent = val;
      const [emoji,txt] = appetiteDescriptor(val);
      appetiteEmoji.textContent = emoji; appetiteText.textContent = txt;
      setFieldState(e.target, validateAppetite(val));
    });
    fields.concentration.addEventListener('input', e => {
      const val = +e.target.value;
      concentrationValueEl.textContent = val;
      const [emoji,txt] = concentrationDescriptor(val);
      concentrationEmoji.textContent = emoji; concentrationText.textContent = txt;
      setFieldState(e.target, validateConcentration(val));
    });

    surveyForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const mood = parseInt(fields.mood.value);
      const sleep_hours = parseFloat(fields.sleep_hours.value);
      const appetite = parseInt(fields.appetite.value);
      const concentration = parseInt(fields.concentration.value);
      const notes = document.getElementById("notes").value || "";

      let valid = true;
      setFieldState(fields.mood, validateMood(mood));
      setFieldState(fields.sleep_hours, validateSleep(sleep_hours));
      setFieldState(fields.appetite, validateAppetite(appetite));
      setFieldState(fields.concentration, validateConcentration(concentration));
      if (!validateMood(mood) || !validateSleep(sleep_hours) || !validateAppetite(appetite) || !validateConcentration(concentration)) {
        valid = false;
      }
      if (!valid) {
        Swal.fire({ icon:'error', title:'Datos inválidos', text:'Por favor corrige los campos marcados.' });
        return;
      }

      // Construir payload asegurando que los valores 0 se envíen correctamente
      const payload = { 
        mood: mood, 
        sleep_hours: sleep_hours, 
        appetite: appetite, 
        concentration: concentration, 
        notes: notes 
      };

      try {
        const res = await fetch(API + "/surveys", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token,
          },
          body: JSON.stringify(payload),
        });

        if (!res.ok) {
          const txt = await res.text().catch(() => null);
          throw new Error(txt || `Error ${res.status}`);
        }

        const data = await res.json();
        console.log("Survey saved:", data);

        Swal.fire({
          icon: "success",
          title: "Estado guardado",
          text: "Tu estado se ha registrado correctamente.",
          showClass: { popup: 'fade-up' }
        });

        // Limpiar formulario
        surveyForm.reset();
        Object.values(fields).forEach(f => f.classList.remove('is-valid','is-invalid'));

        // Refrescar datos del dashboard
        await initDashboard(token);

        // Recargar gráfica personalizada del usuario (manteniendo tipo actual)
        const plotContainer = document.querySelector('.plot-container');
        const activeButton = document.querySelector('[data-plot-type].active');
        const userPlotImg = document.getElementById('userPlotImg');
        if (userPlotImg && activeButton) {
          const currentType = activeButton.dataset.plotType;
          if (plotContainer) plotContainer.classList.add('loading');
          userPlotImg.src = `${API}/user-plot?token=${encodeURIComponent(token)}&kind=${currentType}&ts=${Date.now()}`;
        }

        // Recargar recomendaciones y alertas
        try {
          await loadRecommendations(token);
          await loadAlerts(token);
        } catch (err) {
          console.error("Error recargando recomendaciones/alertas:", err);
        }
      } catch (err) {
        console.error("Error guardando encuesta:", err);
        Swal.fire({ icon: "error", title: "Error", text: err.message || "No se pudo guardar" });
      }
    });

    // Attach logout handler after form setup
    try {
      const logoutBtn = document.getElementById('logoutBtn');
      if (logoutBtn) {
        logoutBtn.addEventListener('click', (evt) => {
          evt.preventDefault();
          evt.stopPropagation();
          Swal.fire({
            title: '¿Cerrar sesión?',
            text: 'Se eliminará tu sesión actual.',
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: 'Sí, salir',
            cancelButtonText: 'Cancelar',
          }).then((r) => {
            if (r && r.isConfirmed) {
              localStorage.removeItem('token');
              localStorage.removeItem('username');
              localStorage.removeItem('role');
              try { if (window.ws) window.ws.close(); } catch (e) {}
              window.location.href = 'login.html';
            } else {
              console.log('Logout cancelled by user');
            }
          });
        });
      }
    } catch (e) {
      console.warn('No se pudo adjuntar logout handler:', e);
    }
  }
});
console.log("⚠️ Saltando validación /me temporalmente (modo entrega)");


// ==========================================
// INICIALIZAR DASHBOARD (gráficas, datos, WS)
// ==========================================

async function initDashboard(token) {
  console.log("🚀 Inicializando dashboard...");

  // Cargar estadísticas iniciales
  try {
    const res = await fetch(API + "/stats", {
      headers: { Authorization: "Bearer " + token },
    });

    if (!res.ok) throw new Error("Error al obtener estadísticas");

    const stats = await res.json();
    renderStats(stats);

  } catch (err) {
    console.error("Error cargando estadísticas:", err);
    Swal.fire({
      icon: "error",
      title: "Error al cargar datos",
      text: "No se pudieron obtener las estadísticas iniciales.",
    });
  }

  // Cargar recomendaciones
  try {
    await loadRecommendations(token);
  } catch (err) {
    console.error("Error cargando recomendaciones:", err);
  }

  // Cargar alertas
  try {
    await loadAlerts(token);
  } catch (err) {
    console.error("Error cargando alertas:", err);
  }

  // Conectar WebSocket (opcional)
  setupWebSocket(token);
}

// ==========================================
// FUNCIONES DE INTERFAZ
// ==========================================

function renderStats(stats) {
  console.log("📈 Renderizando estadísticas:", stats);

  const moodElement = document.getElementById("moodAverage");
  const countElement = document.getElementById("entryCount");

  if (moodElement) moodElement.textContent = stats.average_mood ?? "N/A";
  if (countElement) countElement.textContent = stats.total_entries ?? "0";

  // Si tienes una gráfica de estados de ánimo:
  if (window.Chart && stats.history) {
    const ctx = document.getElementById("moodChart");
    if (ctx) {
      new Chart(ctx, {
        type: "line",
        data: {
          labels: stats.history.map((e) => e.date),
          datasets: [
            {
              label: "Nivel de ánimo",
              data: stats.history.map((e) => e.mood),
              borderWidth: 2,
            },
          ],
        },
        options: { responsive: true },
      });
    }
  }
}

// ==========================================
// WEBSOCKET (actualizaciones en tiempo real)
// ==========================================

function setupWebSocket(token) {
  try {
  const wsUrl = API.replace(/^http/, "ws") + `/ws/alerts?token=${token}`;
    console.log("🌐 Conectando WebSocket:", wsUrl);

    const ws = new WebSocket(wsUrl);
    window.ws = ws;

    ws.onopen = () => console.log("✅ WebSocket conectado");
    ws.onclose = () => console.log("🔌 WebSocket cerrado");
    ws.onerror = (err) => console.error("⚠️ WebSocket error:", err);

    ws.onmessage = (event) => {
      console.log("📨 WS mensaje recibido:", event.data);
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "stats_update") {
          renderStats(msg.data);
        }
      } catch (e) {
        console.warn("Mensaje WS no válido:", event.data);
      }
    };
  } catch (err) {
    console.error("Error inicializando WebSocket:", err);
  }
}

// ==========================================
// CERRAR SESIÓN
// ==========================================

document.addEventListener("click", (e) => {
  if (e.target.matches("#logoutBtn")) {
    e.preventDefault();
    Swal.fire({
      title: "¿Cerrar sesión?",
      text: "Se eliminará tu sesión actual.",
      icon: "question",
      showCancelButton: true,
      confirmButtonText: "Sí, salir",
      cancelButtonText: "Cancelar",
    }).then((r) => {
      if (r.isConfirmed) {
        localStorage.removeItem("token");
        localStorage.removeItem("username");
        localStorage.removeItem("role");
        if (window.ws) window.ws.close();
        window.location.href = "login.html";
      }
    });
  }
});

// ==========================================
// FUNCIONES PARA RECOMENDACIONES Y ALERTAS
// ==========================================

async function loadRecommendations(token) {
  console.log("🎯 Cargando recomendaciones...");
  
  try {
    const res = await fetch(API + "/recommendations", {
      headers: { Authorization: "Bearer " + token },
    });

    if (!res.ok) {
      throw new Error(`Error ${res.status}: ${res.statusText}`);
    }

    const data = await res.json();
    renderRecommendations(data);
    
  } catch (err) {
    console.error("Error al cargar recomendaciones:", err);
    const recsDiv = document.getElementById("recs");
    if (recsDiv) {
      recsDiv.innerHTML = `
        <div class="alert alert-warning" role="alert">
          <small>No se pudieron cargar las recomendaciones.</small>
        </div>
      `;
    }
  }
}

async function loadAlerts(token) {
  console.log("🚨 Cargando alertas...");
  
  try {
    const res = await fetch(API + "/all-alerts", {
      headers: { Authorization: "Bearer " + token },
    });

    if (!res.ok) {
      throw new Error(`Error ${res.status}: ${res.statusText}`);
    }

    const data = await res.json();
    renderAlerts(data);
    
  } catch (err) {
    console.error("Error al cargar alertas:", err);
    const alertsDiv = document.getElementById("alertsTable");
    if (alertsDiv) {
      alertsDiv.innerHTML = `
        <div class="alert alert-warning" role="alert">
          <small>No se pudieron cargar las alertas.</small>
        </div>
      `;
    }
  }
}

function renderRecommendations(data) {
  console.log("📋 Renderizando recomendaciones:", data);
  
  const recsDiv = document.getElementById("recs");
  if (!recsDiv) return;

  const riskLevelClass = {
    'ALTO': 'danger',
    'MODERADO': 'warning', 
    'BAJO': 'success'
  };

  const riskLevelIcon = {
    'ALTO': '🔴',
    'MODERADO': '🟡',
    'BAJO': '🟢'
  };

  const riskClass = riskLevelClass[data.risk_level] || 'secondary';
  const riskIcon = riskLevelIcon[data.risk_level] || '⚪';

  let html = `
    <div class="alert alert-${riskClass} mb-3" role="alert">
      <h6 class="alert-heading">${riskIcon} Nivel de riesgo: ${data.risk_level}</h6>
      <p class="mb-0"><strong>${data.recommendation}</strong></p>
    </div>
  `;

  if (data.general_tips && data.general_tips.length > 0) {
    html += `
      <div class="mt-3">
        <h6 class="text-muted">Consejos generales:</h6>
        <ul class="list-unstyled">
    `;
    
    data.general_tips.forEach(tip => {
      html += `<li class="mb-1"><small>💡 ${tip}</small></li>`;
    });
    
    html += `
        </ul>
      </div>
    `;
  }

  recsDiv.innerHTML = html;
}

function renderAlerts(data) {
  console.log("🚨 Renderizando alertas:", data);
  
  const alertsDiv = document.getElementById("alertsTable");
  if (!alertsDiv) return;

  if (!data.alerts || data.alerts.length === 0) {
    alertsDiv.innerHTML = `
      <div class="alert alert-info" role="alert">
        <small>No hay alertas en este momento.</small>
      </div>
    `;
    return;
  }

  let html = `
    <div class="table-responsive">
      <table class="table table-sm table-hover">
        <thead>
          <tr>
            <th>Usuario</th>
            <th>Nivel de Riesgo</th>
            <th>Puntaje Promedio</th>
            <th>Tendencia</th>
          </tr>
        </thead>
        <tbody>
  `;

  data.alerts.forEach(alert => {
    const riskClass = {
      'ALTO': 'table-danger',
      'MODERADO': 'table-warning',
      'BAJO': 'table-success'
    }[alert.risk_level] || '';

    const trendIcon = alert.trend_negative ? '📉' : '📈';
    const trendText = alert.trend_negative ? 'Negativa' : 'Positiva';

    html += `
      <tr class="${riskClass}">
        <td><strong>${alert.username}</strong></td>
        <td>${alert.risk_level}</td>
        <td>${alert.avg_score.toFixed(1)}</td>
        <td>${trendIcon} ${trendText}</td>
      </tr>
    `;
  });

  html += `
        </tbody>
      </table>
    </div>
    <div class="mt-2">
      <small class="text-muted">Total de alertas: ${data.total_alerts}</small>
    </div>
  `;

  alertsDiv.innerHTML = html;
}
