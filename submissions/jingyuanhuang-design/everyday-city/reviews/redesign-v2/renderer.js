/* XCITY AI Competition - offline 3D scene of one submission.
 * Built by scripts/make_scene.py from the package's own geometry. Uses three.js r147 (MIT), inlined.
 * Coordinates: metres, x = east, z = -north, y = up, origin at the master area.
 * window.XC.render(viewId, width, height) returns a PNG data URL (used by scripts/render_views.py).
 * Entourage (trees, people, vehicles, PV tables) is generated from the geometry to show scale and use; it is not evidence.
 */
(function () {
  'use strict';
  const D = window.XCITY_SCENE;
  const T = THREE;
  const deg = T.MathUtils.degToRad;

  // ------------------------------------------------------------------ helpers
  function rng(seed) { let s = seed >>> 0; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  const R = rng(D.seed || 7);

  function grid(G) {
    const bin = atob(G.heights_b64), u8 = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
    G.v = new Int16Array(u8.buffer); return G;
  }
  const TH = grid(D.terrain), TN = grid(D.terrain_near);
  function sample(G, x, y) {
    const fx = (x - G.x0) / (G.x1 - G.x0) * (G.w - 1), fy = (G.y1 - y) / (G.y1 - G.y0) * (G.h - 1);
    const i = Math.max(0, Math.min(G.w - 2, Math.floor(fx))), j = Math.max(0, Math.min(G.h - 2, Math.floor(fy)));
    const a = Math.min(1, Math.max(0, fx - i)), b = Math.min(1, Math.max(0, fy - j));
    const g = (ii, jj) => G.v[jj * G.w + ii] / 10;
    return (g(i, j) * (1 - a) + g(i + 1, j) * a) * (1 - b) + (g(i, j + 1) * (1 - a) + g(i + 1, j + 1) * a) * b;
  }
  function hAt(x, y) {
    if (x > TN.x0 && x < TN.x1 && y > TN.y0 && y < TN.y1) return sample(TN, x, y);
    return sample(TH, x, y);
  }

  // merge simple parts into one geometry with vertex colours
  function mergeParts(parts) {
    const pos = [], nrm = [], col = [];
    parts.forEach(pt => {
      let g = pt.geom.index ? pt.geom.toNonIndexed() : pt.geom.clone();
      if (pt.matrix) g.applyMatrix4(pt.matrix);
      const p = g.attributes.position.array, n = g.attributes.normal.array, c = new T.Color(pt.color === undefined ? 0xffffff : pt.color);
      for (let i = 0; i < p.length; i++) { pos.push(p[i]); nrm.push(n[i]); }
      for (let i = 0; i < p.length / 3; i++) col.push(c.r, c.g, c.b);
    });
    const g = new T.BufferGeometry();
    g.setAttribute('position', new T.Float32BufferAttribute(pos, 3));
    g.setAttribute('normal', new T.Float32BufferAttribute(nrm, 3));
    g.setAttribute('color', new T.Float32BufferAttribute(col, 3));
    return g;
  }
  const M4 = (x, y, z, sx, sy, sz, rx, ry, rz) => new T.Matrix4().compose(new T.Vector3(x, y, z),
    new T.Quaternion().setFromEuler(new T.Euler(rx || 0, ry || 0, rz || 0)), new T.Vector3(sx || 1, sy || 1, sz || 1));

  // ------------------------------------------------------------------ procedural textures
  function canvasTex(w, h, draw, repeat, srgb) {
    const c = document.createElement('canvas'); c.width = w; c.height = h;
    const g = c.getContext('2d'); draw(g, w, h);
    const t = new T.CanvasTexture(c); t.wrapS = t.wrapT = T.RepeatWrapping;
    if (srgb !== false) t.encoding = T.sRGBEncoding;
    t.anisotropy = 8; if (repeat) t.repeat.set(repeat[0], repeat[1]); return t;
  }
  function noise(g, w, h, base, amp, n) {
    g.fillStyle = base; g.fillRect(0, 0, w, h);
    for (let i = 0; i < n; i++) {
      const v = (R() - 0.5) * amp; g.fillStyle = v > 0 ? `rgba(255,248,235,${v})` : `rgba(70,50,30,${-v})`;
      const s = 1 + R() * 3; g.fillRect(R() * w, R() * h, s, s);
    }
  }
  function windowAt(g, x0, y0, ww, wh, frame, shutter) {
    g.fillStyle = 'rgba(0,0,0,0.22)'; g.fillRect(x0 - 3, y0 - 3, ww + 6, wh + 6);
    const gr = g.createLinearGradient(0, y0, 0, y0 + wh); gr.addColorStop(0, '#8696a3'); gr.addColorStop(0.45, '#4d5a66'); gr.addColorStop(1, '#2f3942');
    g.fillStyle = gr; g.fillRect(x0, y0, ww, wh);
    g.fillStyle = frame; g.fillRect(x0 + ww / 2 - 1.5, y0, 3, wh); g.fillRect(x0, y0 + wh * 0.62, ww, 2);
    if (shutter) { g.fillStyle = shutter; g.fillRect(x0 - 13, y0, 10, wh); g.fillRect(x0 + ww + 3, y0, 10, wh);
      g.fillStyle = 'rgba(0,0,0,0.18)'; for (let y = y0 + 3; y < y0 + wh; y += 5) { g.fillRect(x0 - 13, y, 10, 1); g.fillRect(x0 + ww + 3, y, 10, 1); } }
    g.fillStyle = 'rgba(70,55,40,0.55)'; g.fillRect(x0 - 4, y0 + wh, ww + 8, 4);
  }
  function resFloor(g, oy, w, wall, shutter) {
    windowAt(g, (w - 46) / 2, oy + 36, 46, 66, 'rgba(235,228,214,0.95)', shutter);
    g.fillStyle = 'rgba(0,0,0,0.08)'; g.fillRect(0, oy + 136, w, 4);
  }
  function shopFloor(g, oy, w) {
    g.fillStyle = 'rgba(0,0,0,0.25)'; g.fillRect(10, oy + 24, w - 20, 116);
    const gr = g.createLinearGradient(0, oy + 28, 0, oy + 140); gr.addColorStop(0, '#9aa7b0'); gr.addColorStop(1, '#3a444c');
    g.fillStyle = gr; g.fillRect(14, oy + 28, w - 28, 112);
    g.fillStyle = 'rgba(240,232,215,0.95)'; g.fillRect(w / 2 - 2, oy + 28, 4, 112);
    g.fillStyle = '#9b5a36'; g.fillRect(6, oy + 12, w - 12, 12);          // awning band
  }
  function facadeTex(wall, kind, shutter) {
    if (kind === 'mixed') {          // ground-floor shops, three floors of homes above, repeating every 14 m
      return canvasTex(240, 560, (g, w, h) => {
        noise(g, w, h, wall, 0.07, 2400);
        for (let f = 0; f < 3; f++) resFloor(g, f * 140, w, wall, shutter);
        shopFloor(g, 420, w);
      }, [1 / 6, 1 / 14]);
    }
    return canvasTex(240, 140, (g, w, h) => {
      noise(g, w, h, wall, 0.07, 700);
      if (kind === 'blank') { g.fillStyle = 'rgba(0,0,0,0.07)'; for (let x = 0; x < w; x += 20) g.fillRect(x, 0, 2, h); g.fillStyle = 'rgba(0,0,0,0.12)'; g.fillRect(0, 0, w, 6); return; }
      if (kind === 'glass') { const gr = g.createLinearGradient(0, 14, 0, h - 10); gr.addColorStop(0, '#93a3ad'); gr.addColorStop(1, '#3c4852');
        g.fillStyle = gr; g.fillRect(8, 14, w - 16, h - 24); g.fillStyle = 'rgba(240,235,225,0.9)'; for (let x = 8; x < w; x += 46) g.fillRect(x, 14, 4, h - 24); g.fillRect(8, 14, w - 16, 4); return; }
      resFloor(g, 0, w, wall, shutter);
    }, [1 / 6, 1 / 3.5]);
  }
  const TEX = {
    sand: canvasTex(512, 512, (g, w, h) => noise(g, w, h, '#c2a37a', 0.26, 30000), [1 / 30, 1 / 30]),
    soil: canvasTex(256, 256, (g, w, h) => { noise(g, w, h, '#a98b67', 0.2, 6000); g.fillStyle = 'rgba(70,50,30,0.16)'; for (let y = 0; y < h; y += 16) g.fillRect(0, y, w, 4); }, [1 / 24, 1 / 24]),
    asphalt: canvasTex(256, 256, (g, w, h) => noise(g, w, h, '#58595c', 0.22, 9000), [1 / 10, 1 / 10]),
    paving: canvasTex(256, 256, (g, w, h) => { noise(g, w, h, '#d9ccb4', 0.12, 4000); g.strokeStyle = 'rgba(110,85,60,0.28)'; g.lineWidth = 1.5; for (let i = 0; i <= w; i += 32) { g.beginPath(); g.moveTo(i, 0); g.lineTo(i, h); g.stroke(); g.beginPath(); g.moveTo(0, i); g.lineTo(w, i); g.stroke(); } }, [1 / 6, 1 / 6]),
    pavers: canvasTex(256, 256, (g, w, h) => { noise(g, w, h, '#c4a682', 0.14, 4000); g.strokeStyle = 'rgba(90,65,40,0.32)'; for (let y = 0; y < h; y += 16) { const o = (y / 16) % 2 ? 16 : 0; for (let x = -16 + o; x < w; x += 32) g.strokeRect(x, y, 32, 16); } }, [1 / 4, 1 / 4]),
    gravel: canvasTex(256, 256, (g, w, h) => noise(g, w, h, '#c5b293', 0.32, 14000), [1 / 10, 1 / 10]),
    dirt: canvasTex(256, 256, (g, w, h) => noise(g, w, h, '#b9a07c', 0.25, 9000), [1 / 12, 1 / 12]),
    pv: canvasTex(128, 128, (g, w, h) => { g.fillStyle = '#18202c'; g.fillRect(0, 0, w, h); g.strokeStyle = 'rgba(170,190,215,0.35)'; g.lineWidth = 1; for (let i = 0; i <= w; i += 16) { g.beginPath(); g.moveTo(i, 0); g.lineTo(i, h); g.stroke(); g.beginPath(); g.moveTo(0, i); g.lineTo(w, i); g.stroke(); } }, [1 / 2, 1 / 2]),
    roof: canvasTex(256, 256, (g, w, h) => noise(g, w, h, '#c9bba3', 0.12, 5000), [1 / 16, 1 / 16]),
  };
  const FAC = {
    residential: facadeTex('#ece2d0', 'res', 'rgba(150,104,62,0.95)'),
    mixed_use: facadeTex('#e2cba6', 'mixed', 'rgba(120,96,70,0.95)'),
    civic: facadeTex('#c98f6c', 'glass'),
    compute: facadeTex('#c3c6c9', 'blank'),
    industry: facadeTex('#b9b7b0', 'blank'),
    logistics: facadeTex('#c2beb5', 'blank'),
    infrastructure: facadeTex('#cbc6bb', 'blank'),
    open_space: facadeTex('#cdb48d', 'blank'), energy: facadeTex('#cbc6bb', 'blank'),
  };
  function emisTex(kind) {
    if (kind === 'mixed') return canvasTex(240, 560, (g, w, h) => {
      g.fillStyle = '#000'; g.fillRect(0, 0, w, h);
      for (let f = 0; f < 3; f++) { g.fillStyle = R() < 0.6 ? '#ffd08e' : '#000'; g.fillRect((w - 46) / 2, f * 140 + 36, 46, 66); }
      g.fillStyle = '#ffd59a'; g.fillRect(14, 448, w - 28, 112);
    }, [1 / 6, 1 / 14]);
    return canvasTex(240, 140, (g, w, h) => {
      g.fillStyle = '#000'; g.fillRect(0, 0, w, h);
      if (kind === 'glass') { g.fillStyle = '#ffd59a'; g.fillRect(8, 14, w - 16, h - 24); return; }
      g.fillStyle = '#ffd08e'; g.fillRect((w - 46) / 2, 36, 46, 66);
    }, [1 / 6, 1 / 3.5]);
  }
  const EMIS = { res: emisTex('res'), mixed: emisTex('mixed'), glass: emisTex('glass') };

  // ------------------------------------------------------------------ renderer and scene
  const renderer = new T.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true, logarithmicDepthBuffer: true });
  renderer.setPixelRatio(1);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = T.PCFSoftShadowMap;
  renderer.toneMapping = T.ACESFilmicToneMapping; renderer.toneMappingExposure = 0.6;
  renderer.outputEncoding = T.sRGBEncoding; renderer.physicallyCorrectLights = true;
  document.getElementById('view').appendChild(renderer.domElement);
  const scene = new T.Scene();
  const camera = new T.PerspectiveCamera(50, 1.6, 0.3, 150000);

  const sky = new T.Sky(); sky.scale.setScalar(120000); scene.add(sky);
  const su = sky.material.uniforms;
  su.turbidity.value = 4.5; su.rayleigh.value = 1.4; su.mieCoefficient.value = 0.005; su.mieDirectionalG.value = 0.8;
  const sunLight = new T.DirectionalLight(0xffffff, 3.5); sunLight.castShadow = true;
  sunLight.shadow.mapSize.set(4096, 4096); sunLight.shadow.bias = -0.0003; sunLight.shadow.normalBias = 0.4;
  scene.add(sunLight); scene.add(sunLight.target);
  const hemi = new T.HemisphereLight(0xd6e4f5, 0xa88a64, 0.5); scene.add(hemi);
  scene.fog = new T.FogExp2(0xdfe3e2, 0.000022);
  const pmrem = new T.PMREMGenerator(renderer);
  const ALLMATS = [];
  function std(o) { const m = new T.MeshStandardMaterial(o); ALLMATS.push(m); return m; }

  const NIGHT = [], WALLMATS = [];
  function setSun(az, el, night) {
    const phi = deg(90 - Math.max(el, -10)), theta = deg(az);
    const s = new T.Vector3(Math.sin(theta) * Math.sin(phi), Math.cos(phi), -Math.cos(theta) * Math.sin(phi));
    su.sunPosition.value.copy(s);
    const low = Math.max(0, Math.min(1, el / 30));
    sunLight.color.setRGB(1.0, 0.78 + 0.2 * low, 0.55 + 0.4 * low);
    sunLight.intensity = night ? 0.0 : 1.2 + 3.3 * low;
    hemi.intensity = night ? 0.03 : 0.25 + 0.3 * low;
    renderer.toneMappingExposure = night ? 1.1 : (low < 0.3 ? 0.75 : 0.6);
    scene.fog.color.set(night ? 0x0c1320 : (low < 0.3 ? 0xe6c7a2 : 0xdfe3e2));
    scene.fog.density = night ? 0.00004 : 0.000022;
    sky.visible = !night;
    scene.environment = night ? null : pmrem.fromScene(sky, 0, 0.1, 150000).texture;
    scene.background = night ? new T.Color(0x0a1220) : null;
    ALLMATS.forEach(m => { m.envMapIntensity = 0.4; });
    NIGHT.forEach(o => o.visible = !!night);
    WALLMATS.forEach(m => { m.emissiveIntensity = night ? 1.6 : (low < 0.3 ? 0.35 : 0.0); });
  }

  // ------------------------------------------------------------------ terrain (far + near)
  function terrainMesh(x0, y0, x1, y1, nx, ny, mat, drop) {
    const g = new T.PlaneGeometry(x1 - x0, y1 - y0, nx, ny);
    g.rotateX(-Math.PI / 2); g.translate((x0 + x1) / 2, 0, -(y0 + y1) / 2);
    const p = g.attributes.position, col = new Float32Array(p.count * 3);
    for (let i = 0; i < p.count; i++) {
      const x = p.getX(i), y = -p.getZ(i); let h = hAt(x, y);
      if (drop && drop(x, y)) h -= 4;
      p.setY(i, h);
    }
    g.computeVertexNormals();
    const n = g.attributes.normal;
    for (let i = 0; i < p.count; i++) { const k = 0.8 + 0.2 * n.getY(i) + (R() - 0.5) * 0.05; col[i * 3] = k; col[i * 3 + 1] = k * 0.96; col[i * 3 + 2] = k * 0.9; }
    g.setAttribute('color', new T.BufferAttribute(col, 3));
    g.setAttribute('uv', new T.BufferAttribute(new Float32Array(p.count * 2).map((v, k) => k % 2 ? -p.getZ(k >> 1) : p.getX(k >> 1)), 2));
    const m = new T.Mesh(g, mat); m.receiveShadow = true; return m;
  }
  const N = D.near;
  const terrainMat = std({ map: TEX.sand, roughness: 1, vertexColors: true });
  scene.add(terrainMesh(TH.x0, TH.y0, TH.x1, TH.y1, Math.min(300, TH.w - 1), Math.min(300, TH.h - 1), terrainMat,
    (x, y) => x > N[0] + 250 && x < N[2] - 250 && y > N[1] + 250 && y < N[3] - 250));
  scene.add(terrainMesh(N[0], N[1], N[2], N[3], Math.round((N[2] - N[0]) / 30), Math.round((N[3] - N[1]) / 30), terrainMat));

  // ------------------------------------------------------------------ flat layers draped on the ground
  function shapeOf(poly) {
    const s = new T.Shape(poly.outer.map(q => new T.Vector2(q[0], q[1])));
    (poly.holes || []).forEach(h => s.holes.push(new T.Path(h.map(q => new T.Vector2(q[0], q[1])))));
    return s;
  }
  const BUCKET = new Map();       // material -> {pos:[], uv:[]}
  function addTri(mat, a, b, c, lift, maxLen) {
    const d = (u, v) => Math.hypot(u[0] - v[0], u[1] - v[1]);
    const stack = [[a, b, c]]; const B = BUCKET.get(mat) || { pos: [], uv: [] }; BUCKET.set(mat, B);
    let guard = 0;
    while (stack.length && guard++ < 200000) {
      const [p, q, r] = stack.pop();
      const pq = d(p, q), qr = d(q, r), rp = d(r, p), m = Math.max(pq, qr, rp);
      if (m <= maxLen) {
        [p, q, r].forEach(v => { B.pos.push(v[0], hAt(v[0], v[1]) + lift, -v[1]); B.uv.push(v[0], v[1]); });
        continue;
      }
      const mid = (u, v) => [(u[0] + v[0]) / 2, (u[1] + v[1]) / 2];
      if (m === pq) { const k = mid(p, q); stack.push([p, k, r], [k, q, r]); }
      else if (m === qr) { const k = mid(q, r); stack.push([p, q, k], [p, k, r]); }
      else { const k = mid(r, p); stack.push([p, q, k], [k, q, r]); }
    }
  }
  function flat(poly, mat, lift, maxLen) {
    const g = new T.ShapeGeometry(shapeOf(poly)), p = g.attributes.position, idx = g.index;
    const v = i => [p.getX(i), p.getY(i)];
    for (let k = 0; k < idx.count; k += 3) {
      // ShapeGeometry winds counter-clockwise in xy; after mapping y -> -z the face points up
      addTri(mat, v(idx.getX(k)), v(idx.getX(k + 1)), v(idx.getX(k + 2)), lift, maxLen || 24);
    }
    g.dispose();
  }
  function flushFlat() {
    BUCKET.forEach((B, mat) => {
      const g = new T.BufferGeometry();
      g.setAttribute('position', new T.Float32BufferAttribute(B.pos, 3));
      g.setAttribute('uv', new T.Float32BufferAttribute(B.uv, 2));
      g.computeVertexNormals();
      const m = new T.Mesh(g, mat); m.receiveShadow = true; scene.add(m);
    });
    BUCKET.clear();
  }
  const GROUND = {
    open_space: std({ map: TEX.dirt, color: 0xf0e2c8, roughness: 1 }),
    agriculture: std({ map: TEX.soil, roughness: 1 }),
    reserve: std({ map: TEX.sand, color: 0xf5ead8, roughness: 1 }),
    plaza: std({ map: TEX.paving, roughness: 0.92 }),
    residential: std({ map: TEX.pavers, color: 0xf2e4d0, roughness: 0.95 }),
    mixed_use: std({ map: TEX.paving, roughness: 0.92 }),
    civic: std({ map: TEX.paving, color: 0xf6e6d6, roughness: 0.92 }),
    compute: std({ map: TEX.gravel, color: 0xe2ddd3, roughness: 1 }),
    industry: std({ map: TEX.gravel, color: 0xddd6ca, roughness: 1 }),
    logistics: std({ map: TEX.asphalt, color: 0xb8b8b8, roughness: 1 }),
    infrastructure: std({ map: TEX.gravel, color: 0xe0d9cc, roughness: 1 }),
    energy: std({ map: TEX.gravel, color: 0xe9dfcc, roughness: 1 }),
  };
  D.ground.forEach(gr => { if (gr.use !== 'reserve') flat(gr, gr.plaza ? GROUND.plaza : (GROUND[gr.use] || GROUND.open_space), 0.06, gr.use === 'energy' || gr.use === 'agriculture' ? 40 : 24); });
  const WASH = std({ map: TEX.gravel, color: 0xb5a693, roughness: 1 });
  (D.crop_bands || []).forEach(gr => flat(gr, new T.MeshStandardMaterial({color: gr.species === 'forage' ? 0x7d9258 : 0x9a876a, roughness:1}), .10, 10));
  D.washes.forEach(w => flat(w, WASH, 0.04, 40));
  const ROAD = { machine: std({ map: TEX.asphalt, roughness: 0.85 }),
                 people: std({ map: TEX.paving, roughness: 0.9 }),
                 shared: std({ map: TEX.pavers, roughness: 0.9 }),
                 table: std({ color: 0xe9dcc4, roughness: 0.9 }) };
  D.roads.forEach(r => flat(r, ROAD[r.net] || ROAD.people, r.net === 'machine' ? 0.12 : 0.16, 20));
  D.tables.forEach(r => flat(r, ROAD.table, 0.24, 10));
  // acequias: narrow open channels of water along the shaded streets
  const WATER = new T.MeshStandardMaterial({ color: 0x3f5a63, roughness: 0.08, metalness: 0.0 }); ALLMATS.push(WATER);
  D.acequias.forEach(r => flat(r, WATER, 0.2, 12));
  flushFlat();

  // ------------------------------------------------------------------ buildings, merged per material
  const roofMat = std({ map: TEX.roof, roughness: 0.95 });
  const glassMat = new T.MeshStandardMaterial({ color: 0xe6f2ef, roughness: 0.12, metalness: 0.1, transparent: true, opacity: 0.55 });
  const glassRoof = new T.MeshStandardMaterial({ color: 0xf1f6f3, roughness: 0.18, metalness: 0.05, transparent: true, opacity: 0.62 });
  const pvMat = std({ map: TEX.pv, roughness: 0.3, metalness: 0.35 });
  const underMat = std({ color: 0xefe6d6, roughness: 0.85 });
  const postMat = std({ color: 0x8a8681, roughness: 0.6, metalness: 0.4 });
  function wallMat(b) {
    const t = FAC[b.use] || FAC.infrastructure;
    const m = std({ map: t, roughness: 0.92 });
    if (['residential', 'mixed_use', 'civic'].includes(b.use)) {
      m.emissiveMap = b.use === 'civic' ? EMIS.glass : (b.use === 'mixed_use' ? EMIS.mixed : EMIS.res);
      m.emissive = new T.Color(0xffffff); m.emissiveIntensity = 0; WALLMATS.push(m);
    }
    return m;
  }
  const BB = new Map();   // material -> {pos, nrm, uv}
  function bucket(mat) { let b = BB.get(mat); if (!b) { b = { pos: [], nrm: [], uv: [] }; BB.set(mat, b); } return b; }
  const matCache = {}, roofPV = [], posts = [];
  D.buildings.forEach(b => {
    const hs = b.outer.map(q => hAt(q[0], q[1]));
    const base = Math.max(...hs) - 0.3;
    if (b.form === 'canopy') {
      const g = new T.ExtrudeGeometry(shapeOf(b), { depth: 0.4, bevelEnabled: false });
      g.rotateX(-Math.PI / 2); g.translate(0, base + b.h - 0.4, 0);
      const m = new T.Mesh(g, [b.pv ? pvMat : roofMat, underMat]); m.castShadow = true; m.receiveShadow = true; scene.add(m);
      b.posts.forEach(q => { const hq = hAt(q[0], q[1]); posts.push([q[0], q[1], hq, base + b.h - hq]); });
      return;
    }
    const g = new T.ExtrudeGeometry(shapeOf(b), { depth: b.h + 0.3, bevelEnabled: false }).toNonIndexed();
    g.rotateX(-Math.PI / 2); g.translate(0, base, 0); g.computeVertexNormals();
    let wall, roof;
    if (b.use === 'agriculture') { wall = glassMat; roof = glassRoof; }
    else { const k = b.use; matCache[k] = matCache[k] || wallMat(b); wall = matCache[k]; roof = roofMat; }
    const pos = g.attributes.position, nrm = g.attributes.normal;
    for (let i = 0; i < pos.count; i++) {
      const side = Math.abs(nrm.getY(i)) < 0.5, B = bucket(side ? wall : roof);
      B.pos.push(pos.getX(i), pos.getY(i), pos.getZ(i)); B.nrm.push(nrm.getX(i), nrm.getY(i), nrm.getZ(i));
      if (side) { const along = Math.abs(nrm.getX(i)) > Math.abs(nrm.getZ(i)) ? -pos.getZ(i) : pos.getX(i); B.uv.push(along, pos.getY(i) - base - 0.3); }
      else B.uv.push(pos.getX(i), -pos.getZ(i));
    }
    g.dispose();
    if (b.roof_pv) {
      const xs = b.outer.map(q => q[0]), ys = b.outer.map(q => q[1]);
      const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
      roofPV.push([(x0 + x1) / 2, (y0 + y1) / 2, base + b.h + 0.65, (x1 - x0) * 0.78, (y1 - y0) * 0.72]);
    }
  });
  BB.forEach((B, mat) => {
    const g = new T.BufferGeometry();
    g.setAttribute('position', new T.Float32BufferAttribute(B.pos, 3));
    g.setAttribute('normal', new T.Float32BufferAttribute(B.nrm, 3));
    g.setAttribute('uv', new T.Float32BufferAttribute(B.uv, 2));
    const m = new T.Mesh(g, mat); m.castShadow = true; m.receiveShadow = true; scene.add(m);
  });

  // ------------------------------------------------------------------ instanced entourage
  function instanced(geom, mat, items, place, shadow, colorOf) {
    if (!items.length) return null;
    const im = new T.InstancedMesh(geom, mat, items.length);
    const M = new T.Matrix4(), q = new T.Quaternion(), s = new T.Vector3(), p = new T.Vector3(), c = new T.Color();
    items.forEach((it, i) => { place(it, p, q, s); M.compose(p, q, s); im.setMatrixAt(i, M); if (colorOf) im.setColorAt(i, c.set(colorOf(it, i))); });
    im.castShadow = shadow !== false; im.receiveShadow = true; scene.add(im); return im;
  }
  const up = new T.Vector3(0, 1, 0);
  instanced(new T.BoxGeometry(1, 0.35, 1), pvMat, roofPV, (r, p, q, s) => { p.set(r[0], r[2], -r[1]); q.setFromAxisAngle(new T.Vector3(1, 0, 0), deg(-8)); s.set(r[3], 1, r[4]); });
  instanced(new T.CylinderGeometry(0.11, 0.11, 1, 8), postMat, posts, (r, p, q, s) => { p.set(r[0], r[2] + r[3] / 2, -r[1]); q.identity(); s.set(1, r[3], 1); });
  // PV tables: single-axis trackers, rows north-south
  const pvRows = D.pv_rows, tilt = deg(D.pv_tilt || 20);
  const pvq = new T.Quaternion().setFromEuler(new T.Euler(-tilt, Math.PI / 2, 0));
  instanced(new T.BoxGeometry(4, 0.06, 1), pvMat, pvRows, (r, p, q, s) => { p.set(r[0], hAt(r[0], r[1]) + (r[3] || 1.7), -r[1]); q.copy(pvq); s.set(1, 1, r[2]); });
  instanced(new T.BoxGeometry(0.1, 1, 0.1), postMat, pvRows, (r, p, q, s) => { p.set(r[0], hAt(r[0], r[1]) + (r[3] || 1.7) / 2, -r[1]); q.identity(); s.set(1, (r[3] || 1.7), r[2]); }, false);

  instanced(new T.IcosahedronGeometry(1,1), new T.MeshStandardMaterial({color:0x77805b,roughness:1}), D.jojoba || [], (r,p,q,s)=>{p.set(r[0],hAt(r[0],r[1])+.6,-r[1]);q.identity();s.set(1,.6,1);});
  // trees: 0 broad (algarrobo), 1 poplar (windbreaks), 2 olive (orchards); t = [x, y, size, rot, type]
  const ico = (r, d) => new T.IcosahedronGeometry(r, d);
  const crownBroad = mergeParts([
    { geom: ico(1, 1), matrix: M4(0, 0, 0, 1.15, 0.62, 1.1) }, { geom: ico(0.8, 1), matrix: M4(0.75, 0.05, 0.3, 1, 0.65, 1) },
    { geom: ico(0.8, 1), matrix: M4(-0.65, 0.0, -0.4, 1, 0.6, 1) }, { geom: ico(0.7, 1), matrix: M4(0.1, 0.3, -0.6, 1, 0.65, 1) },
    { geom: ico(0.7, 1), matrix: M4(-0.3, 0.25, 0.7, 1, 0.6, 1) }]);
  const crownPoplar = mergeParts([{ geom: ico(1, 1), matrix: M4(0, 0, 0, 1, 4.2, 1) }, { geom: ico(0.7, 1), matrix: M4(0.2, 1.8, 0.1, 1, 2.5, 1) }]);
  const crownOlive = mergeParts([{ geom: ico(1, 1), matrix: M4(0, 0, 0, 1.1, 0.8, 1.1) }, { geom: ico(0.7, 0), matrix: M4(0.5, 0.2, 0.3) }]);
  const crownMat = std({ vertexColors: false, roughness: 1, flatShading: true });
  const trunkMat = std({ color: 0x5b4636, roughness: 1 });
  const TR = [[], [], []]; D.trees.forEach(t => TR[t[4] || 0].push(t));
  const green = { 0: [0x6b7a3e, 0x7d8a48, 0x5f6e38, 0x86904f], 1: [0x6c8a3a, 0x7a9442, 0x5e7a33], 2: [0x8c9873, 0x95a07c, 0x7f8c68] };
  // trunk heights per type: broad 2.4 m, poplar 3 m, olive 1.2 m (times size)
  const TH_ = [3.4, 3.0, 1.3], CR = [crownBroad, crownPoplar, crownOlive], CRS = [2.5, 1.3, 1.4], CRY = [4.9, 7.2, 2.3];
  for (let k = 0; k < 3; k++) {
    if (!TR[k].length) continue;
    instanced(new T.CylinderGeometry(0.14, 0.24, 1, 6), trunkMat, TR[k], (t, p, q, s) => { const h = TH_[k] * t[2]; p.set(t[0], hAt(t[0], t[1]) + h / 2, -t[1]); q.identity(); s.set(t[2], h, t[2]); });
    instanced(CR[k], crownMat, TR[k], (t, p, q, s) => { const r = CRS[k] * t[2]; p.set(t[0], hAt(t[0], t[1]) + CRY[k] * t[2], -t[1]); q.setFromAxisAngle(up, t[3] || 0); s.set(r, r, r); },
      true, (t, i) => green[k][i % green[k].length]);
  }
  instanced(ico(1, 0), std({ color: 0x8b8d5e, roughness: 1, flatShading: true }), D.shrubs, (t, p, q, s) => { p.set(t[0], hAt(t[0], t[1]) + 0.3 * t[2], -t[1]); q.setFromAxisAngle(up, t[0] % 6); s.set(0.9 * t[2], 0.5 * t[2], 0.9 * t[2]); });

  // people: clothing (instance colour) and body (fixed colours), two poses; pp = [x, y, heading, pose, colour, scale]
  function personParts(walk) {
    const a = walk ? deg(22) : 0;
    const body = [
      { geom: new T.BoxGeometry(0.13, 0.82, 0.15), matrix: M4(-0.09, 0.41, 0, 1, 1, 1, a, 0, 0), color: 0x2c2c33 },
      { geom: new T.BoxGeometry(0.13, 0.82, 0.15), matrix: M4(0.09, 0.41, 0, 1, 1, 1, -a, 0, 0), color: 0x2c2c33 },
      { geom: new T.SphereGeometry(0.115, 10, 8), matrix: M4(0, 1.62, 0), color: 0xb5876a },
      { geom: new T.SphereGeometry(0.12, 10, 6, 0, Math.PI * 2, 0, Math.PI / 2), matrix: M4(0, 1.645, -0.01), color: 0x2a2018 },
    ];
    const cloth = [
      { geom: new T.BoxGeometry(0.4, 0.62, 0.23), matrix: M4(0, 1.13, 0) },
      { geom: new T.BoxGeometry(0.1, 0.6, 0.12), matrix: M4(-0.26, 1.12, 0, 1, 1, 1, -a * 0.8, 0, 0) },
      { geom: new T.BoxGeometry(0.1, 0.6, 0.12), matrix: M4(0.26, 1.12, 0, 1, 1, 1, a * 0.8, 0, 0) },
    ];
    return [mergeParts(body), mergeParts(cloth)];
  }
  const POSE = [personParts(false), personParts(true)];
  const bodyMat = std({ vertexColors: true, roughness: 0.85 }), clothMat = std({ vertexColors: true, roughness: 0.9 });
  const CLOTH = [0xf2efe8, 0xc4552f, 0x2f4b6e, 0xd6a640, 0x3d3d3d, 0x6f8f5a, 0x9ec3d8, 0xa23b3b, 0xe8d6b5, 0x7b5a8c];
  for (let k = 0; k < 2; k++) {
    const sub = D.people.filter(pp => (pp[3] || 0) === k);
    const place = (pp, p, q, s) => { const sc = pp[5] || 1; p.set(pp[0], hAt(pp[0], pp[1]) + 0.2, -pp[1]); q.setFromAxisAngle(up, pp[2] || 0); s.set(sc, sc, sc); };
    instanced(POSE[k][0], bodyMat, sub, place);
    instanced(POSE[k][1], clothMat, sub, place, true, pp => CLOTH[(pp[4] || 0) % CLOTH.length]);
  }
  // delivery robots, driverless shuttles, freight
  const robotG = mergeParts([{ geom: new T.BoxGeometry(0.62, 0.5, 0.86), matrix: M4(0, 0.4, 0), color: 0xf4f4f1 },
    { geom: new T.BoxGeometry(0.64, 0.08, 0.88), matrix: M4(0, 0.68, 0), color: 0x2b2f36 },
    { geom: new T.BoxGeometry(0.66, 0.16, 0.9), matrix: M4(0, 0.12, 0), color: 0x30343a }]);
  instanced(robotG, std({ vertexColors: true, roughness: 0.5 }), D.robots, (r, p, q, s) => { p.set(r[0], hAt(r[0], r[1]) + 0.15, -r[1]); q.setFromAxisAngle(up, r[2]); s.set(1, 1, 1); });
  const shuttleG = mergeParts([{ geom: new T.BoxGeometry(2.3, 2.5, 7.5), matrix: M4(0, 1.6, 0), color: 0xf1f1ee },
    { geom: new T.BoxGeometry(2.34, 0.9, 7.2), matrix: M4(0, 2.0, 0), color: 0x24303a },
    { geom: new T.BoxGeometry(2.0, 0.35, 6.8), matrix: M4(0, 0.35, 0), color: 0x2a2a2a }]);
  const truckG = mergeParts([{ geom: new T.BoxGeometry(2.5, 3.0, 9.5), matrix: M4(0, 2.0, -1.5), color: 0xe8e6e0 },
    { geom: new T.BoxGeometry(2.4, 2.4, 2.4), matrix: M4(0, 1.7, 4.6), color: 0xd9dcdc },
    { geom: new T.BoxGeometry(2.42, 0.8, 0.2), matrix: M4(0, 2.2, 5.8), color: 0x1f262d },
    { geom: new T.BoxGeometry(2.2, 0.4, 11.5), matrix: M4(0, 0.4, 0), color: 0x2a2a2a }]);
  const vehMat = std({ vertexColors: true, roughness: 0.45, metalness: 0.1 });
  instanced(shuttleG, vehMat, D.trucks.filter(t => t[3] === 0), (r, p, q, s) => { p.set(r[0], hAt(r[0], r[1]) + 0.1, -r[1]); q.setFromAxisAngle(up, r[2]); s.set(1, 1, 1); });
  instanced(truckG, vehMat, D.trucks.filter(t => t[3] === 1), (r, p, q, s) => { p.set(r[0], hAt(r[0], r[1]) + 0.1, -r[1]); q.setFromAxisAngle(up, r[2]); s.set(1, 1, 1); });
  // street lamps; the heads glow at night
  instanced(new T.CylinderGeometry(0.06, 0.09, 4.6, 6), postMat, D.lamps, (l, p, q, s) => { p.set(l[0], hAt(l[0], l[1]) + 2.3, -l[1]); q.identity(); s.set(1, 1, 1); }, false);
  const lampHead = new T.MeshStandardMaterial({ color: 0x333333, emissive: new T.Color(0xffd29a), emissiveIntensity: 0 }); WALLMATS.push(lampHead);
  instanced(new T.BoxGeometry(0.5, 0.12, 0.3), lampHead, D.lamps, (l, p, q, s) => { p.set(l[0], hAt(l[0], l[1]) + 4.65, -l[1]); q.identity(); s.set(1, 1, 1); }, false);
  const pools = instanced(new T.CircleGeometry(7, 20).rotateX(-Math.PI / 2), new T.MeshBasicMaterial({ color: 0xffc98a, transparent: true, opacity: 0.2, depthWrite: false }), D.lamps, (l, p, q, s) => { p.set(l[0], hAt(l[0], l[1]) + 0.35, -l[1]); q.identity(); s.set(1, 1, 1); }, false);
  if (pools) NIGHT.push(pools);
  const moon = new T.DirectionalLight(0x8fa6d6, 0.25); moon.position.set(-3000, 4000, 2000); NIGHT.push(moon); scene.add(moon);
  const nightAmb = new T.AmbientLight(0x4a5a7a, 0.5); NIGHT.push(nightAmb); scene.add(nightAmb);

  // ------------------------------------------------------------------ views
  function fitShadow(target, radius) {
    const s = sunLight.shadow.camera; const r = Math.max(120, radius);
    s.left = -r; s.right = r; s.top = r; s.bottom = -r; s.near = 10; s.far = 20000; s.updateProjectionMatrix();
    sunLight.target.position.copy(target); sunLight.position.copy(target).add(su.sunPosition.value.clone().multiplyScalar(8000));
  }
  function applyView(v) {
    const sunv = D.suns[v.time] || D.suns.day;
    setSun(sunv.azimuth, sunv.elevation, v.time === 'night');
    camera.fov = v.fov; camera.position.set(v.pos[0], hAt(v.pos[0], v.pos[1]) + v.pos[2], -v.pos[1]);
    const tgt = new T.Vector3(v.target[0], hAt(v.target[0], v.target[1]) + v.target[2], -v.target[1]);
    camera.lookAt(tgt); camera.updateProjectionMatrix();
    fitShadow(tgt, v.shadow_radius || 700);
    if (window.CONTROLS) { CONTROLS.target.copy(tgt); CONTROLS.update(); }
    document.getElementById('cap').textContent = v.label + ' · ' + sunv.label;
  }
  function size(w, h) { renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); }
  window.XC = {
    views: D.views, scene, camera, hAt,
    render(id, w, h) {
      const v = D.views.find(x => x.id === id); size(w, h); applyView(v);
      renderer.render(scene, camera); return renderer.domElement.toDataURL('image/png');
    },
  };
  // interactive page
  const box = document.getElementById('view');
  function fit() { const w = box.clientWidth, h = box.clientHeight; renderer.setSize(w, h); camera.aspect = w / h; camera.updateProjectionMatrix(); }
  if (!new URLSearchParams(location.search).has('render')) {
    window.CONTROLS = new T.OrbitControls(camera, renderer.domElement);
    CONTROLS.maxPolarAngle = deg(89); CONTROLS.enableDamping = true;
    const bar = document.getElementById('views');
    D.views.forEach((v, i) => {
      const b = document.createElement('button'); b.textContent = v.label; b.onclick = () => { applyView(v); };
      bar.appendChild(b); if (i === 0) applyView(v);
    });
    const save = document.createElement('button'); save.textContent = 'Save PNG'; save.className = 'save';
    save.onclick = () => { renderer.render(scene, camera); const a = document.createElement('a'); a.href = renderer.domElement.toDataURL('image/png'); a.download = 'xcity-view.png'; a.click(); };
    bar.appendChild(save);
    window.addEventListener('resize', fit); fit();
    (function loop() { requestAnimationFrame(loop); CONTROLS.update(); renderer.render(scene, camera); })();
  }
  window.XC_READY = true;
})();
