// auth.js - utilidades de autenticación
const API_URL = window.API_BASE;

// Registro de usuario
async function registerUser(username, email, password) {
  const payload = { username, email, password };
  const r = await fetch(`${API_URL}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!r.ok) throw new Error("Registro fallido");
  return await r.json();
}

// Login de usuario
async function loginUser(username, password) {
  const payload = { username, password };
  const r = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!r.ok) {
    const errText = await r.text().catch(() => "Error desconocido");
    throw new Error(`Login fallido: ${errText}`);
  }

  const data = await r.json();

  // Detectar la clave correcta del token
  const token =
    data.access_token ||
    data.token ||
    data.jwt ||
    data.access ||
    data.detail?.token ||
    null;

  if (!token) throw new Error("Respuesta del servidor no contiene token");

  // Guardar en localStorage
  localStorage.setItem("token", token);
  localStorage.setItem("username", data.username || username);

  return data;
}

// Obtener usuario autenticado
async function getMe() {
  const token = localStorage.getItem("token");
  if (!token) {
    console.warn("⚠️ No hay token en localStorage");
    return null;
  }

  const headers = {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json"
  };

  try {
    const r = await fetch(`${API_URL}/me`, { headers });

    if (r.status === 401) {
      console.warn("⚠️ Token inválido o expirado. Redirigiendo a login...");
      localStorage.removeItem("token");
      localStorage.removeItem("username");
      window.location.href = "login.html";
      return null;
    }

    if (!r.ok) {
      console.error("❌ Error en /me:", r.status);
      return null;
    }

    const data = await r.json();
    console.log("✅ Usuario autenticado:", data);
    return data;
  } catch (err) {
    console.error("❌ Error de red al consultar /me:", err);
    return null;
  }
}

// Verificación de autenticación
async function checkAuth(redirect = true) {
  const me = await getMe();
  if (!me) {
    if (redirect) window.location.href = "login.html";
    return false;
  }
  return me;
}
