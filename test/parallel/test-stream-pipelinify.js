'use strict';

const common = require('../common');
const {
  Readable,
  Transform,
  Writable,
  pipelinify
} = require('stream');
const assert = require('assert');

{
  let res = '';
  pipelinify(
    new Transform({
      transform: common.mustCall((chunk, encoding, callback) => {
        callback(null, chunk + chunk);
      })
    }),
    new Transform({
      transform: common.mustCall((chunk, encoding, callback) => {
        callback(null, chunk.toString().toUpperCase());
      })
    })
  )
  .end('asd')
  .on('data', common.mustCall((buf) => {
    res += buf;
  }))
  .on('end', common.mustCall(() => {
    assert.strictEqual(res, 'ASDASD');
  }));
}

{
  let res = '';
  pipelinify(
    Readable.from(['asd']),
    new Transform({
      transform: common.mustCall((chunk, encoding, callback) => {
        callback(null, chunk.toString().toUpperCase());
      })
    })
  )
  .on('data', common.mustCall((buf) => {
    res += buf;
  }))
  .on('end', common.mustCall(() => {
    assert.strictEqual(res, 'ASD');
  }));
}

{
  let res = '';
  pipelinify(
    async function* () {
      yield 'asd';
    },
    new Transform({
      transform: common.mustCall((chunk, encoding, callback) => {
        callback(null, chunk.toString().toUpperCase());
      })
    })
  )
  .on('data', common.mustCall((buf) => {
    res += buf;
  }))
  .on('end', common.mustCall(() => {
    assert.strictEqual(res, 'ASD');
  }));
}

{
  let res = '';
  pipelinify(
    new Transform({
      transform: common.mustCall((chunk, encoding, callback) => {
        callback(null, chunk.toString().toUpperCase());
      })
    }),
    async function*(source) {
      for await (const chunk of source) {
        yield chunk;
      }
    },
    new Writable({
      write: common.mustCall((chunk, encoding, callback) => {
        res += chunk;
        callback(null);
      })
    })
  )
  .end('asd')
  .on('finish', common.mustCall(() => {
    assert.strictEqual(res, 'ASD');
  }));
}

{
  let res = '';
  pipelinify(
    new Transform({
      transform: common.mustCall((chunk, encoding, callback) => {
        callback(null, chunk.toString().toUpperCase());
      })
    }),
    async function*(source) {
      for await (const chunk of source) {
        yield chunk;
      }
    },
    async function(source) {
      for await (const chunk of source) {
        res += chunk;
      }
    }
  )
  .end('asd')
  .on('finish', common.mustCall(() => {
    assert.strictEqual(res, 'ASD');
  }));
}

{
  let res;
  pipelinify(
    new Transform({
      objectMode: true,
      transform: common.mustCall((chunk, encoding, callback) => {
        callback(null, { chunk });
      })
    }),
    async function*(source) {
      for await (const chunk of source) {
        yield chunk;
      }
    },
    new Transform({
      objectMode: true,
      transform: common.mustCall((chunk, encoding, callback) => {
        callback(null, { chunk });
      })
    })
  )
  .end(true)
  .on('data', common.mustCall((buf) => {
    res = buf;
  }))
  .on('end', common.mustCall(() => {
    assert.strictEqual(res.chunk.chunk, true);
  }));
}

{
  const _err = new Error('asd');
  pipelinify(
    new Transform({
      objectMode: true,
      transform: common.mustCall((chunk, encoding, callback) => {
        callback(_err);
      })
    }),
    async function*(source) {
      for await (const chunk of source) {
        yield chunk;
      }
    },
    new Transform({
      objectMode: true,
      transform: common.mustNotCall((chunk, encoding, callback) => {
        callback(null, { chunk });
      })
    })
  )
  .end(true)
  .on('data', common.mustNotCall())
  .on('end', common.mustNotCall())
  .on('error', (err) => {
    assert.strictEqual(err, _err);
  });
}

{
  const _err = new Error('asd');
  pipelinify(
    new Transform({
      objectMode: true,
      transform: common.mustCall((chunk, encoding, callback) => {
        callback(null, chunk);
      })
    }),
    async function*(source) {
      let tmp = '';
      for await (const chunk of source) {
        tmp += chunk;
        throw _err;
      }
      return tmp;
    },
    new Transform({
      objectMode: true,
      transform: common.mustNotCall((chunk, encoding, callback) => {
        callback(null, { chunk });
      })
    })
  )
  .end(true)
  .on('data', common.mustNotCall())
  .on('end', common.mustNotCall())
  .on('error', (err) => {
    assert.strictEqual(err, _err);
  });
}
