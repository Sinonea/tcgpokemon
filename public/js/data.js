/* Tout ce que les pages savent de l'arborescence des données : index.html et admin.html l'importent.
 *
 *   data/blocs/blocs.json                       { "blocs": [ { "bloc": "Méga-Évolution" } ] }
 *   data/blocs/<bloc>/sets.json                 { "sets":  [ { "set": "Nuit Noire" } ] }
 *   data/blocs/<bloc>/<set>/booster.json        emplacements du booster (+ taux)
 *   data/blocs/<bloc>/<set>/cartes.json         liste des cartes
 *   assets/images/<bloc>/<set>/<id>.webp        images
 *
 * Les dossiers portent exactement le nom écrit dans blocs.json et sets.json.
 * Pour changer une convention (nom de fichier, dossier d'images…), modifiez uniquement ce fichier.
 */
export const ROOT = 'data/blocs';
export const FICHIERS = { blocs: 'blocs.json', sets: 'sets.json', booster: 'booster.json', cartes: 'cartes.json' };

const seg = s => encodeURIComponent(s);          // accents, espaces, « ᵉ »… : chaque dossier est encodé

export const URLS = {
  blocs:   ()                => `${ROOT}/${FICHIERS.blocs}`,
  sets:    bloc              => `${ROOT}/${seg(bloc)}/${FICHIERS.sets}`,
  booster: (bloc, set)       => `${ROOT}/${seg(bloc)}/${seg(set)}/${FICHIERS.booster}`,
  cartes:  (bloc, set)       => `${ROOT}/${seg(bloc)}/${seg(set)}/${FICHIERS.cartes}`,
  image:   (bloc, set, id)   => `assets/images/${seg(bloc)}/${seg(set)}/${seg(id)}.webp`,
  save:    pseudo            => `api/save/${seg(pseudo)}`,        // GET : progression du joueur (404 si aucune) ; PUT : la remplace
  admin:   'api/admin/saves',                                     // GET avec « Authorization: Bearer <jeton> »
};

export const norm = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();

// Clé d'un set dans la sauvegarde du joueur : « Méga-Évolution/Nuit Noire »
export const cle = (bloc, set) => `${bloc}/${set}`;
export const decle = k => { const i = k.indexOf('/'); return i < 0 ? [null, k] : [k.slice(0, i), k.slice(i + 1)]; };

export async function getJSON(u) {
  const r = await fetch(u);
  if (!r.ok) { const e = new Error('HTTP ' + r.status); e.status = r.status; throw e; }
  return r.json();
}

const horsServeur = () => location.protocol === 'file:'
  ? 'Ouvrez la page depuis le serveur (http), pas en double-clic : le navigateur bloque la lecture des fichiers JSON.' : '';

export async function loadBlocs() {
  const d = await getJSON(URLS.blocs());
  return (d.blocs || []).map(x => String(x.bloc));
}

export async function loadSets(bloc) {
  const d = await getJSON(URLS.sets(bloc));
  return (d.sets || []).map(x => String(x.set));
}

// Charge cartes.json et booster.json d'un set. Ne lève jamais d'exception : l'état est dans error / absent.
export async function loadSet(bloc, set) {
  const s = { bloc, set, sortie: '', cards: [], slots: [], rates: [], byRarity: {}, error: '', absent: false };
  try {
    const [c, b] = await Promise.all([getJSON(URLS.cartes(bloc, set)), getJSON(URLS.booster(bloc, set))]);
    s.sortie = c.sortie || '';
    s.cards = (c.cartes || []).map(x => ({ id: String(x.id), name: String(x.name), rarity: String(x.rarity) }));
    const bo = b.booster || {};
    s.slots = (bo.slots || []).slice().sort((x, y) => (x.position || 0) - (y.position || 0))
      .map(sl => Object.entries(sl.rarities || {}).map(([rarity, p]) => ({ rarity, p: Number(p) })).filter(o => o.p > 0))
      .filter(sl => sl.length);
    s.rates = (bo.rates || []).map(r => ({ rarity: String(r.rarity), cartes: Number(r.cartes), chance: Number(r.chance) }));
    s.cards.forEach(c => (s.byRarity[norm(c.rarity)] ||= []).push(c));
    if (!s.cards.length || !s.slots.length) throw new Error('cartes ou emplacements vides');
    const manque = [...new Set(s.slots.flat().map(o => o.rarity))].filter(r => !s.byRarity[norm(r)]);
    if (manque.length) s.error = `Raretés sans carte dans ${URLS.cartes(bloc, set)} : ${manque.join(', ')}.`;
  } catch (e) {
    s.absent = e.status === 404;
    s.cards = []; s.slots = []; s.rates = []; s.byRarity = {};
    s.error = horsServeur() || `Chargement impossible (${URLS.cartes(bloc, set)}, ${URLS.booster(bloc, set)}) : ${e.message}`;
  }
  return s;
}
