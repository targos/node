import { register } from 'node:module';

register('./loader-resolve-passthru.mjs', { parentURL: import.meta.url });
