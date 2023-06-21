import module from 'node:module';

const { port1, port2 } = new MessageChannel();

module.register('./poc.loader.mjs', {
  parentURL: import.meta.url,
  data: {
    entryPoint: process.argv[1],
    port: port2
  },
  transferList: [port2],
});

port1.once('message', (message) => {
  console.log(message);
});
