'use strict';

const pipeline = require('internal/streams/pipeline');
const Duplex = require('internal/streams/duplex');
const { destroyer } = require('internal/streams/destroy');

module.exports = function pipe(...streams) {
  let ondrain;
  let onfinish;
  let onreadable;
  let onclose;
  let d;

  const r = pipeline(streams, function(err) {
    if (onclose) {
      onclose(err);
    } else if (err) {
      d.destroy(err);
    }
    onclose = null;
  });
  const w = streams[0];

  // TODO (ronag): Avoid double buffering.
  // Implement Writable/Readable/Duplex traits.
  // See, https://github.com/nodejs/node/pull/33515.
  d = new Duplex({
    writable: w.writable,
    readable: r.readable,
    objectMode: w.readableObjectMode
  });

  if (w.writable) {
    d._write = function(chunk, encoding, callback) {
      if (w.write(chunk, encoding)) {
        callback();
      } else {
        ondrain = callback;
      }
    };

    d._final = function(callback) {
      w.end();
      onfinish = callback;
    };

    w.on('drain', function() {
      if (ondrain) {
        const cb = ondrain;
        ondrain = null;
        cb();
      }
    });

    r.on('finish', function() {
      if (onfinish) {
        const cb = onfinish;
        onfinish = null;
        cb();
      }
    });
  }

  if (r.readable) {
    r.on('readable', function() {
      if (onreadable) {
        const cb = onreadable;
        onreadable = null;
        cb();
      }
    });

    r.on('end', function() {
      d.push(null);
    });

    d._read = function() {
      while (true) {
        const buf = r.read();

        if (buf === null) {
          onreadable = d._read;
          return;
        }

        if (!d.push(buf)) {
          return;
        }
      }
    };
  }

  d._destroy = function(err, callback) {
    onreadable = null;
    ondrain = null;
    onfinish = null;

    if (onclose === null) {
      callback(err);
    } else {
      onclose = callback;
      destroyer(r, err);
    }
  };

  return d;
};
