// ═══════════════════════════════════════════════════════════════
//  Copihue · Backend de Juegos PS2 (v3)
//  Agrega: registrarCupon, verificarCupon → hoja CUPONES_PS2
//  Todo lo anterior sin cambios.
// ═══════════════════════════════════════════════════════════════

const HOJA_RECORDS  = 'RecordsJuegos';
const HOJA_ERRORES  = 'ErroresJuegos';
const HOJA_CUPONES  = 'CUPONES_PS2';
const TOP_N         = 10;
const GAS_VERSION   = 'v3';
const DESCUENTO_PEN = 700; // pesos de descuento por cupón (10% de $7000)

function doGet(e) {
  const action = e.parameter.action;
  const data   = e.parameter.data ? JSON.parse(e.parameter.data) : {};
  let resultado;
  try {
    if (action === 'guardarRecord')    resultado = guardarRecord(data);
    else if (action === 'obtenerRecords') resultado = obtenerRecords(data);
    else if (action === 'guardarError')   resultado = guardarError(data);
    else if (action === 'registrarCupon') resultado = registrarCupon(data);
    else if (action === 'verificarCupon') resultado = verificarCupon(data);
    else resultado = { ok: false, error: 'Acción desconocida' };
  } catch (err) {
    resultado = { ok: false, error: err.message };
  }
  return ContentService
    .createTextOutput(JSON.stringify(resultado))
    .setMimeType(ContentService.MimeType.JSON);
}

// ── RECORDS ──────────────────────────────────────────────────
function getHoja() {
  const ss   = SpreadsheetApp.getActiveSpreadsheet();
  let hoja   = ss.getSheetByName(HOJA_RECORDS);
  if (!hoja) {
    hoja = ss.insertSheet(HOJA_RECORDS);
    hoja.appendRow(['Juego','Iniciales','Puntaje','Detalle','Fecha']);
  }
  return hoja;
}

function guardarRecord(data) {
  const juego     = (data.juego     || 'general').toString().slice(0, 30);
  const iniciales = (data.iniciales || '???').toString().toUpperCase().slice(0, 3);
  const puntaje   = Number(data.puntaje) || 0;
  const detalle   = (data.detalle   || '').toString().slice(0, 100);
  getHoja().appendRow([juego, iniciales, puntaje, detalle, new Date()]);
  return { ok: true };
}

function obtenerRecords(data) {
  const juego = (data.juego || 'general').toString();
  const filas = getHoja().getDataRange().getValues();
  filas.shift();
  const records = filas
    .filter(f => f[0] === juego)
    .map(f => ({ iniciales: f[1], puntaje: f[2], detalle: f[3], fecha: f[4] }))
    .sort((a, b) => b.puntaje - a.puntaje)
    .slice(0, TOP_N);
  return { ok: true, records };
}

// ── ERRORES ───────────────────────────────────────────────────
function getHojaErrores() {
  const ss   = SpreadsheetApp.getActiveSpreadsheet();
  let hoja   = ss.getSheetByName(HOJA_ERRORES);
  if (!hoja) {
    hoja = ss.insertSheet(HOJA_ERRORES);
    hoja.appendRow(['Juego','Operación','Detalle','Fecha']);
  }
  return hoja;
}

function guardarError(data) {
  const juego    = (data.juego    || 'general').toString().slice(0, 30);
  const operacion = (data.operacion || '').toString().slice(0, 30);
  const detalle  = (data.detalle  || '').toString().slice(0, 100);
  getHojaErrores().appendRow([juego, operacion, detalle, new Date()]);
  return { ok: true };
}

// ── CUPONES PS2 ───────────────────────────────────────────────
function getHojaCupones() {
  const ss   = SpreadsheetApp.getActiveSpreadsheet();
  let hoja   = ss.getSheetByName(HOJA_CUPONES);
  if (!hoja) {
    hoja = ss.insertSheet(HOJA_CUPONES);
    hoja.appendRow(['CODIGO','JUEGO','DESCUENTO','FECHA_GENERADO','NOMBRE','TELEFONO','FECHA_USADO','ESTADO']);
    hoja.getRange(1,1,1,8).setFontWeight('bold').setBackground('#c0392b').setFontColor('#ffffff');
    hoja.setColumnWidth(1, 120);
    hoja.setColumnWidth(3, 100);
    hoja.setColumnWidth(4, 160);
    hoja.setColumnWidth(7, 160);
  }
  return hoja;
}

// Registrar cupón ganado — lo llama el frontend al ganar
// data: { codigo, juego, descuento }
function registrarCupon(data) {
  const codigo    = (data.codigo    || '').toString().toUpperCase().slice(0, 12);
  const juego     = (data.juego     || 'ps2').toString().slice(0, 30);
  const descuento = Number(data.descuento) || DESCUENTO_PEN;

  if (!codigo) return { ok: false, error: 'Código vacío' };

  const hoja = getHojaCupones();

  // Verificar que no exista ya ese código
  const filas = hoja.getDataRange().getValues();
  for (let i = 1; i < filas.length; i++) {
    if (filas[i][0] === codigo) return { ok: true, yaExiste: true };
  }

  hoja.appendRow([codigo, juego, '$' + descuento, new Date(), '', '', '', 'ACTIVO']);
  return { ok: true };
}

// Marcar cupón como usado cuando el cliente confirma el pedido
// data: { codigo, nombre, telefono }
function verificarCupon(data) {
  const codigo   = (data.codigo   || '').toString().toUpperCase().trim();
  const nombre   = (data.nombre   || '').toString();
  const telefono = (data.telefono || '').toString();

  if (!codigo) return { ok: false, error: 'Código vacío' };

  const hoja  = getHojaCupones();
  const filas = hoja.getDataRange().getValues();

  for (let i = 1; i < filas.length; i++) {
    if (filas[i][0] === codigo) {
      if (filas[i][7] === 'USADO') return { ok: false, error: 'Cupón ya utilizado' };
      // Marcar como usado
      hoja.getRange(i+1, 5).setValue(nombre);
      hoja.getRange(i+1, 6).setValue(telefono);
      hoja.getRange(i+1, 7).setValue(new Date());
      hoja.getRange(i+1, 8).setValue('USADO');
      return { ok: true, descuento: filas[i][2] };
    }
  }
  return { ok: false, error: 'Cupón no encontrado' };
}
