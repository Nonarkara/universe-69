# Humans in the headset viewer — credits

| File | Source | Author | Licence |
|---|---|---|---|
| `male.glb`, `female.glb`, `male_light.jpg`, `female_light.jpg` | Universal Base Characters [Standard] (quaternius.itch.io/universal-base-characters) | Quaternius | CC0 1.0 Universal |
| `hair_*.glb` | Universal Base Characters [Standard], hairstyles | Quaternius | CC0 1.0 Universal |
| `anims.glb` | Universal Animation Library [Standard] (quaternius.itch.io/universal-animation-library) | Quaternius | CC0 1.0 Universal |
| `../addons/GLTFLoader.js`, `SkeletonUtils.js`, `BufferGeometryUtils.js` | three.js r160 `examples/jsm` | three.js authors | MIT |

CC0: <https://creativecommons.org/publicdomain/zero/1.0/>. Both packs were
downloaded on 2026-11-04 as the free Standard tier; each zip's licence file
states CC0 1.0.

`tools/build_humans.py` repacks them: textures downsized to 1024 px JPEG,
OpenGL-convention normal maps, and only the clips the viewer plays. The
garments, soft tissue (fat, muscle, belly), the ground sit and the sleeping
curl are made at runtime in `humans.js` from the same meshes and clips.
