from pathlib import Path
APP = Path("/root/werkraum/tools/gesamtatlas_world/app.py")
text = APP.read_text(encoding="utf-8")

checks = {
    "container": '<div id="ansicht-zeitstrom" class="ansicht"><div id="zeitstrom-inhalt"></div></div>',
    "button": '<button disabled title="folgt später">Globus</button>',
    "wire": "document.getElementById('linse-zeitstrom').onclick = () => linseWechseln('zeitstrom');",
    "linsewechseln_body": "  if (name === 'zeitstrom') zeitstromLaden();\n}",
    "head_close": "::-webkit-scrollbar-thumb { background: rgba(192,64,0,0.35); border-radius: 3px; }\n</style>\n</head>",
}
for k, v in checks.items():
    n = text.count(v)
    print(k, ":", n)
    if n != 1:
        raise SystemExit(f"abbruch bei {k}")

# 1) Three.js aus cdnjs einbinden
text = text.replace(
    "::-webkit-scrollbar-thumb { background: rgba(192,64,0,0.35); border-radius: 3px; }\n</style>\n</head>",
    '::-webkit-scrollbar-thumb { background: rgba(192,64,0,0.35); border-radius: 3px; }\n'
    '  #globus-canvas { position:absolute; inset:0; width:100%; height:100%; display:block; }\n'
    '  #globus-labels { position:absolute; inset:0; pointer-events:none; overflow:hidden; }\n'
    '</style>\n'
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>\n</head>',
    1,
)

# 2) Container fuer die Globus-Ansicht
text = text.replace(
    '<div id="ansicht-zeitstrom" class="ansicht"><div id="zeitstrom-inhalt"></div></div>',
    '<div id="ansicht-zeitstrom" class="ansicht"><div id="zeitstrom-inhalt"></div></div>\n'
    '  <div id="ansicht-globus" class="ansicht"><canvas id="globus-canvas"></canvas>'
    '<div id="globus-labels"></div>'
    '<div id="globus-status" class="panel" style="position:absolute; bottom:12px; left:12px; padding:8px 12px; font-size:0.66rem; color:var(--text-faint);"></div>'
    '</div>',
    1,
)

# 3) Button aktivieren
text = text.replace(
    '<button disabled title="folgt später">Globus</button>',
    '<button id="linse-globus">Globus</button>',
    1,
)

# 4) linseWechseln() um globus erweitern
text = text.replace(
    "  if (name === 'zeitstrom') zeitstromLaden();\n}",
    "  if (name === 'zeitstrom') zeitstromLaden();\n  if (name === 'globus') globusLaden();\n}",
    1,
)

# 5) Klick-Handler + Globus-Renderer-JS registrieren
text = text.replace(
    "document.getElementById('linse-zeitstrom').onclick = () => linseWechseln('zeitstrom');",
    "document.getElementById('linse-zeitstrom').onclick = () => linseWechseln('zeitstrom');\n"
    "document.getElementById('linse-globus').onclick = () => linseWechseln('globus');",
    1,
)

GLOBUS_JS = '''
let globusGeladen = false;
let globusState = null;

async function globusLaden() {
  if (globusGeladen) return;
  globusGeladen = true;
  const statusEl = document.getElementById('globus-status');
  statusEl.textContent = 'Lade Cluster-Daten...';
  let daten;
  try {
    const r = await fetch('api/megavault/globus');
    daten = await r.json();
  } catch (e) {
    statusEl.textContent = 'Fehler beim Laden: ' + e;
    return;
  }
  if (!daten.ok) {
    statusEl.textContent = 'Fehler: ' + (daten.error || 'unbekannt');
    return;
  }
  statusEl.textContent = `${daten.gesamt_knoten.toLocaleString('de-DE')} Knoten gesamt · ${daten.gesamt_kanten.toLocaleString('de-DE')} Kanten gesamt · Stichprobe pro Cluster sichtbar`;
  globusRendern(daten);
}

function globusRendern(daten) {
  const canvas = document.getElementById('globus-canvas');
  const container = document.getElementById('ansicht-globus');
  const labelLayer = document.getElementById('globus-labels');
  const breite = container.clientWidth, hoehe = container.clientHeight;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(50, breite / hoehe, 0.1, 1000);
  camera.position.z = 6.2;
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setSize(breite, hoehe);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  // Basis-Kugel: duenne Wireframe-Andeutung, kein Foto-Globus (keine erfundene Erde-Textur)
  const kugelGeo = new THREE.SphereGeometry(2.4, 32, 24);
  const kugelMat = new THREE.MeshBasicMaterial({ color: 0x3a4048, wireframe: true, transparent: true, opacity: 0.25 });
  scene.add(new THREE.Mesh(kugelGeo, kugelMat));
  const kernGlow = new THREE.Mesh(new THREE.SphereGeometry(2.36, 32, 24), new THREE.MeshBasicMaterial({ color: 0x1a1d22, transparent: true, opacity: 0.55 }));
  scene.add(kernGlow);

  // Cluster als eigene Kalotten-Regionen ueber die Kugel verteilt (Fibonacci-Sphere
  // fuer die Clusterzentren, Knoten innerhalb jedes Clusters zufaellig um dessen
  // Zentrum gestreut). Groessere Cluster bekommen eine groessere Streuung.
  const anzahlCluster = daten.clusters.length;
  const clusterPunkte = [];
  const nodeIndex = {};

  daten.clusters.forEach((cluster, ci) => {
    // Fibonacci-Sphere-Verteilung fuer gleichmaessige Clusterzentren
    const golden = Math.PI * (3 - Math.sqrt(5));
    const y = 1 - (ci / Math.max(anzahlCluster - 1, 1)) * 2;
    const radiusXZ = Math.sqrt(1 - y * y);
    const theta = golden * ci;
    const zentrum = new THREE.Vector3(Math.cos(theta) * radiusXZ, y, Math.sin(theta) * radiusXZ).multiplyScalar(2.4);

    const streuung = 0.28 + Math.min(0.42, Math.log10(cluster.gesamt + 1) * 0.09);
    const farbe = new THREE.Color(cluster.farbe);
    const positionen = [];
    const farben = [];

    cluster.knoten.forEach(knoten => {
      const off = new THREE.Vector3((Math.random() - 0.5), (Math.random() - 0.5), (Math.random() - 0.5)).multiplyScalar(streuung);
      const p = zentrum.clone().add(off).normalize().multiplyScalar(2.4 + Math.random() * 0.12);
      positionen.push(p.x, p.y, p.z);
      farben.push(farbe.r, farbe.g, farbe.b);
      nodeIndex[positionen.length / 3 - 1 + '|' + ci] = knoten;
    });

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(positionen, 3));
    geo.setAttribute('color', new THREE.Float32BufferAttribute(farben, 3));
    const mat = new THREE.PointsMaterial({ size: 0.045, vertexColors: true, transparent: true, opacity: 0.92, sizeAttenuation: true });
    const punkte = new THREE.Points(geo, mat);
    scene.add(punkte);

    clusterPunkte.push({ cluster, zentrum, ci });
  });

  // Cluster-Labels als HTML-Overlay, jeden Frame per 3D->2D-Projektion neu positioniert
  const labelElemente = clusterPunkte.map(cp => {
    const el = document.createElement('div');
    el.className = 'globus-label';
    el.style.cssText = 'position:absolute; transform: translate(-50%,-50%); font-size:0.72rem; color:' + cp.cluster.farbe + '; text-shadow: 0 0 6px rgba(0,0,0,0.9), 0 0 2px rgba(0,0,0,0.9); white-space:nowrap; pointer-events:none; font-weight:600;';
    el.textContent = cp.cluster.label + ' · ' + cp.cluster.gesamt.toLocaleString('de-DE');
    labelLayer.appendChild(el);
    return el;
  });

  let rotY = 0, rotX = 0.15;
  let ziehen = false, letzterX = 0, letzterY = 0;
  canvas.addEventListener('mousedown', e => { ziehen = true; letzterX = e.clientX; letzterY = e.clientY; });
  window.addEventListener('mouseup', () => ziehen = false);
  window.addEventListener('mousemove', e => {
    if (!ziehen) return;
    rotY += (e.clientX - letzterX) * 0.005;
    rotX += (e.clientY - letzterY) * 0.005;
    rotX = Math.max(-1.3, Math.min(1.3, rotX));
    letzterX = e.clientX; letzterY = e.clientY;
  });
  canvas.addEventListener('wheel', e => {
    camera.position.z = Math.max(3.2, Math.min(14, camera.position.z + e.deltaY * 0.003));
  }, { passive: true });

  function animieren() {
    requestAnimationFrame(animieren);
    if (!ziehen) rotY += 0.0009;
    scene.rotation.y = rotY;
    scene.rotation.x = rotX;
    renderer.render(scene, camera);

    clusterPunkte.forEach((cp, i) => {
      const weltpos = cp.zentrum.clone().applyMatrix4(scene.matrixWorld);
      const projiziert = weltpos.clone().project(camera);
      const sichtbar = projiziert.z < 1;
      const el = labelElemente[i];
      if (!sichtbar) { el.style.display = 'none'; return; }
      el.style.display = 'block';
      el.style.left = ((projiziert.x * 0.5 + 0.5) * breite) + 'px';
      el.style.top = ((-projiziert.y * 0.5 + 0.5) * hoehe) + 'px';
      el.style.opacity = projiziert.z < -0.3 ? '1' : '0.55';
    });
  }
  animieren();

  window.addEventListener('resize', () => {
    if (!document.getElementById('ansicht-globus').classList.contains('aktiv')) return;
    const b = container.clientWidth, h = container.clientHeight;
    camera.aspect = b / h; camera.updateProjectionMatrix();
    renderer.setSize(b, h);
  });

  globusState = { scene, camera, renderer };
}
'''

# JS-Funktion direkt vor linseWechseln einfuegen
text = text.replace("function linseWechseln(name) {", GLOBUS_JS + "\nfunction linseWechseln(name) {", 1)

APP.write_text(text, encoding="utf-8")
print("GLOBUS-FRONTEND EINGEFUEGT")
