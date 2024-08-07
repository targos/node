import {DatabaseSync} from 'node:sqlite';

const db = new DatabaseSync(':memory:');

const stmt = db.prepare('SELECT 2 as __proto__');

const result = stmt.all();

console.log(result)
