/* UNIVERSE 69 — skinned humans for the headset viewer.
 *
 * Near people are drawn as real skinned bodies (CC0 Quaternius base
 * characters) moved by motion-captured-quality clips (CC0 Universal
 * Animation Library); far people stay on the instanced figures in vr.html.
 * The record decides everything: position, heading, activity, age, sex,
 * body mass, strength. This module never writes to it.
 *
 * Credits and licences: humans/CREDITS.md.
 */
import * as THREE from 'three';
import { GLTFLoader } from './addons/GLTFLoader.js';
import * as SkeletonUtils from './addons/SkeletonUtils.js';

const BASE = new URL('./humans/', import.meta.url).href;
const HAIR = { 0: ['simpleparted', 'buzzed'], 1: ['long', 'buns'] };
const HAIR_FILES = [...HAIR[0], ...HAIR[1], 'beard'];
// Fat settles on the belly in front, not evenly round the body.
const BELLY = { pelvis: .8, spine_01: 1, spine_02: .55 };

// Activity codes mirror the A table in vr.html.
const A = { WALK: 1, FORAGE: 2, HUNT: 3, FISH: 4, FARM: 5, BUILD: 6, TALK: 7,
  MATE: 8, BIRTH: 9, TEND: 10, REST: 11, EAT: 12, WITHDRAW: 13, FIGHT: 14,
  PLAY: 15, RITE: 16, SLEEP: 17, WORK: 18, SCOUT: 19, WATCH: 20, GROOM: 21, DRINK: 22 };

// What a still body is doing, by activity. Seated work is a squat: foragers
// sit on their heels, and the pen has no chairs a figure could be put on.
// Resting, eating, grooming, tending and withdrawing sit on the ground (SIT).
export const STILL_CLIP = {
  [A.FORAGE]: 'PickUp_Table', [A.HUNT]: 'Crouch_Idle_Loop', [A.FISH]: 'Crouch_Idle_Loop',
  [A.FARM]: 'Fixing_Kneeling', [A.BUILD]: 'Fixing_Kneeling', [A.WORK]: 'Fixing_Kneeling',
  [A.TALK]: 'Idle_Talking_Loop', [A.DRINK]: 'Crouch_Idle_Loop',
  [A.FIGHT]: 'Punch_Jab', [A.PLAY]: 'Dance_Loop',
  [A.RITE]: 'Dance_Loop', [A.SCOUT]: 'Idle_Loop',
};
const LYING = new Set([A.SLEEP, A.MATE, A.BIRTH]);
// Sitting on the ground: the library's seated clip with the knees and ankles
// returned to their straight rest pose, so the legs lie out in front.
const SIT = { [A.REST]: 'Sitting_Idle_Loop', [A.EAT]: 'Sitting_Idle_Loop',
  [A.TEND]: 'Sitting_Idle_Loop', [A.WITHDRAW]: 'Sitting_Idle_Loop',
  [A.GROOM]: 'Sitting_Talking_Loop' };
const SIT_CONTACTS = ['pelvis', 'thigh_l', 'thigh_r', 'calf_l', 'calf_r', 'foot_l', 'foot_r'];
const STRAIGHT = ['calf_l', 'calf_r', 'foot_l', 'foot_r'];
// The sleeper's curl, degrees about the body's left-right axis.
const CURL = [['spine_01', 12], ['spine_02', 10], ['neck_01', 12],
  ['thigh_l', -55], ['thigh_r', -40], ['calf_l', 75], ['calf_r', 60],
  ['upperarm_l', -45], ['upperarm_r', -35], ['lowerarm_l', -60], ['lowerarm_r', -70]];
const LYING_CONTACTS = ['pelvis', 'spine_02', 'spine_03', 'Head', 'thigh_l', 'thigh_r',
  'calf_l', 'calf_r', 'upperarm_l', 'upperarm_r', 'lowerarm_l', 'lowerarm_r'];
// Ground speed of each gait at model scale 1, measured from the clips' strides.
const GAIT = [['Walk_Loop', 1.3, 2.1], ['Jog_Fwd_Loop', 3.0, 4.6], ['Sprint_Loop', 6.0, Infinity]];

// Soft tissue follows the skin weights: fat gathers on the trunk, hips and
// upper limbs; muscle on the limbs, shoulders and chest. Weights per bone.
const FAT = { pelvis: 1, spine_01: 1, spine_02: .75, spine_03: .45, thigh: .7, calf: .25,
  upperarm: .45, lowerarm: .15, neck_01: .25, clavicle: .2 };
const MUSCLE = { upperarm: 1, lowerarm: .6, thigh: .85, calf: .6, spine_03: .55,
  clavicle: .6, neck_01: .35, spine_02: .2 };

function boneWeight(table, name) {
  const base = name.replace(/_(l|r)$/, '');
  return table[base] || 0;
}

let lib = null, loading = null;

export function loadHumans() {
  if (!loading) loading = load().then((l) => (lib = l)).catch((e) => {
    console.warn('humans: falling back to instanced figures', e);
    return null;
  });
  return loading;
}
export function humansReady() { return !!lib; }

async function load() {
  const gl = new GLTFLoader();
  const get = (f) => gl.loadAsync(BASE + f);
  const tex = new THREE.TextureLoader();
  const light = (f) => tex.loadAsync(BASE + f).then((t) => {
    t.colorSpace = THREE.SRGBColorSpace; t.flipY = false; return t; });
  const [male, female, anims, mLight, fLight, ...hair] = await Promise.all([
    get('male.glb'), get('female.glb'), get('anims.glb'),
    light('male_light.jpg'), light('female_light.jpg'),
    ...HAIR_FILES.map((h) => get('hair_' + h + '.glb'))]);
  const hairByName = {};
  HAIR_FILES.forEach((h, i) => {
    let mesh = null; hair[i].scene.traverse((o) => { if (o.isMesh && !mesh) mesh = o; });
    hairByName[h] = mesh;
  });
  return {
    sex: [prepare(male.scene, mLight), prepare(female.scene, fLight)],
    hair: hairByName,
    clips: prepareClips(anims.animations, anims.scene, male.scene),
  };
}

// Per-sex template: the body mesh with its soft-tissue masks, the bind pose
// of the head (hair is modelled in that space) and the garment geometry.
function prepare(scene, lightMap) {
  let body = null;
  scene.traverse((o) => {
    if (o.isSkinnedMesh && (!body || o.geometry.attributes.position.count >
        body.geometry.attributes.position.count)) body = o;
    if (o.isMesh) { o.castShadow = true; o.frustumCulled = false; }
  });
  const g = body.geometry, names = body.skeleton.bones.map((b) => b.name);
  const si = g.attributes.skinIndex, sw = g.attributes.skinWeight, n = si.count;
  const fat = new Float32Array(n), muscle = new Float32Array(n), belly = new Float32Array(n);
  for (let i = 0; i < n; i++) for (let k = 0; k < 4; k++) {
    const w = sw.getComponent(i, k), name = names[si.getComponent(i, k)];
    fat[i] += w * boneWeight(FAT, name);
    muscle[i] += w * boneWeight(MUSCLE, name);
    belly[i] += w * (BELLY[name] || 0);
  }
  g.setAttribute('aFat', new THREE.BufferAttribute(fat, 1));
  g.setAttribute('aMuscle', new THREE.BufferAttribute(muscle, 1));
  g.setAttribute('aBelly', new THREE.BufferAttribute(belly, 1));
  g.computeBoundingBox();
  scene.updateMatrixWorld(true);
  const head = scene.getObjectByName('Head');
  return {
    scene, body: body.name, height: g.boundingBox.max.y,
    darkMap: body.material.map, lightMap,
    headBindInverse: head.matrixWorld.clone().invert(),
    garments: garmentGeometries(g),
  };
}

// A garment is the body's own skin over a region, worn a few millimetres out,
// so it follows every pose and every body without a second rig. Regions are
// bands of the bind pose (y up, metres; |x| keeps the hanging arms out).
const GARMENT = {
  hide: [[0.86, 1.02, 0.24]],
  swimM: [[0.86, 1.02, 0.24]],
  swimF: [[0.82, 1.02, 0.24], [1.20, 1.37, 0.20]],
  fur: [[0.62, 1.47, 0.30]],
};
function garmentGeometries(g) {
  const pos = g.attributes.position, idx = g.index.array, out = {};
  for (const [kind, bands] of Object.entries(GARMENT)) {
    const inside = (v) => bands.some(([lo, hi, half]) => {
      const y = pos.getY(v), x = Math.abs(pos.getX(v));
      return y >= lo && y <= hi && x <= half;
    });
    const keep = [];
    for (let t = 0; t < idx.length; t += 3)
      if (inside(idx[t]) && inside(idx[t + 1]) && inside(idx[t + 2]))
        keep.push(idx[t], idx[t + 1], idx[t + 2]);
    const c = g.clone(); c.setIndex(keep);
    out[kind] = c;
  }
  return out;
}

// Rotations only: the library's skeleton and the bodies share bone names but
// not every length, so positional tracks would stretch limbs. The pelvis keeps
// its height track, rescaled, so squats and kneels still lower the body.
function prepareClips(clips, animScene, bodyScene) {
  const pa = animScene.getObjectByName('pelvis'), pb = bodyScene.getObjectByName('pelvis');
  const ratio = pb.position.length() / (pa.position.length() || 1);
  const out = {};
  clips.forEach((clip) => {
    const tracks = [];
    clip.tracks.forEach((t) => {
      if (t.name.endsWith('.quaternion')) tracks.push(t);
      else if (t.name === 'pelvis.position') {
        const c = t.clone();
        for (let i = 0; i < c.values.length; i++) c.values[i] *= ratio;
        tracks.push(c);
      }
    });
    out[clip.name] = new THREE.AnimationClip(clip.name, clip.duration, tracks);
  });
  return out;
}

function hash(id, salt) {
  let h = (id * 2654435761 + salt * 40503) >>> 0;
  h ^= h >>> 15; h = Math.imul(h, 2246822519) >>> 0; h ^= h >>> 13;
  return (h >>> 0) / 4294967296;
}

// Soft tissue displaces along the bind-pose normal before skinning, so a fat,
// starved or strong body moves exactly as the rig does.
function tissueMaterial(src, opts) {
  const m = src.clone();
  Object.assign(m, opts);
  m.userData.tissue = { uFat: { value: 0 }, uMuscle: { value: 0 }, uLift: { value: 0 } };
  m.onBeforeCompile = (shader) => {
    Object.assign(shader.uniforms, m.userData.tissue);
    shader.vertexShader = shader.vertexShader
      .replace('#include <common>', '#include <common>\nattribute float aFat;\nattribute float aMuscle;\nattribute float aBelly;\nuniform float uFat;\nuniform float uMuscle;\nuniform float uLift;')
      .replace('#include <begin_vertex>', '#include <begin_vertex>\ntransformed += normal * (uFat * aFat + uMuscle * aMuscle + uLift) + vec3(0., 0., 1.) * max(uFat, 0.) * 2.2 * aBelly * max(normal.z, 0.);');
  };
  m.customProgramCacheKey = () => 'u69-tissue';
  return m;
}

const AGE_BAND = [0, 1.5, 3, 6, 9, 12, 15, 18, 60];
const HEADS = [4.0, 4.5, 5.0, 6.0, 6.5, 7.0, 7.3, 7.6, 7.5];
const LEG_FRAC = [.38, .41, .44, .46, .48, .495, .51, .52, .515];
function band(age) {
  for (let i = AGE_BAND.length - 1; i > 0; i--) if (age >= AGE_BAND[i]) return i;
  return 0;
}

class Figure {
  constructor(a, look) {
    const T = lib.sex[a.sex === 1 ? 1 : 0];
    this.sex = a.sex === 1 ? 1 : 0;
    this.root = SkeletonUtils.clone(T.scene);
    this.T = T;
    this.mixer = new THREE.AnimationMixer(this.root);
    this.actions = {};
    this.clip = null;
    this.lift = null;
    this.bones = {};
    this.root.traverse((o) => { if (o.isBone) this.bones[o.name] = o; });
    this.rest = Object.fromEntries(STRAIGHT.map((n) => [n, this.bones[n].quaternion.clone()]));
    this.materials = [];
    let body = null;
    this.root.traverse((o) => {
      if (!o.isSkinnedMesh) return;
      if (o.name === T.body) body = o;
      const skinOpts = o.name === T.body ? this.skinOpts(a, look) : {};
      o.material = tissueMaterial(o.material, skinOpts);
      this.materials.push(o.material);
    });
    this.body = body;
    this.addHair(a, look);
    this.dress(look.dress, look);
    this.shape(a);
    // A gift party carries the exchange: a bound bundle at the hand, warm
    // outbound and a shade deeper homeward (2026.11.12.3/2026.11.12.5).
    if (a.gift) this.addBundle(a.gift);
    else this.addHeld(a);
  }

  // What the hands hold: a shaft with a tip (hunt, fish), a hoe's blade
  // (farm), a basket (forage), a load (build) — the 2D mapping, on the rig.
  addHeld(a) {
    const hand = this.bones.hand_r || this.bones.hand_l || this.bones.lowerarm_r;
    if (!hand) return;
    const isHand = /^hand/i.test(hand.name);
    const place = (g, mat, x, y, z) => {
      const m = new THREE.Mesh(g, mat);
      m.position.set(isHand ? x : x + 0.02, isHand ? y : y - 0.23, isHand ? z : z + 0.02);
      m.castShadow = true;
      hand.add(m);
      return m;
    };
    if (a.act === A.HUNT || a.act === A.FISH) {
      place(HELD.shaft, WOOD, 0.04, -0.10, 0.10);
      place(HELD.tip, STONE, 0.04, -0.78, 0.10);
    } else if (a.act === A.FARM) {
      place(HELD.shaft, WOOD, 0.05, -0.06, 0.06);
      place(HELD.blade, STONE, 0.05, -0.60, 0.10);
    } else if (a.act === A.FORAGE) {
      place(HELD.basket, WOOD, 0.02, -0.06, 0.10);
    } else if (a.act === A.BUILD) {
      place(HELD.load, WOOD, 0.02, -0.05, 0.10);
    }
  }

  addBundle(stage) {
    const hand = this.bones.hand_r || this.bones.hand_l || this.bones.lowerarm_r;
    if (!hand) return;
    const isHand = /^hand/i.test(hand.name);
    const m = new THREE.Mesh(BUNDLE_GEO,
      new THREE.MeshStandardMaterial({ color: stage === 1 ? 0xc8a06a : 0xb98d54,
                                       roughness: .82 }));
    m.position.set(isHand ? 0.03 : 0.02, isHand ? -0.02 : -0.23, isHand ? 0.05 : 0.02);
    m.castShadow = true;
    hand.add(m);
    this.bundle = m;
  }

  skinOpts(a, look) {
    const tone = a.id % 4;           // the same four tones as the instanced crowd
    const map = tone < 2 ? this.T.lightMap : this.T.darkMap;
    const tint = tone % 2 ? 0xd9c3ad : 0xffffff;
    // The base meshes are painted as athletes; real people show far less.
    return { map, color: new THREE.Color(tint), roughness: .72, normalScale: new THREE.Vector2(.35, .35) };
  }

  addHair(a, look) {
    if (a.age < 2) return;
    const names = HAIR[this.sex];
    const pick = names[Math.floor(hash(a.id, 2) * names.length)];
    const add = (name) => {
      const src = lib.hair[name];
      const m = new THREE.Mesh(src.geometry, src.material.clone());
      if (look.grey) { m.material.map = null; m.material.color.set(0xcfccc6); }
      else m.material.color.set(look.hairColor);
      m.matrixAutoUpdate = false;
      m.matrix.copy(this.T.headBindInverse);
      m.castShadow = true; m.frustumCulled = false;
      this.bones.Head.add(m);
    };
    add(pick);
    if (this.sex === 0 && a.age >= 18 && hash(a.id, 9) < .45) add('beard');
  }

  dress(kind, look) {
    const key = kind === 'swim' ? (this.sex ? 'swimF' : 'swimM') : kind;
    const geo = this.T.garments[key];
    const mat = tissueMaterial(new THREE.MeshStandardMaterial({ roughness: .9 }), { color: new THREE.Color(look.cloth) });
    mat.userData.tissue.uLift.value = kind === 'fur' ? .012 : .005;
    const m = new THREE.SkinnedMesh(geo, mat);
    m.bind(this.body.skeleton, this.body.bindMatrix);
    m.castShadow = true; m.frustumCulled = false;
    this.body.parent.add(m);
    this.materials.push(mat);
  }

  // Age shapes the skeleton (head to height, leg length); body mass and
  // strength shape the tissue. All from the record's own fields.
  shape(a) {
    const i = band(a.age);
    const head = 7.6 / HEADS[i];
    const legs = LEG_FRAC[i] / .52;
    this.bones.Head.scale.setScalar(head);
    for (const s of ['l', 'r']) this.bones['thigh_' + s].scale.setScalar(legs);
    const bmi = a.bmi || 22, sn = a.sn == null ? 5 : a.sn;
    const fat = bmi >= 22 ? Math.min(.06, (bmi - 22) * .0055) : Math.max(-.016, (bmi - 22) * .0028);
    const muscle = -.010 + .0016 * sn;          // the base meshes are athletic
    this.materials.forEach((m) => {
      m.userData.tissue.uFat.value = fat;
      m.userData.tissue.uMuscle.value = muscle;
    });
    this.heightFactor = (1 + (head - 1) / HEADS[i]) * (legs * .52 + .48);
  }

  play(name, timeScale) {
    const clip = lib.clips[name];
    if (!clip) return;
    let act = this.actions[name];
    if (!act) act = this.actions[name] = this.mixer.clipAction(clip);
    act.timeScale = timeScale;
    if (this.clip === name) return;
    const prev = this.clip && this.actions[this.clip];
    act.reset();
    act.play();
    if (prev) act.crossFadeFrom(prev, .35, false);
    this.clip = name;
  }

  pose(a, H, dt) {
    const s = H / (this.T.height * this.heightFactor);
    this.root.scale.setScalar(s);
    const lying = LYING.has(a.act) || a.age < 1;
    // Sleep is on one side, hips and knees drawn up, breathing slowly (CURL).
    // Never a death clip: a sleeper is not a corpse.
    this.root.rotation.set(0, a.yaw || 0, lying ? (hash(a.id, 5) < .5 ? 1 : -1) * Math.PI / 2 : 0, 'YXZ');
    this.lying = lying;
    this.sitting = !lying && !a.moving && !!SIT[a.act];
    if (lying) this.play('Idle_Loop', .3);
    else if (this.sitting) this.play(SIT[a.act], a.act === A.WITHDRAW ? .5 : 1);
    else if (a.moving) {
      const v = (a.speed || 0) / s;
      const [name, base] = GAIT.find(([, , top]) => v < top);
      this.play(name, Math.max(.55, Math.min(1.7, v / base)));
    } else this.play(STILL_CLIP[a.act] || 'Idle_Loop', 1);
    this.mixer.update(dt);
    if (this.sitting) STRAIGHT.forEach((n) => this.bones[n].quaternion.copy(this.rest[n]));
    if (this.lying) {
      this.root.updateMatrixWorld(true);
      CURL.forEach(([name, deg]) => this.bend(name, deg * Math.PI / 180));
    }
  }

  // Turn a bone about the body's own left-right axis (flexion is negative).
  bend(name, angle) {
    const b = this.bones[name];
    b.parent.updateWorldMatrix(true, false);
    this.root.getWorldQuaternion(_q1);
    _ax.set(1, 0, 0).applyQuaternion(_q1);
    b.parent.getWorldQuaternion(_q2);
    _q3.setFromAxisAngle(_ax, angle);
    b.quaternion.premultiply(_q2.clone().invert().multiply(_q3).multiply(_q2));
    b.updateWorldMatrix(false, true);
  }

  // Plant the body on the ground: the lowest contact bone touches the surface.
  ground(groundY, parent) {
    this.root.updateMatrixWorld(true);
    const lying = this.lying;
    const contacts = lying ? LYING_CONTACTS : this.sitting ? SIT_CONTACTS : ['ball_l', 'ball_r', 'foot_l', 'foot_r'];
    const rest = lying ? .09 : this.sitting ? .07 : .035;
    let low = Infinity;
    for (const name of contacts) {
      const b = this.bones[name];
      if (!b) continue;
      _p.setFromMatrixPosition(b.matrixWorld);
      parent.worldToLocal(_p);
      low = Math.min(low, _p.y - (name.startsWith('foot') ? .05 * this.root.scale.x : 0));
    }
    const want = groundY + rest * this.root.scale.x - (low - this.root.position.y);
    this.lift = this.lift == null ? want : this.lift + (want - this.lift) * .35;
    this.root.position.y = this.lift;
  }

  dispose() {
    this.mixer.stopAllAction();
    this.root.removeFromParent();
    this.materials.forEach((m) => m.dispose());
  }
}
const _p = new THREE.Vector3(), _c = new THREE.Vector3(), _w = new THREE.Vector3(), _ax = new THREE.Vector3();
// A gift party's bundle, bound, about a head and a half wide.
const BUNDLE_GEO = new THREE.BoxGeometry(0.20, 0.15, 0.14);
// What the hands hold, by the record's activity: the shaft for a spear or a
// rod, the blade of a hoe, a basket, a load (the 2D rig's own mapping,
// carried onto the near bodies).
const HELD = {
  shaft: new THREE.BoxGeometry(0.028, 0.95, 0.028),
  tip: new THREE.BoxGeometry(0.055, 0.16, 0.028),
  blade: new THREE.BoxGeometry(0.20, 0.14, 0.03),
  basket: new THREE.BoxGeometry(0.19, 0.13, 0.17),
  load: new THREE.BoxGeometry(0.20, 0.16, 0.24),
};
const WOOD = new THREE.MeshStandardMaterial({ color: 0x6b4a2e, roughness: .85 });
const STONE = new THREE.MeshStandardMaterial({ color: 0xa49c8c, roughness: .9 });
const _q1 = new THREE.Quaternion(), _q2 = new THREE.Quaternion(), _q3 = new THREE.Quaternion();

// One figure outside any crowd, for the figure study page.
export function makeFigure(a, look) { return lib ? new Figure(a, look) : null; }

// The near layer of one crowd: which actors get a skinned body this moment.
export class HumanLayer {
  constructor(group, lookOf) {
    this.group = group;          // the crowd's group (world-local space)
    this.lookOf = lookOf;        // actor -> {dress, cloth, hairColor, grey}
    this.figures = new Map();
    this.nextPick = 0;
  }

  // Nearest by apparent size, within a budget; hysteresis keeps a figure
  // that is just past the threshold, so bodies do not pop at the edge.
  pick(actors, camera, budget, now, worldOf) {
    if (!lib || now < this.nextPick) return;
    this.nextPick = now + 400;
    camera.getWorldPosition(_c);
    const scale = this.group.getWorldScale(_w).x;
    const ranked = [];
    actors.forEach((a) => {
      const local = worldOf(a);
      this.group.localToWorld(_p.copy(local));
      const d = Math.max(.05, _p.distanceTo(_c));
      const size = 1.7 * scale / d;                 // radians subtended by a body
      const keep = this.figures.has(a.id) ? .7 : 1;
      if (size > .045 * keep) ranked.push([size, a]);
    });
    ranked.sort((x, y) => y[0] - x[0]);
    const want = new Set(ranked.slice(0, budget).map(([, a]) => a.id));
    for (const [id, f] of this.figures) if (!want.has(id) || f.sex !== (actors.get(id).sex === 1 ? 1 : 0)) {
      f.dispose(); this.figures.delete(id);
    }
    ranked.slice(0, budget).forEach(([, a]) => {
      if (this.figures.has(a.id)) return;
      const f = new Figure(a, this.lookOf(a));
      this.group.add(f.root);
      this.figures.set(a.id, f);
    });
  }

  has(id) { return this.figures.has(id); }

  draw(a, root, H, dt) {
    const f = this.figures.get(a.id);
    f.root.position.set(root.x, root.y, root.z);
    f.pose(a, H, dt);
    f.ground(root.y, this.group);
  }

  prune(actors) {
    for (const [id, f] of this.figures) if (!actors.has(id)) { f.dispose(); this.figures.delete(id); }
  }
}
